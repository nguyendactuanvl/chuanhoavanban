import streamlit as st
import google.generativeai as genai
from docx import Document

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

# CSS để kết quả hiện ra trắng trẻo, giống tờ giấy A4
st.markdown("""
    <style>
    .giay-a4 {
        background-color: white;
        padding: 40px;
        color: black;
        font-family: 'Times New Roman', serif;
        border: 1px solid #ccc;
        border-radius: 5px;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    if st.button("🔄 Làm mới trang"):
        st.rerun()

st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Thầy vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. KHỞI TẠO AI (BẢN TỰ ĐỘNG QUÉT MODEL - KHỬ LỖI 404) ---
@st.cache_resource
def get_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Quét lấy tên model chuẩn để tránh lỗi 404
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        
        # Bí kíp prompt từ AI Studio của thầy
        instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản theo Nghị định 187/2025/NĐ-CP. TRẢ VỀ MÃ HTML (dùng bảng cho phần đầu/cuối). Không giải thích thêm."
        
        return genai.GenerativeModel(model_name=name, system_instruction=instruct), name
    except Exception as e:
        return None, str(e)

ai, m_name = get_model(user_api_key)

if ai is None:
    st.error(f"Lỗi: {m_name}")
    st.stop()

# --- 3. GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Dán nội dung:", height=400)
    process_btn = st.button("🚀 CHUẨN HÓA NGAY", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả chuyên gia")
    input_data = ""
    if uploaded_file:
        doc = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc.paragraphs])
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("Đang trình bày văn bản..."):
                try:
                    response = ai.generate_content(input_data)
                    # LỆNH QUAN TRỌNG NHẤT: Hiển thị HTML chứ không hiện mã code
                    st.markdown(f'<div class="giay-a4">{response.text}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.info("💡 Thầy hãy bôi đen nội dung trên và dán vào Word là đẹp ngay ạ!")
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")
