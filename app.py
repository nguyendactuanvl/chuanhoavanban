import streamlit as st
import google.generativeai as genai
from docx import Document
import re

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

st.markdown("""
    <style>
    .to-giay-a4 {
        background-color: white;
        padding: 40px;
        color: black !important;
        font-family: 'Times New Roman', Times, serif;
        font-size: 14pt;
        line-height: 1.5;
        border: 1px solid #ccc;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        min-height: 800px;
        margin: auto;
    }
    /* Đảm bảo chữ bên trong luôn đen và rõ */
    .to-giay-a4 div, .to-giay-a4 p, .to-giay-a4 td, .to-giay-a4 b {
        color: black !important;
    }
    table { width: 100%; border-collapse: collapse; border: none !important; }
    td { border: none !important; vertical-align: top; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Cấu hình App")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    if st.button("🔄 Làm mới trang"):
        st.rerun()

st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Thầy vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. KHỞI TẠO AI ---
@st.cache_resource
def get_model(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        
        # Chỉ dẫn cực kỳ nghiêm ngặt để AI không bọc code lung tung
        instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản hành chính. TRẢ VỀ DUY NHẤT MÃ HTML. TUYỆT ĐỐI KHÔNG dùng dấu ``` hay ghi chữ 'html'. Chỉ trả về nội dung bên trong văn bản."
        return genai.GenerativeModel(model_name=name, system_instruction=instruct)
    except Exception as e:
        return str(e)

ai_model = get_model(user_api_key)

# --- 3. XỬ LÝ ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Dán nội dung:", height=450)
    process_btn = st.button("🚀 BẮT ĐẦU CHUẨN HÓA", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả thực tế")
    input_data = ""
    if uploaded_file:
        doc_in = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc_in.paragraphs])
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("Đang loại bỏ mã code và dàn trang..."):
                try:
                    response = ai_model.generate_content(input_data)
                    raw_html = response.text
                    
                    # Mẹo kỹ thuật: Loại bỏ các dấu bọc code ```html nếu AI lỡ tay thêm vào
                    clean_html = re.sub(r'```html|```', '', raw_html)
                    
                    # HIỂN THỊ THÀNH VĂN BẢN THẬT
                    st.markdown(f'<div class="to-giay-a4">{clean_html}</div>', unsafe_allow_html=True)
                    
                    st.success("✅ Đã xong! Thầy hãy bôi đen văn bản trên và dán vào Word.")
                except Exception as ex:
                    st.error(f"Lỗi hiển thị: {ex}")
