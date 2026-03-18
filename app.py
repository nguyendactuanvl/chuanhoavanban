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

# --- KẾT NỐI AI (BẢN KIỂM TRA LỖI CHI TIẾT) ---
try:
    genai.configure(api_key=user_api_key)
    # Thử kết nối trực tiếp với model cơ bản nhất để kiểm tra Key
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Kiểm tra xem Key có quyền liệt kê Model không (Để xác định Key sống hay chết)
    available_models = [m.name for m in genai.list_models()]
    st.sidebar.success(f"✅ Kết nối thành công!")
    st.sidebar.write("Model khả dụng:", available_models)
    
except Exception as e:
    st.error(f"❌ Lỗi kết nối hệ thống: {str(e)}")
    if "403" in str(e):
        st.info("Mẹo: Lỗi 403 thường do vùng địa lý (Việt Nam đôi khi bị chặn API trực tiếp). Hãy thử dùng mạng khác hoặc kiểm tra lại quyền của Key.")
    elif "400" in str(e):
        st.info("Mẹo: API Key không hợp lệ hoặc đã hết hạn.")
    st.stop()

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
        doc = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc.paragraphs])
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("AI đang xử lý..."):
                try:
                    prompt = f"Chuẩn hóa đoạn văn bản sau đúng quy định Nghị định 30/2020/NĐ-CP: \n\n{input_data}"
                    response = model.generate_content(prompt)
                    st.success("Xong!")
                    st.write(response.text)
                except Exception as ex:
                    st.error(f"Lỗi khi xử lý: {str(ex)}")
