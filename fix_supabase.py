import io
import re

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with io.open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the top initialization
top_init_pattern = r'const SUPABASE_URL.*?\/\/ Load data from DB when app starts\s*loadData\(\);\s*'
match = re.search(top_init_pattern, html, re.DOTALL)
if match:
    html = html.replace(match.group(0), '')
    
    # Append it to the bottom, right before </script>
    safe_init = """
try {
  const SUPABASE_URL = 'https://yhrlrzwsoqgryocrurms.supabase.co';
  const SUPABASE_KEY = 'sb_publishable_g8-aXuPxQ-1LC_j5bWVrZg_l0ezxAT8';
  window.supabaseClient = window.supabase ? window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY) : null;

  async function loadData() {
    if (!window.supabaseClient) return;
    try {
      const { data: records, error } = await window.supabaseClient.from('inspections').select('*').order('created_at', { ascending: false });
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
      console.error('Supabase fetch error:', e);
    }
  }
  loadData();
} catch (err) {
  console.error('Supabase init error:', err);
}
"""
    html = html.replace('</script>\n<div class="font-control"', safe_init + '\n</script>\n<div class="font-control"')
    
    # Also fix saveCheck and delete to use window.supabaseClient safely
    html = html.replace('await supabase.from', 'if(window.supabaseClient) await window.supabaseClient.from')
    html = html.replace('supabase.from', 'if(window.supabaseClient) window.supabaseClient.from')
    
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Fixed gracefully!')
else:
    print('Pattern not found!')
