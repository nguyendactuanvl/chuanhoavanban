import streamlit as st
import google.generativeai as genai
from docx import Document

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide", page_icon="📝")

with st.sidebar:
    st.title("⚙️ Cấu hình App")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")
    st.divider()
    st.write("👨‍🏫 **Tác giả:** Nguyễn Đắc Tuấn")

st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái để bắt đầu!")
    st.stop()

# --- CẤU HÌNH MODEL (SỬA LỖI 404 VỚI SYSTEM INSTRUCTION) ---
@st.cache_resource
def load_model(api_key):
    try:
        genai.configure(api_key=api_key)
        
        # CHỈ DẪN HỆ THỐNG (Thầy có thể sửa nội dung trong ngoặc này cho giống AI Studio của thầy)
        instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản theo Nghị định 30/2020/NĐ-CP. Sửa lỗi chính tả, viết hoa và trình bày trang trọng."
        
        # Cách gọi model này giúp tránh lỗi 404 khi dùng System Instruction
        model = genai.GenerativeModel(
            model_name='models/gemini-1.5-flash', # Thêm 'models/' vào trước tên
            system_instruction=instruct
        )
        return model
    except Exception as e:
        return str(e)

model_ai = load_model(user_api_key)

if isinstance(model_ai, str):
    st.error(f"Lỗi hệ thống: {model_ai}")
    st.stop()

# --- GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file Word (.docx)", type=["docx"])
    user_text = st.text_area("Hoặc dán nội dung:", height=300)
    btn = st.button("🚀 BẮT ĐẦU CHUẨN HÓA", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả")
    input_data = ""
    if uploaded_file:
        doc = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc.paragraphs])
    elif user_text:
        input_data = user_text

    if btn:
        if input_data:
            with st.spinner("Đang xử lý..."):
                try:
                    # Cấu hình tham số để kết quả chuẩn xác nhất
                    config = {"temperature": 0.1, "top_p": 0.95}
                    response = model_ai.generate_content(input_data, generation_config=config)
                    
                    st.success("Hoàn thành!")
                    st.write(response.text)
                    st.download_button("💾 Tải file (.txt)", response.text, "ket_qua.txt")
                except Exception as ex:
                    st.error(f"Lỗi khi xử lý: {str(ex)}")
        else:
            st.warning("Vui lòng nhập nội dung!")
