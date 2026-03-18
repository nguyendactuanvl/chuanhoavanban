import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
import io

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide", page_icon="📝")

# Hàm tạo file Word (Dùng để người dùng tải lên Google Docs)
def create_docx(text):
    doc = Document()
    # Thiết lập font chữ chuẩn hành chính
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    
    for line in text.split('\n'):
        doc.add_paragraph(line)
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# Giao diện Header
st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Hỗ trợ copy nhanh và xuất bản thảo chuyên nghiệp</p>", unsafe_allow_html=True)

# Nút Làm mới ở góc trên
if st.button("🔄 Làm mới dữ liệu", use_container_width=False):
    st.rerun()

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")
    st.divider()
    st.write("👨‍🏫 **Tác giả:** Nguyễn Đắc Tuấn")

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. KẾT NỐI AI ---
@st.cache_resource
def get_ai_model(api_key):
    try:
        genai.configure(api_key=api_key)
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else available[0]
        
        instruct = "Bạn là chuyên gia văn thư hành chính. Hãy chuẩn hóa văn bản theo Nghị định 30/2020/NĐ-CP. Sửa lỗi chính tả, trình bày đúng thể thức Quốc hiệu, Tiêu ngữ, viết hoa chuẩn."
        return genai.GenerativeModel(model_name=selected, system_instruction=instruct)
    except Exception as e:
        return str(e)

model_ai = get_ai_model(user_api_key)

# --- 3. GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải lên file Word (.docx)", type=["docx"])
    user_text = st.text_area("Hoặc dán nội dung trực tiếp:", height=300)
    process_btn = st.button("🚀 CHUẨN HÓA VĂN BẢN", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả chuẩn hóa")
    
    input_data = ""
    if uploaded_file:
        doc = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc.paragraphs])
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("Đang chuẩn hóa theo Nghị định 30..."):
                try:
                    response = model_ai.generate_content(input_data, generation_config={"temperature": 0.2})
                    st.session_state['last_result'] = response.text
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")
        else:
            st.warning("Vui lòng nhập nội dung!")

    # HIỂN THỊ KẾT QUẢ VÀ CÁC NÚT CHỨC NĂNG
    if 'last_result' in st.session_state:
        result = st.session_state['last_result']
        
        # Ô hiển thị văn bản (Có thể copy trực tiếp)
        st.text_area("Nội dung đã chuẩn hóa (Bạn có thể Ctrl+A để copy):", value=result, height=300)
        
        st.divider()
        # HÀNG NÚT CHỨC NĂNG
        c1, c2, c3 = st.columns(3)
        
        with c1:
            # Chức năng Tải xuống Word
            st.download_button(
                label="📥 Tải xuống Word",
                data=create_docx(result),
                file_name="van_ban_chuan_hoa.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with c2:
            # Hướng dẫn copy
            st.info("Nhấn Ctrl+A rồi Ctrl+C ở ô văn bản trên để Copy nhanh.")
            
        with c3:
            # Chức năng mở Google Docs (Thông qua link tạo mới)
            st.link_button("🌐 Mở Google Docs", "https://docs.google.com/document/u/0/create", use_container_width=True, help="Nhấn vào đây để tạo trang Google Docs mới và dán kết quả vào.")

st.divider()
st.caption("Ứng dụng được thiết kế riêng cho thầy Nguyễn Đắc Tuấn.")
