import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện
st.set_page_config(page_title="Chuẩn hóa văn bản", layout="centered")
st.title("📝 Ứng dụng Chuẩn hóa văn bản AI")

# Dán API Key của bạn vào giữa hai dấu ngoặc kép ở dưới
API_KEY = "AIzaSyA00LWbDGphFpsvUWdQOVAJ6K_15ckEUKg" 

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Giao diện nhập liệu
user_content = st.text_area("Nhập văn bản cần chuẩn hóa:", height=200)

if st.button("Bắt đầu chuẩn hóa"):
    if user_content:
        with st.spinner('Đang xử lý...'):
            response = model.generate_content(f"Hãy chuẩn hóa đoạn văn bản sau: {user_content}")
            st.success("Kết quả:")
            st.write(response.text)
    else:
        st.warning("Vui lòng nhập nội dung!")
