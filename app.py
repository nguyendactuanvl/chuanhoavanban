import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# 1. Cấu hình trang
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📄 Chuẩn Hóa Văn Bản Hành Chính</h1>", unsafe_allow_html=True)

# 2. Cấu hình API (Dán Key của bạn vào đây)
API_KEY = "AIzaSyA00LWbDGphFpsvUWdQOVAJ6K_15ckEUKg"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Hàm để đọc file Docx
def read_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# 3. Giao diện chia cột
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải lên file Word (.docx)", type=["docx"])
    
    user_content = st.text_area("HOẶC dán nội dung văn bản vào đây:", height=250)
    btn_run = st.button("🚀 Chuẩn hóa văn bản", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả chuẩn hóa")
    
    # Ưu tiên lấy nội dung từ file tải lên, nếu không có thì lấy từ ô dán văn bản
    final_input = ""
    if uploaded_file is not None:
        final_input = read_docx(uploaded_file)
    elif user_content:
        final_input = user_content

    if btn_run:
        if final_input:
            with st.spinner('Đang xử lý văn bản...'):
                try:
                    prompt = f"Hãy đóng vai chuyên gia văn thư, chuẩn hóa đoạn văn bản sau đúng quy định hành chính Nghị định 30/2020/NĐ-CP: {final_input}"
                    response = model.generate_content(prompt)
                    
                    st.success("Đã chuẩn hóa xong!")
                    st.write(response.text)
                    
                    # Nút tải kết quả về dạng text (tạm thời)
                    st.download_button("Tải kết quả (.txt)", response.text, file_name="ket_qua.txt")
                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
        else:
            st.warning("Vui lòng tải file hoặc nhập nội dung!")
