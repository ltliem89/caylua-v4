import io
import re

with io.open('C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("CSS Leaflet:", bool(re.search(r'leaflet\.css', html)))
print("JS Leaflet:", bool(re.search(r'leaflet\.js', html)))
print("Supabase URL:", bool(re.search(r'yhrlrzwsoqgryocrurms\.supabase\.co', html)))
print("JS Error Potential (Supabase):", bool(re.search(r'window\.supabase\.createClient', html)))

# Truncate and print the first 2000 chars of the script block
script_start = html.find('<script>')
if script_start != -1:
    print("\n--- Start of script block ---")
    print(html[script_start:script_start+1500])
