import io
import re

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with io.open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# We need to rewrite the saveCheck and syncQueue inside the HTML to handle file blobs.
# Let's extract the JS block and replace it using regex.

replacement = """
        // Sync Queue with FILE
        await db.sync_queue.add({
            table: 'inspections',
            operation: 'INSERT',
            payload: record,
            file: file, // Store the raw Blob locally
            created_at: new Date().toISOString(),
            retry_count: 0
        });
"""
html = html.replace("""
        // Sync Queue
        await db.sync_queue.add({
            table: 'inspections',
            operation: 'INSERT',
            payload: record,
            created_at: new Date().toISOString(),
            retry_count: 0
        });""", replacement)

sync_logic = """
            if(job.operation === 'INSERT' && window.supabaseClient) {
                // 1. Upload File to Supabase Storage if exists
                let image_path = null;
                if(job.file) {
                    const ext = job.file.name ? job.file.name.split('.').pop() : 'jpg';
                    image_path = 'public/' + job.payload.id + '.' + ext;
                    
                    const { error: uploadError } = await window.supabaseClient.storage
                        .from('rice-images')
                        .upload(image_path, job.file, { upsert: true });
                        
                    if(uploadError) {
                        console.warn('Storage upload error:', uploadError);
                        // We will proceed to save metadata even if image fails, or you can throw.
                    } else {
                        job.payload.image_path = image_path;
                    }
                }
                
                // 2. Insert Metadata
                const {error} = await window.supabaseClient.from(job.table).insert(job.payload);
                if(!error) {
                    await db.sync_queue.delete(job.id);
                    await db.inspections.update(job.payload.id, {sync_status: 'synced', image_path: image_path});
                }
            }
"""

html = html.replace("""
            if(job.operation === 'INSERT' && window.supabaseClient) {
                const {error} = await window.supabaseClient.from(job.table).insert(job.payload);
                if(!error) {
                    await db.sync_queue.delete(job.id);
                    await db.inspections.update(job.payload.id, {sync_status: 'synced'});
                }
            }""", sync_logic)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Storage sync injected!')
