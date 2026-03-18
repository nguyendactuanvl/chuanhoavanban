import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

# HÀM TẠO FILE WORD CHUẨN NGHỊ ĐỊNH (BÍ QUYẾT Ở ĐÂY)
def export_to_word(html_content):
    doc = Document()
    
    # Thiết lập lề trang chuẩn (Trái 3cm, Phải 1.5cm, Trên 2cm, Dưới 2cm)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.59)

    # Style mặc định: Times New Roman, Size 14
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)

    # Chuyển nội dung từ AI vào Word (Dùng đoạn text thô để xử lý)
    # Lưu ý: Đây là xử lý đơn giản hóa, AI trả về text sạch sẽ giúp Word đẹp hơn
    paragraphs = html_content.split('\n')
    for p_text in paragraphs:
        if p_text.strip():
            para = doc.add_paragraph(p_text)
            para.paragraph_format.line_spacing = 1.5
            para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    if st.button("🔄 Làm mới trang"):
        st.rerun()

st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Thầy vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. KHỞI TẠO AI ---
@st.cache_resource
def get_model(api_key):
    genai.configure(api_key=api_key)
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
    
    # Ép AI trả về text thuần để Python tự dựng file Word cho chuẩn
    instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản theo Nghị định 187/2025/NĐ-CP. Không trả về mã HTML, hãy trả về văn bản thô (plain text) nhưng trình bày đúng thứ tự các dòng. Không giải thích thêm."
    return genai.GenerativeModel(model_name=name, system_instruction=instruct)

ai = get_model(user_api_key)

# --- 3. XỬ LÝ VĂN BẢN ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Dán nội dung:", height=400)
    process_btn = st.button("🚀 CHUẨN HÓA VÀ XUẤT WORD", type="primary", use_container_width=True)

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
            with st.spinner("Đang dựng file Word chuẩn..."):
                try:
                    response = ai.generate_content(input_data)
                    result_text = response.text
                    
                    # Hiển thị xem trước
                    st.text_area("Xem trước nội dung:", value=result_text, height=300)
                    
                    # NÚT TẢI FILE WORD CHUẨN
                    word_file = export_to_word(result_text)
                    st.download_button(
                        label="📥 TẢI FILE WORD ĐÃ CHUẨN HÓA",
                        data=word_file,
                        file_name="van_ban_chuan_hoa.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    st.success("✅ Đã tạo xong file Word chuẩn font Times New Roman, cỡ 14, giãn dòng 1.5!")
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")
