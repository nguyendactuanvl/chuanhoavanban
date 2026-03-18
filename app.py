import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

# Hàm tạo file Word nâng cao (Xử lý định dạng chuyên nghiệp hơn)
def create_docx(text):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)
    
    for line in text.split('\n'):
        p = doc.add_paragraph(line)
        # Nếu là Quốc hiệu hoặc Tên cơ quan (giả định dựa trên nội dung), có thể căn giữa
        if "CỘNG HÒA XÃ HỘI" in line or "Độc lập - Tự do" in line or "TỜ TRÌNH" in line:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key!")
    st.stop()

# --- 2. CHỈ DẪN HỆ THỐNG CỰC KỲ CHI TIẾT ---
@st.cache_resource
def get_model(api_key):
    genai.configure(api_key=api_key)
    
    # BÍ QUYẾT Ở ĐÂY: Chỉ dẫn AI cách dàn trang theo hàng và cột
    instruct = """
    Bạn là chuyên gia soạn thảo văn bản hành chính theo Nghị định 30/2020/NĐ-CP.
    Khi chuẩn hóa, hãy tuân thủ TUYỆT ĐỐI cấu trúc sau:
    
    1. ĐẦU VĂN BẢN (TRÌNH BÀY DẠNG 2 CỘT):
       - Cột trái: Tên cơ quan chủ quản (nếu có), Tên cơ quan ban hành (IN HOA), Số hiệu văn bản.
       - Cột phải: Quốc hiệu (IN HOA ĐẬM), Tiêu ngữ (Viết hoa chữ cái đầu, có gạch nối), Địa danh, ngày tháng năm.
       Ví dụ:
       CƠ QUAN CHỦ QUẢN             CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
       TÊN CƠ QUAN BAN HÀNH                Độc lập - Tự do - Hạnh phúc
       Số: .../TTr-...               Địa danh, ngày ... tháng ... năm ...

    2. TIÊU ĐỀ: Tên văn bản (IN HOA ĐẬM, Căn giữa), Trích yếu nội dung.
    3. NỘI DUNG: Căn cứ, các điều khoản rõ ràng.
    4. CUỐI VĂN BẢN (TRÌNH BÀY DẠNG 2 CỘT):
       - Cột trái: Nơi nhận (ghi chú rõ 'Như trên', 'Lưu VT').
       - Cột phải: Chức vụ người ký (IN HOA ĐẬM), Họ tên người ký.

    LƯU Ý: Không thêm lời chào hỏi của AI như 'Chào bạn', 'Dưới đây là...'. Chỉ trả về nội dung văn bản duy nhất.
    """
    
    available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else available[0]
    return genai.GenerativeModel(model_name=selected, system_instruction=instruct)

model_ai = get_model(user_api_key)

# --- 3. XỬ LÝ ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Dán nội dung:", height=400)
    process_btn = st.button("🚀 CHUẨN HÓA NGAY", type="primary", use_container_width=True)

with col2:
    if process_btn:
        input_data = ""
        if uploaded_file:
            doc = Document(uploaded_file)
            input_data = "\n".join([p.text for p in doc.paragraphs])
        else:
            input_data = user_text

        if input_data:
            with st.spinner("Đang chuẩn hóa..."):
                response = model_ai.generate_content(input_data, generation_config={"temperature": 0.1})
                st.session_state['res'] = response.text
                st.markdown(f"```\n{response.text}\n```") # Hiển thị dạng code để dễ copy đúng khoảng cách
                
                st.download_button("📥 Tải xuống Word", create_docx(response.text), "van_ban.docx", use_container_width=True)
