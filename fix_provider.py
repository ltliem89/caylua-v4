import codecs
import re

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with codecs.open(path, 'r', 'utf-8') as f:
    html = f.read()

new_analyze = """    async analyze(file, context) {
        const fd = new FormData();
        fd.append('file', file, file.name);
        fd.append('latitude', String(context.latitude));
        fd.append('longitude', String(context.longitude));
        fd.append('location_source', context.location_source);
        let res = await fetch(CAYLUA_CONFIG.server.baseUrl + CAYLUA_CONFIG.server.analyzePath, { method: 'POST', body: fd, signal: AbortSignal.timeout(CAYLUA_CONFIG.server.timeoutMs) });
        if(!res.ok) throw new Error('Server error');
        let data = await res.json();
        const disease = (data.diseases && data.diseases.length) ? data.diseases.map(x=>x.name||x.label||x).join(', ') : 'Không phát hiện';
        const disease_id = (data.diseases && data.diseases.length) ? data.diseases[0].id : null;
        const confidence = (data.diseases && data.diseases.length) ? data.diseases[0].confidence : 0.9;
        return { status: "success", provider: "caylua-yolov8", disease: disease, id: disease_id, confidence: confidence, job_id: data.job_id };
    }"""

html = re.sub(r'    async analyze\(file, context\) \{.*?    \}', new_analyze, html, count=1, flags=re.DOTALL)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(html)
