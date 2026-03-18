import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Chuẩn hóa văn bản AI", layout="wide")

# --- 2. THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.title("🔑 Cấu hình")
    user_api_key = st.text_input("Nhập Gemini API Key:", type="password")
    st.info("Lấy Key tại: aistudio.google.com/app/apikey")
    st.divider()
    st.caption("Phiên bản: 2.0 (Stable)")

# --- 3. GIAO DIỆN CHÍNH ---
st.markdown("<h1 style='text-align: center;'>📄 Chuẩn Hóa Văn Bản Hành Chính</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái để sử dụng!")
    st.stop()

# --- 4. KẾT NỐI AI (Xử lý lỗi 404 & NameError) ---
@st.cache_resource # Giúp app chạy nhanh hơn, không phải kết nối lại liên tục
def get_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Danh sách model dự phòng theo thứ tự ưu tiên
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        for m_name in models_to_try:
            try:
                m = genai.GenerativeModel(m_name)
                # Thử tạo một nội dung nhỏ để kiểm tra model có thực sự chạy không
                m.generate_content("test", generation_config={"max_output_tokens": 1})
                return m, m_name
            except:
                continue
        return None, None
    except Exception as err:
        return None, str(err)

model, model_info = get_model(user_api_key)

if model is None:
    st.error(f"❌ Không thể kết nối AI. Lỗi: {model_info}")
    st.info("Mẹo: Hãy kiểm tra API Key hoặc đảm bảo bạn đang ở vùng được hỗ trợ.")
    st.stop()
else:
    st.sidebar.success(f"✅ Đang dùng: {model_info}")

# --- 5. XỬ LÝ VĂN BẢN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Hoặc dán văn bản:", height=250)
    process_btn = st.button("🚀 Chuẩn hóa ngay", use_container_width=True, type="primary")

with col2:
    st.subheader("📥 Kết quả")
    
    # Lấy nội dung
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
                    prompt = f"Hãy chuẩn hóa đoạn văn bản sau đúng quy định hành chính (Nghị định 30/2020/NĐ-CP): \n\n{input_data}"
                    response = model.generate_content(prompt)
                    
                    st.markdown(f"""<div style="background:white; padding:15px; border-radius:5px; border:1px solid #ddd; color:black;">
                        {response.text.replace('\n', '<br>')}
                    </div>""", unsafe_allow_html=True)
                    
                    st.download_button("💾 Tải file .txt", response.text, "ket_qua.txt")
                except Exception as ex:
                    st.error(f"Lỗi khi tạo nội dung: {ex}")
        else:
            st.warning("Vui lòng nhập liệu!")
