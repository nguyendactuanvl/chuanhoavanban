import streamlit as st
import google.generativeai as genai
from docx import Document

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")
    if st.button("🔄 Làm mới trang"):
        st.rerun()

st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. HÀM KHỞI TẠO AI "THÔNG MINH" (TRÁNH LỖI 404) ---
@st.cache_resource
def get_working_model(api_key):
    try:
        genai.configure(api_key=api_key)
        
        # Bước quan trọng: Quét danh sách các model mà Key này được phép dùng
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Ưu tiên chọn theo thứ tự, nếu không có cái nào thì lấy cái đầu tiên trong danh sách
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        final_model_name = available_models[0] if available_models else None
        
        for p in priority:
            if p in available_models:
                final_model_name = p
                break
        
        if not final_model_name:
            return None, "Không tìm thấy model khả dụng trong tài khoản của bạn."

        # Nội dung bí kíp từ AI Studio của thầy Tuấn
        instruct = """Bạn là một chuyên gia ngôn ngữ học và chuyên gia văn thư lưu trữ tại Việt Nam.
Nhiệm vụ: Sửa lỗi chính tả, ngữ pháp và chuẩn hóa văn bản theo Nghị định 187/2025/NĐ-CP.
Yêu cầu: Trình bày kết quả dưới dạng HTML (dùng bảng <table> cho phần đầu và cuối).
Font chữ: Times New Roman, cỡ 14pt. Chỉ trả về mã HTML thuần túy."""

        model = genai.GenerativeModel(model_name=final_model_name, system_instruction=instruct)
        return model, final_model_name
    except Exception as e:
        return None, str(e)

# Chạy khởi tạo
ai_model, model_info = get_working_model(user_api_key)

if ai_model is None:
    st.error(f"❌ Lỗi: {model_info}")
    st.stop()
else:
    st.sidebar.success(f"✅ Đang dùng: {model_info}")

# --- 3. XỬ LÝ VĂN BẢN ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Hoặc dán nội dung tại đây:", height=400)
    process_btn = st.button("🚀 CHUẨN HÓA VĂN BẢN", type="primary", use_container_width=True)

with col2:
    if process_btn:
        input_data = ""
        if uploaded_file:
            doc = Document(uploaded_file)
            input_data = "\n".join([p.text for p in doc.paragraphs])
        else:
            input_data = user_text

        if input_data:
            with st.spinner("Đang chuẩn hóa..."):
                try:
                    response = ai_model.generate_content(input_data)
                    # Hiển thị kết quả HTML trực tiếp
                    st.markdown(f'<div style="background:white; padding:20px; border-radius:10px; color:black; font-family:Times New Roman;">{response.text}</div>', unsafe_allow_html=True)
                except Exception as ex:
                    st.error(f"Lỗi xử lý: {str(ex)}")
