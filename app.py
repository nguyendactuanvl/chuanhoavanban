import streamlit as st
import google.generativeai as genai

# 1. Cấu hình trang chuyên nghiệp
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

# Giao diện phía trên
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📄 Chuẩn Hóa Văn Bản Hành Chính</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Theo Nghị định 30/2020/NĐ-CP & Quy định Bộ Xây dựng</p>", unsafe_allow_html=True)

# 2. Cấu hình API (Thay bằng Key của bạn)
API_KEY = "AIzaSyA00LWbDGphFpsvUWdQOVAJ6K_15ckEUKg"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Chia cột giao diện (Cột trái: Nhập liệu - Cột phải: Kết quả)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    # Thêm tính năng tải file (như trong ảnh bạn muốn)
    uploaded_file = st.file_uploader("Tải lên file Word (.docx)", type=["docx"])
    
    st.write("HOẶC")
    
    user_content = st.text_area("Dán nội dung văn bản:", height=300)
    
    btn_run = st.button("🚀 Chuẩn hóa văn bản", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả chuẩn hóa")
    if btn_run:
        if user_content:
            with st.spinner('Đang xử lý...'):
                # Nội dung yêu cầu AI
                prompt = f"Hãy đóng vai chuyên gia văn thư, chuẩn hóa đoạn văn bản sau đúng quy định hành chính: {user_content}"
                response = model.generate_content(prompt)
                
                # Hiển thị kết quả trong khung
                st.info("Nội dung đã được xử lý:")
                st.write(response.text)
                
                # Nút tải xuống (giả lập)
                st.download_button("Tải xuống bản Word", response.text, file_name="van_ban_chuan_hoa.txt")
        else:
            st.warning("Vui lòng nhập nội dung hoặc tải file!")
    else:
        st.write("Kết quả sẽ hiển thị tại đây sau khi bạn nhấn nút.")
