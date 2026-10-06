import codecs
import re

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with codecs.open(path, 'r', 'utf-8') as f:
    html = f.read()

# Add Supabase Script
if 'unpkg.com/@supabase' not in html:
    html = html.replace('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>', '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n<script src="https://unpkg.com/@supabase/supabase-js@2"></script>')

# Initialize Supabase inside the <script> block
init_code = """
const SUPABASE_URL = 'https://yhrlrzwsoqgryocrurms.supabase.co';
const SUPABASE_KEY = 'sb_publishable_g8-aXuPxQ-1LC_j5bWVrZg_l0ezxAT8';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

async function loadData() {
  try {
    const { data: records, error } = await supabase.from('inspections').select('*').order('created_at', { ascending: false });
    if (records && records.length > 0) {
      data = records.map(r => ({
        db_id: r.id,
        f: r.field_name,
        s: r.status_color,
        d: r.disease_name,
        id: r.disease_id,
        c: r.confidence,
        a: r.age_days,
        g: r.growth_stage,
        t: r.created_at,
        lat: r.latitude,
        lng: r.longitude,
        job_id: r.job_id,
        location_source: r.location_source,
        provider: r.ai_provider
      }));
    }
    render();
  } catch(e) {
    console.error("Lỗi lấy dữ liệu Supabase:", e);
    render();
  }
}
// Load data from DB when app starts
loadData();
"""
if 'SUPABASE_URL' not in html:
    html = html.replace('const CAYLUA_CONFIG = {', init_code + '\nconst CAYLUA_CONFIG = {')

# Modify saveCheck to insert into Supabase
save_db_code = """
    const record={f:'Vị trí mới',s: result.disease.includes('Không') ? 'green' : 'red', d: result.disease, id: result.id || null, c: (result.confidence*100).toFixed(0)+'%', a: document.getElementById('age').value||'—', g: 'Chưa rõ', t: new Date().toISOString(), lat: selectedPos.lat, lng: selectedPos.lng, job_id: result.job_id, location_source: selectedPos.source, provider: result.provider};
    
    // Save to Supabase
    const { data: inserted, error: dbErr } = await supabase.from('inspections').insert({
        field_name: record.f,
        disease_id: record.id,
        disease_name: record.d,
        status_color: record.s,
        confidence: record.c,
        age_days: parseInt(record.a) || null,
        growth_stage: record.g,
        latitude: record.lat,
        longitude: record.lng,
        location_source: record.location_source,
        ai_provider: record.provider,
        job_id: record.job_id
    }).select();
    
    if (inserted && inserted.length > 0) record.db_id = inserted[0].id;
    
    data.unshift(record);
    render();
"""
# Find the record creation line and replace it
html = re.sub(r'const record=\{f:.*?data\.unshift\(record\);\n\s*render\(\);', save_db_code, html, flags=re.DOTALL)

# Modify delete logic to delete from DB
del_code = """if(confirm('Bạn có chắc chắn muốn xóa nhật ký này?')){
          data = data.filter(d => d !== x);
          render();
          if (x.db_id) supabase.from('inspections').delete().eq('id', x.db_id).then();
        }"""
html = html.replace("if(confirm('Bạn có chắc chắn muốn xóa nhật ký này?')){\n          data = data.filter(d => d !== x);\n          render();\n        }", del_code)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(html)
