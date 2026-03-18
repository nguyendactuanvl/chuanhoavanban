import streamlit as st
import google.generativeai as genai
from docx import Document

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Chuẩn hóa văn bản AI", layout="wide")

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")

st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- HÀM KHỞI TẠO AI THÔNG MINH (TỰ QUÉT MODEL) ---
@st.cache_resource
def get_working_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # 1. Lấy danh sách tất cả model khả dụng trong tài khoản của thầy
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            return None, "Tài khoản không có model nào hỗ trợ tạo nội dung."

        # 2. Ưu tiên chọn các bản Flash 1.5 hoặc Pro
        target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        selected = models[0] # Mặc định lấy cái đầu tiên nếu không tìm thấy cái ưu tiên
        
        for t in target_models:
            if t in models:
                selected = t
                break
        
        # 3. Chỉ định System Instruction (Thầy sửa nội dung trong ngoặc này cho giống AI Studio)
        instruct = "Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản theo Nghị định 30/2020/NĐ-CP. Sửa lỗi chính tả, viết hoa và trình bày trang trọng."
        
        model = genai.GenerativeModel(model_name=selected, system_instruction=instruct)
        return model, selected
    except Exception as e:
        return None, str(e)

# Chạy khởi tạo
ai_model, model_name = get_working_model(user_api_key)

if ai_model is None:
    st.error(f"❌ Lỗi: {model_name}")
    st.stop()
else:
    st.sidebar.success(f"✅ Đang dùng: {model_name}")

# --- GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Hoặc dán nội dung:", height=300)
    btn = st.button("🚀 CHUẨN HÓA NGAY", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả")
    input_data = ""
    if uploaded_file:
        doc = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc.paragraphs])
    elif user_text:
        input_data = user_text

    if btn:
        if input_data:
            with st.spinner("Đang xử lý..."):
                try:
                    # Giao tiếp với AI
                    response = ai_model.generate_content(input_data, generation_config={"temperature": 0.1})
                    st.success("Hoàn thành!")
                    st.write(response.text)
                except Exception as ex:
                    st.error(f"Lỗi khi tạo nội dung: {str(ex)}")
        else:
            st.warning("Vui lòng nhập liệu!")
