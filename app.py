import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Chuẩn hóa văn bản hành chính AI",
    page_icon="📄",
    layout="wide"
)

# --- THANH BÊN (SIDEBAR) ĐỂ NHẬP API KEY ---
with st.sidebar:
    st.title("🔑 Cấu hình")
    user_api_key = st.text_input("Nhập Gemini API Key của bạn:", type="password", help="Lấy Key tại: https://aistudio.google.com/app/apikey")
    st.info("💡 Lưu ý: API Key của bạn sẽ không bị lưu lại trên hệ thống.")
    st.markdown("---")
    st.markdown("### Hướng dẫn lấy API Key:")
    st.markdown("1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey)\n2. Nhấn 'Create API key'\n3. Copy và dán vào ô trên.")

# --- GIAO DIỆN CHÍNH ---
st.markdown("<h1 style='text-align: center; color: #0D47A1;'>📄 Chuẩn Hóa Văn Bản Hành Chính</h1>", unsafe_allow_html=True)
st.divider()

# Kiểm tra xem người dùng đã nhập API Key chưa
if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở thanh bên trái để bắt đầu sử dụng ứng dụng!")
    st.stop() # Dừng ứng dụng tại đây nếu chưa có Key

# Cấu hình AI với Key người dùng nhập
try:
    genai.configure(api_key=user_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Lỗi cấu hình AI: {e}")
    st.stop()

# --- CÁC HÀM TIỆN ÍCH ---
def read_docx(file):
    try:
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    except:
        return ""

# --- GIAO DIỆN CHIA 2 CỘT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải lên file Word (.docx)", type=["docx"])
    user_content = st.text_area("Hoặc dán nội dung văn bản vào đây:", height=300)
    btn_run = st.button("🚀 Bắt đầu chuẩn hóa", use_container_width=True, type="primary")

with col2:
    st.subheader("📥 Kết quả chuẩn hóa")
    
    input_to_process = ""
    if uploaded_file:
        input_to_process = read_docx(uploaded_file)
    elif user_content:
        input_to_process = user_content

    if btn_run:
        if not input_to_process:
            st.warning("Vui lòng cung cấp nội dung!")
        else:
            with st.spinner("Đang xử lý..."):
                try:
                    prompt = f"Hãy chuẩn hóa đoạn văn bản sau đúng quy định hành chính Nghị định 30/2020/NĐ-CP: \n\n{input_to_process}"
                    response = model.generate_content(prompt)
                    
                    st.success("Hoàn thành!")
                    st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; color: black;">
                        {response.text.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.download_button("💾 Tải kết quả (.txt)", response.text, file_name="ket_qua.txt")
                except Exception as e:
                    st.error(f"Lỗi: {e}. Hãy kiểm tra lại tính chính xác của API Key.")
