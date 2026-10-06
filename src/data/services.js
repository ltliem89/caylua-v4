// CAY LUA V4 DATA ACCESS LAYER
// Consolidates all Supabase interactions into typed services

window.SupabaseClient = window.supabase ? window.supabase.createClient(CAYLUA_CONFIG.supabaseUrl, CAYLUA_CONFIG.supabaseKey) : null;

window.AuthService = {
    async getUser() {
        if (!SupabaseClient) return null;
        const { data, error } = await SupabaseClient.auth.getUser();
        if (error || !data.user) return null;
        return data.user;
    }
};

window.FieldService = {
    async getFields() {
        if (!SupabaseClient) return [];
        const { data } = await SupabaseClient.from('fields').select('*');
        return data || [];
    },
    async createField(field) {
        const { data } = await SupabaseClient.from('fields').insert(field).select().single();
        return data;
    }
};

window.ImageService = {
    async uploadImage(file, path) {
        if (!SupabaseClient) return null;
        const { data, error } = await SupabaseClient.storage.from('survey-images').upload(path, file, { upsert: true });
        if (error) throw error;
        return data.path;
    },
    async getPublicUrl(path) {
        if (!SupabaseClient) return null;
        const { data } = SupabaseClient.storage.from('survey-images').getPublicUrl(path);
        return data.publicUrl;
    },
    async createImageRecord(record) {
        if (!SupabaseClient) return null;
        const { data, error } = await SupabaseClient.from('images').insert(record).select().single();
        if (error) throw error;
        return data;
    },
    async updateImage(id, updates) {
        await SupabaseClient.from('images').update(updates).eq('id', id);
    }
};

window.AiJobService = {
    async createJob(record) {
        if (!SupabaseClient) return null;
        const { data, error } = await SupabaseClient.from('ai_jobs').insert(record).select().single();
        if (error) throw error;
        return data;
    },
    async updateJob(id, updates) {
        if (!SupabaseClient) return;
        await SupabaseClient.from('ai_jobs').update(updates).eq('id', id);
    }
};

window.DetectionService = {
    async saveAnalysis(record) {
        if (!SupabaseClient) return null;
        const { data } = await SupabaseClient.from('ai_analysis').insert(record).select().single();
        return data;
    },
    async saveDetections(records) {
        if (!SupabaseClient || !records.length) return [];
        const { data } = await SupabaseClient.from('disease_detections').insert(records).select();
        return data;
    }
};

window.InspectionService = {
    async createInspection(record) {
        if (!SupabaseClient) return null;
        const { data, error } = await SupabaseClient.from('inspections').insert(record).select().single();
        if (error) throw error;
        return data;
    },
    async getInspections(bounds) {
        if (!SupabaseClient) return [];
        let q = SupabaseClient.from('inspections').select('*, images(*), ai_jobs(*), alerts(*)');
        if (bounds) {
            // Rough bounding box if needed (not strictly PostGIS here yet)
            q = q.gte('latitude', bounds.south).lte('latitude', bounds.north)
                 .gte('longitude', bounds.west).lte('longitude', bounds.east);
        }
        const { data } = await q;
        return data || [];
    }
};

window.AlertService = {
    async createAlert(record) {
        if (!SupabaseClient) return null;
        const { data } = await SupabaseClient.from('alerts').insert(record).select().single();
        return data;
    },
    async getAlerts() {
        if (!SupabaseClient) return [];
        const { data } = await SupabaseClient.from('alerts').select('*').order('created_at', { ascending: false });
        return data || [];
    }
};

window.InsightService = {
    async createInsight(record) {
        if (!SupabaseClient) return null;
        const { data } = await SupabaseClient.from('insights').insert(record).select().single();
        return data;
    },
    generateInsight(inspection, analysis, field) {
        // Core Logic for Intelligent Response Engine
        if (!analysis || !analysis.summary) return null;
        return {
            insight_type: 'disease_warning',
            title: `Cảnh báo ${analysis.summary}`,
            message: `Phát hiện ${analysis.summary} với độ tin cậy ${Math.round(analysis.overall_confidence*100)}%. ` +
                     `Tuổi lúa: ${inspection.crop_age_days || 'Chưa rõ'} ngày. \n` +
                     `Khuyến nghị: Theo dõi diễn biến và đối chiếu triệu chứng thực tế.`,
            severity: analysis.overall_confidence > 0.8 ? 'high' : 'medium',
            source: 'AI_YOLO',
            confidence: analysis.overall_confidence
        };
    }
};

window.ReminderService = {
    async createReminder(record) {
        if (!SupabaseClient) return null;
        await SupabaseClient.from('reminders').insert(record);
    }
};

window.V4SyncService = {
    async processQueue() {
        console.log("V4 Sync Service: processing offline queue...");
        // Placeholder for advanced offline sync logic. Currently relying on Dexie implementation from v3_services.js
        if(window.SyncService) {
            await window.SyncService.processQueue(); 
        }
    }
};
