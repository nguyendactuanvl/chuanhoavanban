import streamlit as st
import google.generativeai as genai
from docx import Document

# --- CẤU HÌNH ---
st.set_page_config(page_title="Chuẩn hóa văn bản AI", layout="wide")

with st.sidebar:
    st.title("🔑 Cấu hình")
    user_api_key = st.text_input("Nhập Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")

st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- HÀM KẾT NỐI AI THÔNG MINH ---
@st.cache_resource
def initialize_ai(api_key):
    try:
        genai.configure(api_key=api_key)
        # Lấy danh sách tất cả model mà Key này được phép dùng
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            return None, "Không tìm thấy model nào hỗ trợ generateContent."

        # Thứ tự ưu tiên chọn model
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        selected_model = available_models[0] # Mặc định lấy cái đầu tiên
        
        for p in priority:
            if p in available_models:
                selected_model = p
                break
        
        return genai.GenerativeModel(selected_model), selected_model
    except Exception as e:
        return None, str(e)

# Khởi tạo
model, model_info = initialize_ai(user_api_key)

if model is None:
    st.error(f"❌ Lỗi hệ thống: {model_info}")
    st.stop()
else:
    st.sidebar.success(f"✅ Đang dùng: {model_info}")

# --- GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Hoặc dán văn bản:", height=300)
    process_btn = st.button("🚀 Chuẩn hóa ngay", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả")
    input_data = ""
    if uploaded_file:
        try:
            doc = Document(uploaded_file)
            input_data = "\n".join([p.text for p in doc.paragraphs])
        except:
            st.error("Không thể đọc file Word này.")
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("AI đang xử lý..."):
                try:
                    # Gọi trực tiếp model đã được khởi tạo thành công
                    response = model.generate_content(f"Chuẩn hóa đoạn văn bản sau đúng quy định Nghị định 30/2020/NĐ-CP: \n\n{input_data}")
                    st.success("Hoàn thành!")
                    st.write(response.text)
                except Exception as ex:
                    st.error(f"Lỗi khi xử lý: {str(ex)}")
        else:
            st.warning("Vui lòng nhập nội dung!")
