// v3_services.js
// Các Services theo chuẩn MASTER COMMAND

class Config {
    static SUPABASE_URL = localStorage.getItem('SUPABASE_URL') || '';
    static SUPABASE_ANON_KEY = localStorage.getItem('SUPABASE_ANON_KEY') || '';
    static AI_SERVER_URL = localStorage.getItem('AI_SERVER_URL') || 'https://ai.nongnghiepsangtao.io.vn';
    
    static setConfig(url, key, ai_url) {
        localStorage.setItem('SUPABASE_URL', url);
        localStorage.setItem('SUPABASE_ANON_KEY', key);
        localStorage.setItem('AI_SERVER_URL', ai_url);
        this.SUPABASE_URL = url;
        this.SUPABASE_ANON_KEY = key;
        this.AI_SERVER_URL = ai_url;
        location.reload();
    }
}

// 1. SUPABASE SERVICE
class SupabaseService {
    static client = null;
    static init() {
        if(Config.SUPABASE_URL && Config.SUPABASE_ANON_KEY) {
            this.client = supabase.createClient(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY);
        } else {
            this.client = window.supabaseClient; // fallback if defined elsewhere
        }
    }
    
    static async getSession() {
        const { data, error } = await this.client.auth.getSession();
        return data.session;
    }

    static async createSurveySession(field_id) {
        const user = (await this.client.auth.getUser()).data.user;
        const { data, error } = await this.client.from('survey_sessions').insert({
            user_id: user.id,
            field_id: field_id,
            status: 'active'
        }).select().single();
        if(error) throw error;
        return data;
    }

    static async createSurveyPoint(session_id, field_id, lat, lng, acc) {
        const user = (await this.client.auth.getUser()).data.user;
        const { data, error } = await this.client.from('survey_points').insert({
            survey_session_id: session_id,
            field_id: field_id,
            user_id: user.id,
            latitude: lat,
            longitude: lng,
            accuracy: acc,
            status: 'pending'
        }).select().single();
        if(error) throw error;
        return data;
    }

    static async createSurveyImage(session_id, point_id, file, path) {
        const user = (await this.client.auth.getUser()).data.user;
        const { data, error } = await this.client.from('survey_images').insert({
            user_id: user.id,
            survey_session_id: session_id,
            survey_point_id: point_id,
            file_name: file.name,
            mime_type: file.type,
            size: file.size,
            storage_path: path,
            status: 'uploading'
        }).select().single();
        if(error) throw error;
        return data;
    }
    
    static async updateImageStatus(id, status) {
        const { error } = await this.client.from('survey_images').update({ status }).eq('id', id);
        if(error) throw error;
    }
}

// 2. STORAGE SERVICE
class StorageService {
    static async uploadOriginal(file, user_id, session_id, point_id) {
        const ext = file.name.split('.').pop();
        const path = `${user_id}/${session_id}/${point_id}/original.${ext}`;
        const { data, error } = await SupabaseService.client.storage.from('survey-images').upload(path, file, {
            cacheControl: '3600',
            upsert: true
        });
        if(error) throw error;
        return path;
    }
    
    static async getSignedUrl(path) {
        const { data, error } = await SupabaseService.client.storage.from('survey-images').createSignedUrl(path, 3600);
        if(error) throw error;
        return data.signedUrl;
    }
}

// 3. AI SERVICE
class AIService {
    static async submitImage(point_id, image_id, signed_url) {
        const reqData = {
            survey_point_id: point_id,
            survey_image_id: image_id,
            image_url: signed_url
        };
        const res = await fetch(`${Config.AI_SERVER_URL}/api/ai/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqData)
        });
        if(!res.ok) throw new Error('AI Server error');
        return await res.json();
    }
}

// 4. REALTIME SERVICE
class RealtimeService {
    static channel = null;
    static subscribeAI(callback) {
        this.channel = SupabaseService.client.channel('public:ai_results')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'ai_results' }, payload => {
                callback(payload);
            })
            .subscribe();
    }
}

// 5. GPS SERVICE
class GPSService {
    static watchId = null;
    static currentPos = null;
    static start(callback) {
        if('geolocation' in navigator) {
            this.watchId = navigator.geolocation.watchPosition(
                pos => {
                    this.currentPos = pos;
                    callback(pos);
                },
                err => console.warn(err),
                { enableHighAccuracy: true }
            );
        }
    }
}

// 6. SYNC SERVICE (IndexedDB -> Supabase)
const db = new Dexie('CayLuaV3DB');
db.version(1).stores({
    sync_queue: '++id, entity, entity_id, operation, status, payload, file_data'
});

class SyncService {
    static async addQueue(entity, entity_id, operation, payload, file_data = null) {
        await db.sync_queue.add({
            entity, entity_id, operation, payload, file_data, status: 'pending'
        });
        this.processQueue();
    }

    static async processQueue() {
        if(!navigator.onLine) return;
        const pending = await db.sync_queue.where('status').equals('pending').toArray();
        for(let job of pending) {
            try {
                if(job.entity === 'survey_image' && job.operation === 'upload') {
                    // Create Point in DB if not exist (Upsert not easy without RPC, so we check or just insert)
                    // Wait, insert with specific ID requires passing ID.
                    const user = (await SupabaseService.client.auth.getUser()).data.user;
                    if(user) {
                        // Check if point exists
                        const { data: ptCheck } = await SupabaseService.client.from('survey_points').select('id').eq('id', job.payload.point_id).single();
                        if(!ptCheck) {
                            await SupabaseService.client.from('survey_points').insert({
                                id: job.payload.point_id,
                                survey_session_id: job.payload.session_id,
                                field_id: job.payload.field_id || '00000000-0000-0000-0000-000000000000',
                                user_id: user.id,
                                latitude: job.payload.lat,
                                longitude: job.payload.lng,
                                accuracy: 10,
                                status: 'pending'
                            });
                        }
                        
                        // Create Image record
                        const path = `${user.id}/${job.payload.session_id}/${job.payload.point_id}/original.${job.payload.file_name.split('.').pop()}`;
                        const { data: imgCheck } = await SupabaseService.client.from('survey_images').select('id').eq('id', job.entity_id).single();
                        if(!imgCheck) {
                            await SupabaseService.client.from('survey_images').insert({
                                id: job.entity_id,
                                user_id: user.id,
                                survey_session_id: job.payload.session_id,
                                survey_point_id: job.payload.point_id,
                                file_name: job.payload.file_name,
                                mime_type: job.payload.mime_type,
                                size: job.payload.size,
                                storage_path: path,
                                status: 'uploading'
                            });
                        }
                        
                        // Upload to Storage
                        const file = new File([job.file_data], job.payload.file_name, {type: job.payload.mime_type});
                        await StorageService.uploadOriginal(file, user.id, job.payload.session_id, job.payload.point_id);
                        
                        // Update DB record
                        await SupabaseService.updateImageStatus(job.entity_id, 'uploaded');
                        
                        // Trigger AI
                        const signedUrl = await StorageService.getSignedUrl(path);
                        await SupabaseService.updateImageStatus(job.entity_id, 'ai_pending');
                        try {
                            await AIService.submitImage(job.payload.point_id, job.entity_id, signedUrl);
                        } catch(ai_err) {
                            console.warn("AI trigger failed, mark as ai_failed", ai_err);
                            await SupabaseService.updateImageStatus(job.entity_id, 'ai_failed');
                        }
                    }
                }
                await db.sync_queue.delete(job.id);
            } catch(e) {
                console.error("Sync error:", e);
                // Can increment retry count
            }
        }
    }
}

window.addEventListener('online', () => SyncService.processQueue());

// Boot
SupabaseService.init();
