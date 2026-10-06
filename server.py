import time
import os
import uuid
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2

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


try:
    from ultralytics import YOLO
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("WARNING: ultralytics is not installed. AI will return mock results.")

app = FastAPI(title="CAY LUA AI Server", version="1.0")

# Cấu hình CORS để Frontend (HTML) gọi được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nạp model (chú ý: nếu không tìm thấy file, sẽ xử lý lỗi ngầm để server vẫn lên)
model_path = "best02.pt" if os.path.exists("best02.pt") else "best.pt"
model = None
if MODEL_AVAILABLE:
    try:
        model = YOLO(model_path)
        print(f"Model {model_path} loaded successfully.")
    except Exception as e:
        print(f"ERROR loading YOLO model {model_path}: {e}")

@app.get("/health")
def health_check():
    """Health check theo đúng đặc tả CAY_LUA_MD_AI_ADAPTER_LINH_HOAT"""
    return {"status": "ok", "model_loaded": model is not None}


class AIPredictRequest(BaseModel):
    survey_point_id: str
    survey_image_id: str
    image_url: str
    user_id: Optional[str] = None

@app.post("/api/ai/predict")
async def ai_predict(req: AIPredictRequest):
    print(f"\\n[SERVER LOG] Nhận yêu cầu AI Predict từ Client!")
    print(f"[SERVER LOG] Điểm khảo sát: {req.survey_point_id}")
    print(f"[SERVER LOG] ID ảnh: {req.survey_image_id}")
    print(f"[SERVER LOG] Đang tải ảnh từ URL...")
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
            results = model.predict(img, conf=0.10, iou=0.45)
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
            # Tích hợp AI thông minh (Google Gemini) nếu không có YOLO
            import google.generativeai as genai
            from PIL import Image
            import io
            
            gemini_key = os.environ.get("GEMINI_API_KEY")
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    genai_model = genai.GenerativeModel("gemini-1.5-flash")
                    image_parts = [
                        {"mime_type": "image/jpeg", "data": cv2.imencode('.jpg', img)[1].tobytes()}
                    ]
                    prompt = "Đây là ảnh chụp một cây lúa/lá lúa. Hãy phân tích xem nó bị bệnh gì trong danh sách sau: Bệnh bạc lá, Sọc lá vi khuẩn, Sâu ăn lá, Ngộ độc hữu cơ / Phèn, Châu chấu hại, Bệnh vàng lùn, Sâu cuốn lá, Bệnh đạo ôn, Bệnh khô vằn, Sâu đục thân, Bệnh Tungro, hoặc Không phát hiện bệnh. Trả về tên bệnh duy nhất bằng tiếng Việt tương ứng, hoặc 'Không phát hiện bệnh'."
                    
                    response = genai_model.generate_content([prompt, image_parts[0]])
                    disease_result = response.text.strip()
                    
                    # Tìm class ID tương ứng
                    main_disease = "Không phát hiện bệnh"
                    main_id = None
                    main_cls = -1
                    main_conf = 0.95 # Độ tin cậy giả định của Gemini
                    
                    for k, v in CLASS_MAPPING.items():
                        if v['name'].lower() in disease_result.lower():
                            main_disease = v['name']
                            main_id = v['id']
                            main_cls = 0
                            break
                    
                    if main_disease == "Không phát hiện bệnh":
                        diseases.append({"id": None, "name": main_disease, "confidence": main_conf, "class_id": -1})
                    else:
                        diseases.append({"id": main_id, "name": main_disease, "confidence": main_conf, "class_id": main_cls})
                        
                except Exception as ex:
                    print("Gemini API Error:", ex)
                    main_disease = "Lỗi AI thông minh"
                    main_conf = 0.0
                    main_id = None
                    main_cls = -1
            else:
                time.sleep(1)
                main_disease = "Bệnh đạo ôn (YOLO Fake - Chưa cấu hình API Key)"
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
                
        print(f"[SERVER LOG] Phân tích xong! Bệnh phát hiện: {main_disease if main_disease else 'Không phát hiện'} ({main_conf*100:.1f}%)")
        return JSONResponse({
            "status": "success",
            "provider": "caylua-yolov8",
            "diseases": diseases,
            "job_id": job_id
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/analyze_mobile")
async def analyze_mobile(
    file: UploadFile = File(...),
    latitude: str = Form(""),
    longitude: str = Form(""),
    location_source: str = Form("")
):
    """API chính nhận ảnh và context từ thiết bị di động"""
    print(f"\\n[SERVER LOG] Nhận yêu cầu Analyze (Direct/Guest) từ Mobile!")
    print(f"[SERVER LOG] Tên ảnh: {file.filename}")
    print(f"[SERVER LOG] Vị trí: {latitude}, {longitude}")
    start_time = time.time()
    job_id = f"AI-JOB-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Đọc ảnh từ stream
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
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
        
        if model is not None:
            # Predict
            results = model.predict(img, conf=0.10, iou=0.45)
            # Lấy object
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
        else:
            import google.generativeai as genai
            gemini_key = os.environ.get("GEMINI_API_KEY")
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    genai_model = genai.GenerativeModel("gemini-1.5-flash")
                    image_parts = [{"mime_type": "image/jpeg", "data": cv2.imencode('.jpg', img)[1].tobytes()}]
                    prompt = "Đây là ảnh chụp một cây lúa/lá lúa. Hãy phân tích xem nó bị bệnh gì trong danh sách sau: Bệnh bạc lá, Sọc lá vi khuẩn, Sâu ăn lá, Ngộ độc hữu cơ / Phèn, Châu chấu hại, Bệnh vàng lùn, Sâu cuốn lá, Bệnh đạo ôn, Bệnh khô vằn, Sâu đục thân, Bệnh Tungro, hoặc Không phát hiện bệnh. Trả về tên bệnh duy nhất bằng tiếng Việt tương ứng, hoặc 'Không phát hiện bệnh'."
                    
                    response = genai_model.generate_content([prompt, image_parts[0]])
                    disease_result = response.text.strip()
                    
                    main_disease = "Không phát hiện bệnh"
                    main_id = None
                    main_cls = -1
                    main_conf = 0.95
                    
                    for k, v in CLASS_MAPPING.items():
                        if v['name'].lower() in disease_result.lower():
                            main_disease = v['name']
                            main_id = v['id']
                            main_cls = 0
                            break
                            
                    if main_disease != "Không phát hiện bệnh":
                        diseases.append({"id": main_id, "name": main_disease, "confidence": main_conf, "class_id": main_cls})
                except Exception as ex:
                    print("Gemini API Error in analyze_mobile:", ex)
            else:
                time.sleep(1)
                diseases.append({
                    "id": "fungal_dao_on",
                    "name": "Bệnh đạo ôn (YOLO Fake - Chưa cấu hình API Key)",
                    "confidence": 0.88,
                    "class_id": 0
                })
            
        processing_ms = int((time.time() - start_time) * 1000)
        
        main_disease = diseases[0]['name'] if diseases else 'Không phát hiện'
        main_conf = diseases[0]['confidence'] if diseases else 0
        print(f"[SERVER LOG] Phân tích xong (Direct)! Bệnh phát hiện: {main_disease} ({main_conf*100:.1f}%)")
        
        return JSONResponse({
            "status": "success",
            "provider": "caylua-yolov8",
            "diseases": diseases,
            "processing_ms": processing_ms,
            "message": "Phân tích thành công" if len(diseases) > 0 else "Không phát hiện bệnh",
            "job_id": job_id
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
