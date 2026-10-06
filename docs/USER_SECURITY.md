# User Security
Tất cả các bảng trong DB đều được bật Row Level Security (RLS).
User A chỉ SELECT/UPDATE được where `user_id = auth.uid()`.
Frontend sử dụng Publishable Key. Service Role Key KHÔNG lưu ở frontend.
