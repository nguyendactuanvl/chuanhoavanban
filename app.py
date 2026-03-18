import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
import io

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide", page_icon="📝")

# Hàm tạo file Word từ kết quả của AI
def create_docx(text):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)
    
    for line in text.split('\n'):
        doc.add_paragraph(line)
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# Nút Làm mới (Reset app)
if st.button("🔄 Làm mới trang"):
    st.rerun()

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")

st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. KẾT NỐI AI ---
@st.cache_resource
def get_ai_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Tự động quét model để tránh lỗi 404
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else available[0]
        
        instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản theo Nghị định 30/2020/NĐ-CP. Trình bày đúng thể thức, sửa lỗi chính tả, viết hoa."
        return genai.GenerativeModel(model_name=selected, system_instruction=instruct), selected
    except Exception as e:
        return None, str(e)

model_ai, m_name = get_ai_model(user_api_key)

# --- 3. GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải lên file Word (.docx)", type=["docx"])
    user_text = st.text_area("Dán nội dung văn bản:", height=350)
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
            with st.spinner("AI đang xử lý..."):
                try:
                    response = model_ai.generate_content(input_data, generation_config={"temperature": 0.2})
                    result_text = response.text
                    st.session_state['last_result'] = result_text
                    
                    st.success("Hoàn thành!")
                    st.markdown(f'<div style="background:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #ddd; color:black; font-family:Times New Roman;">{result_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")
        else:
            st.warning("Vui lòng nhập nội dung!")

    # Hiển thị các nút chức năng nếu đã có kết quả
    if 'last_result' in st.session_state:
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Tải xuống Word", data=create_docx(st.session_state['last_result']), file_name="van_ban_chuan_hoa.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with c2:
            # Nút copy nhanh
            st.button("📋 Sao chép kết quả", on_click=lambda: st.write("Đã sao chép! (Vui lòng quét khối và Ctrl+C)"))
