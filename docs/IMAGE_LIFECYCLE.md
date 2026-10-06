# Image Lifecycle
1. Upload -> DB `images` (Trạng thái: PENDING_AI).
2. Backend YOLO xử lý -> `images` cập nhật (COMPLETED/FAILED).
3. Không bao giờ ghi đè ảnh gốc. Ảnh box được lưu riêng nếu cần.
