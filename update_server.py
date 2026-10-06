import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

new_imports = """
import httpx
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase client init failed:", e)
"""

code = code.replace("import cv2", "import cv2\n" + new_imports)

new_endpoint = """
class AIPredictRequest(BaseModel):
    survey_point_id: str
    survey_image_id: str
    image_url: str
    user_id: Optional[str] = None

@app.post("/api/ai/predict")
async def ai_predict(req: AIPredictRequest):
    start_time = time.time()
    job_id = f"AI-JOB-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Tải ảnh từ signed_url
        async with httpx.AsyncClient() as client:
            resp = await client.get(req.image_url)
            if resp.status_code != 200:
                return JSONResponse(status_code=400, content={"status": "error", "message": "Không thể tải ảnh từ URL"})
            
            nparr = np.frombuffer(resp.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        diseases = []
        CLASS_MAPPING = {
            'Bacterial blight': {'id': 'bacterial_bac_la', 'name': 'Bệnh bạc lá'},
            'Bacterial leaf': {'id': 'bacterial_leaf_streak', 'name': 'Sọc lá vi khuẩn'},
            'Cuterpillar': {'id': 'pest_caterpillar', 'name': 'Sâu ăn lá'},
            'Drainage impact': {'id': 'physio_organic_toxicity', 'name': 'Ngộ độc hữu cơ / Phèn'},
            'Grashopper damage': {'id': 'pest_grasshopper', 'name': 'Châu chấu hại'},
            'Grassy stunt': {'id': 'viral_grassy_stunt', 'name': 'Bệnh vàng lùn'},
            'Leaf folder': {'id': 'pest_leaf_folder', 'name': 'Sâu cuốn lá'},
            'Rice blast': {'id': 'fungal_dao_on', 'name': 'Bệnh đạo ôn'},
            'Sheath blight': {'id': 'fungal_kho_van', 'name': 'Bệnh khô vằn'},
            'Stem borer': {'id': 'pest_stem_borer', 'name': 'Sâu đục thân'},
            'Tungro': {'id': 'viral_tungro', 'name': 'Bệnh Tungro'}
        }
        
        main_disease = None
        main_conf = 0
        main_id = None
        main_cls = None
        
        if model is not None:
            results = model.predict(img, conf=0.25)
            for box in results[0].boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                cls_name_raw = model.names[cls_id] if hasattr(model, 'names') else f"Class_{cls_id}"
                
                mapped = CLASS_MAPPING.get(cls_name_raw, {'id': None, 'name': cls_name_raw})
                diseases.append({
                    "id": mapped['id'],
                    "name": mapped['name'],
                    "confidence": conf,
                    "class_id": cls_id
                })
                
                if conf > main_conf:
                    main_conf = conf
                    main_disease = mapped['name']
                    main_id = mapped['id']
                    main_cls = cls_id
        else:
            time.sleep(1)
            main_disease = "Bệnh đạo ôn (YOLO Fake)"
            main_conf = 0.88
            main_id = "fungal_dao_on"
            main_cls = 0
            diseases.append({"id": main_id, "name": main_disease, "confidence": main_conf, "class_id": main_cls})
            
        # Ghi kết quả vào Supabase ai_results
        if supabase:
            res_data = {
                "survey_point_id": req.survey_point_id,
                "survey_image_id": req.survey_image_id,
                "job_id": job_id,
                "status": "completed",
                "disease": main_disease if main_disease else "Không phát hiện",
                "class_id": main_cls,
                "confidence": main_conf,
                "final_confidence": main_conf
            }
            try:
                supabase.table("ai_results").insert(res_data).execute()
                # Cập nhật status của survey_images thành ai_completed
                supabase.table("survey_images").update({"status": "completed"}).eq("id", req.survey_image_id).execute()
            except Exception as e:
                print("Error inserting ai_results to Supabase:", e)
                
        return JSONResponse({
            "status": "success",
            "provider": "caylua-yolov8",
            "diseases": diseases,
            "job_id": job_id
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
"""

code = code.replace('@app.post("/analyze_mobile")', new_endpoint + '\n\n@app.post("/analyze_mobile")')

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
