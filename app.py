import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches
import io
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
        min-height: 600px;
        margin-bottom: 20px;
    }
    .to-giay-a4 * { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# Hàm xử lý tạo file Word từ nội dung AI
def create_word_file(html_text):
    doc = Document()
    # Chỉnh lề chuẩn Nghị định
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)
    
    # Loại bỏ các thẻ HTML để lấy text sạch đưa vào Word
    clean_text = re.sub(r'<[^>]+>', '', html_text)
    
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    
    for line in clean_text.split('\n'):
        if line.strip():
            p = doc.add_paragraph(line.strip())
            p.paragraph_format.line_spacing = 1.5
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

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
        
        # Chỉ dẫn ép AI làm đúng vai trò
        instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản hành chính theo Nghị định 187. Trả về mã HTML đơn giản. Không dùng dấu bọc code."
        return genai.GenerativeModel(model_name=name, system_instruction=instruct)
    except Exception as e:
        return str(e)

ai_model = get_model(user_api_key)

# --- 3. XỬ LÝ ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Dán nội dung:", height=400)
    process_btn = st.button("🚀 CHUẨN HÓA VĂN BẢN", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả chuyên gia")
    input_data = ""
    if uploaded_file:
        doc_in = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc_in.paragraphs])
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("Đang chuẩn hóa..."):
                try:
                    response = ai_model.generate_content(input_data)
                    clean_res = re.sub(r'```html|```', '', response.text)
                    st.session_state['final_res'] = clean_res
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")

    if 'final_res' in st.session_state:
        # 1. Hiển thị tờ giấy A4 để xem trước
        st.markdown(f'<div class="to-giay-a4">{st.session_state["final_res"]}</div>', unsafe_allow_html=True)
        
        # 2. NÚT TẢI VỀ FILE WORD (ĐÃ THÊM LẠI)
        st.divider()
        word_data = create_word_file(st.session_state['final_res'])
        st.download_button(
            label="📥 TẢI VỀ FILE WORD (.DOCX)",
            data=word_data,
            file_name="van_ban_da_chuan_hoa.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        st.success("✅ Đã tạo xong nút tải về! Thầy nhấn nút xanh ở trên để lưu file nhé.")
