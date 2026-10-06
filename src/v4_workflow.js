// V4 Orchestration Workflow

window.V4Workflow = {
    async processSurveyPoint(file, lat, lng, isOffline = false) {
        try {
            console.log("V4 Workflow: Bắt đầu xử lý điểm khảo sát mới");
            
            // 1. Get User & Field Context
            const user = await AuthService.getUser();
            const userId = user ? user.id : '00000000-0000-0000-0000-000000000000'; // mock fallback
            
            // Assume we have a default field for now if none exists
            let fields = await FieldService.getFields();
            let fieldId = null;
            let cropAgeDays = 30; // default mock
            if (fields.length > 0) {
                fieldId = fields[0].id;
                if(fields[0].sowing_date) {
                    const sow = new Date(fields[0].sowing_date);
                    cropAgeDays = Math.floor((new Date() - sow) / (1000 * 60 * 60 * 24));
                }
            } else {
                const newField = await FieldService.createField({
                    user_id: userId,
                    name: 'Ruộng Mặc Định (V4)',
                    latitude: lat,
                    longitude: lng,
                    sowing_date: new Date(Date.now() - 30*24*60*60*1000).toISOString().split('T')[0]
                });
                if(newField) fieldId = newField.id;
            }
            
            // 2. Tọa độ, Thời gian & Metadata
            const capturedAt = new Date().toISOString();
            
            // 3. Quản lý Ảnh gốc (Storage + DB)
            let storagePath = `original/${userId}/${Date.now()}_${file.name}`;
            let imageRecord = null;
            let aiJob = null;
            
            if (isOffline) {
                console.log("Offline mode: queued for sync");
                // TODO: Store in IndexedDB properly conforming to new schema
                // For now, reuse Dexie logic if needed
            } else {
                // Upload
                await ImageService.uploadImage(file, storagePath);
                
                // Create Image DB record
                imageRecord = await ImageService.createImageRecord({
                    user_id: userId,
                    field_id: fieldId,
                    original_filename: file.name,
                    storage_path: storagePath,
                    mime_type: file.type,
                    file_size: file.size,
                    captured_at: capturedAt,
                    latitude: lat,
                    longitude: lng,
                    location_source: 'gps',
                    processing_status: 'PENDING_AI'
                });
                
                // 4. Create AI Job
                aiJob = await AiJobService.createJob({
                    image_id: imageRecord.id,
                    user_id: userId,
                    field_id: fieldId,
                    provider: 'YOLO',
                    status: 'PROCESSING',
                    started_at: new Date().toISOString()
                });
            }
            
            // 5. Call AI Backend
            let aiResult = null;
            let finalDisease = "Chưa có kết quả";
            let finalConf = 0;
            
            if (!isOffline) {
                try {
                    const formData = new FormData();
                    formData.append("file", file);
                    const aiUrl = (window.CAYLUA_CONFIG && window.CAYLUA_CONFIG.aiUrl) ? window.CAYLUA_CONFIG.aiUrl : 'http://localhost:8000/api/ai/predict';
                    
                    const res = await fetch(aiUrl, { method: 'POST', body: formData });
                    
                    if (res.ok) {
                        aiResult = await res.json();
                        finalDisease = aiResult.disease;
                        finalConf = aiResult.confidence;
                        
                        // Update Job
                        await AiJobService.updateJob(aiJob.id, { 
                            status: 'COMPLETED',
                            completed_at: new Date().toISOString()
                        });
                        
                        // 6. Save AI Analysis & Detections
                        const analysis = await DetectionService.saveAnalysis({
                            job_id: aiJob.id,
                            image_id: imageRecord.id,
                            provider: 'YOLO',
                            status: 'SUCCESS',
                            overall_confidence: finalConf,
                            summary: finalDisease,
                            raw_result_json: aiResult
                        });
                        
                        if (aiResult.bbox) {
                            await DetectionService.saveDetections([{
                                analysis_id: analysis.id,
                                image_id: imageRecord.id,
                                class_id: aiResult.class_id,
                                disease_name: finalDisease,
                                confidence: finalConf,
                                bbox_x: aiResult.bbox[0],
                                bbox_y: aiResult.bbox[1],
                                bbox_width: aiResult.bbox[2],
                                bbox_height: aiResult.bbox[3],
                                severity: 'high'
                            }]);
                        }
                        
                        // Update Image status
                        await ImageService.updateImage(imageRecord.id, { processing_status: 'COMPLETED' });
                        
                    } else {
                        throw new Error('AI Server responded with error');
                    }
                } catch(e) {
                    console.error("AI Fallback triggered:", e);
                    if(aiJob) {
                        await AiJobService.updateJob(aiJob.id, { 
                            status: 'FAILED',
                            error_message: e.message
                        });
                    }
                    if(imageRecord) {
                        await ImageService.updateImage(imageRecord.id, { processing_status: 'FAILED' });
                    }
                }
            }
            
            // 7. Create Inspection
            let inspection = null;
            if(!isOffline) {
                inspection = await InspectionService.createInspection({
                    user_id: userId,
                    field_id: fieldId,
                    image_id: imageRecord ? imageRecord.id : null,
                    ai_job_id: aiJob ? aiJob.id : null,
                    latitude: lat,
                    longitude: lng,
                    location_source: 'gps',
                    captured_at: capturedAt,
                    crop_age_days: cropAgeDays,
                    status: 'completed',
                    severity: finalConf > 0.8 ? 'high' : 'normal'
                });
                
                // 8. Create Insight & Alert if disease detected
                if (aiResult && finalConf > 0.6) {
                    const insightObj = InsightService.generateInsight(inspection, {summary: finalDisease, overall_confidence: finalConf}, null);
                    if (insightObj) {
                        insightObj.user_id = userId;
                        insightObj.field_id = fieldId;
                        insightObj.inspection_id = inspection.id;
                        insightObj.image_id = imageRecord.id;
                        await InsightService.createInsight(insightObj);
                    }
                    
                    await AlertService.createAlert({
                        user_id: userId,
                        field_id: fieldId,
                        inspection_id: inspection.id,
                        title: 'Phát hiện bệnh: ' + finalDisease,
                        message: `Hệ thống vừa phát hiện ${finalDisease} tại ruộng. Vui lòng kiểm tra.`,
                        severity: 'high'
                    });
                }
            }
            
            // 9. Update UI (Map & History)
            // We append to window.data directly so map_centric.js render() picks it up immediately.
            const newDataPoint = {
                db_id: inspection ? inspection.id : 'temp_' + Date.now(),
                f: 'Điểm',
                s: 'Điểm khảo sát',
                d: finalDisease,
                c: finalConf * 100,
                a: cropAgeDays,
                g: 'Sinh trưởng',
                t: capturedAt,
                lat: lat,
                lng: lng,
                provider: 'YOLO (V4)',
                img: file
            };
            
            if (window.data) {
                window.data.unshift(newDataPoint);
            }
            
            if (typeof window.render === 'function') {
                window.render();
            }
            
            console.log("V4 Workflow: Hoàn tất!");
            
        } catch(e) {
            console.error("V4 Workflow Lỗi:", e);
        }
    }
};

// Override window.saveCheck to use V4Workflow
window.saveCheck = async function() {
    const lat = document.getElementById('lat').value;
    const lng = document.getElementById('lng').value;
    const files = document.getElementById('camera-input').files;
    if (!files.length && !window.capturedBlob) {
        alert("Vui lòng chụp hoặc chọn ảnh!");
        return;
    }
    const file = window.capturedBlob ? new File([window.capturedBlob], "capture.jpg", {type:"image/jpeg"}) : files[0];
    
    // Check network
    const isOffline = !navigator.onLine;
    
    // Show uploading state
    document.querySelector('.upload-btn').innerHTML = '⏳ Đang xử lý...';
    
    // Execute V4 Workflow
    await V4Workflow.processSurveyPoint(file, parseFloat(lat), parseFloat(lng), isOffline);
    
    // Reset UI
    document.querySelector('.upload-btn').innerHTML = '📷 CHỤP ẢNH / UPLOAD';
    document.getElementById('popup-container').style.display = 'none';
    if(window.capturedBlob) window.capturedBlob = null;
    
    // Auto sync if back online
    if (!isOffline && window.SyncService) {
        window.SyncService.processQueue();
    }
};
