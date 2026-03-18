# Cấu hình AI với Key người dùng nhập
try:
    genai.configure(api_key=user_api_key)
    
    # Tự động tìm model phù hợp nhất để tránh lỗi 404
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Ưu tiên flash 1.5, nếu không có thì lấy cái đầu tiên trong danh sách
    if 'models/gemini-1.5-flash' in available_models:
        model_name = 'models/gemini-1.5-flash'
    elif 'models/gemini-pro' in available_models:
        model_name = 'models/gemini-pro'
    else:
        model_name = available_models[0] if available_models else 'gemini-pro'
        
    model = genai.GenerativeModel(model_name)
    st.sidebar.success(f"Đang dùng: {model_name}")
    
except Exception as e:
    st.error(f"Lỗi: {e}")
    st.info("Mẹo: Hãy đảm bảo bạn đã tạo API Key mới nhất tại Google AI Studio.")
    st.stop()
