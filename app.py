import streamlit as st
import google.generativeai as genai
from docx import Document

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide", page_icon="📝")

# CSS để giao diện giống AI Studio hơn (bo tròn, màu sắc chuyên nghiệp)
st.markdown("""
    <style>
    .stTextArea textarea { font-family: 'Times New Roman', serif; font-size: 16px; }
    .result-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; color: #333; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Cấu hình App")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")
    st.divider()
    st.write("👨‍🏫 **Tác giả:** Nguyễn Đắc Tuấn")

st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tự động sửa lỗi chính tả, trình bày theo Nghị định 30/2020/NĐ-CP</p>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái để bắt đầu!")
    st.stop()

# --- CẤU HÌNH MODEL (BÍ QUYẾT GIỐNG AI STUDIO) ---
@st.cache_resource
def load_ai_studio_model(api_key):
    try:
        genai.configure(api_key=api_key)
        
        # ĐÂY LÀ PHẦN QUAN TRỌNG: Đưa nội dung từ mục 'System Instructions' của bạn vào đây
        system_instruction = """
        Bạn là một chuyên gia văn thư và pháp chế tại Việt Nam.
        Nhiệm vụ: Chuẩn hóa mọi văn bản hành chính được cung cấp.
        Quy tắc:
        1. Tuân thủ tuyệt đối Nghị định 30/2020/NĐ-CP về thể thức văn bản.
        2. Viết hoa đúng các danh từ riêng, chức vụ, đơn vị hành chính.
        3. Chỉnh sửa câu văn mạch lạc, trang trọng, chuyên nghiệp.
        4. Định dạng đầu ra sạch sẽ, rõ ràng các mục: Quốc hiệu, Tiêu ngữ, Tên văn bản, Nội dung...
        """
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction, # Kích hoạt bộ não chuyên gia
            generation_config={
                "temperature": 0.2, # Giảm sáng tạo để tăng độ chính xác văn bản
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }
        )
        return model
    except Exception as e:
        return str(e)

ai_model = load_ai_studio_model(user_api_key)

if isinstance(ai_model, str):
    st.error(f"Lỗi kết nối: {ai_model}")
    st.stop()

# --- XỬ LÝ DỮ LIỆU ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file Word", type=["docx"])
    user_text = st.text_area("Hoặc dán nội dung vào đây:", height=350, placeholder="Dán văn bản hành chính cần sửa...")
    
    if st.button("🚀 BẮT ĐẦU CHUẨN HÓA", type="primary", use_container_width=True):
        input_data = ""
        if uploaded_file:
            doc = Document(uploaded_file)
            input_data = "\n".join([p.text for p in doc.paragraphs])
        elif user_text:
            input_data = user_text
            
        if input_data:
            with st.spinner("Đang chuẩn hóa theo Nghị định 30..."):
                try:
                    # Gửi yêu cầu cho AI
                    response = ai_model.generate_content(input_data)
                    st.session_state['result'] = response.text
                except Exception as ex:
                    st.error(f"Lỗi xử lý: {ex}")
        else:
            st.warning("Vui lòng nhập nội dung!")

with col2:
    st.subheader("📥 Kết quả chuyên gia")
    if 'result' in st.session_state:
        # Hiển thị kết quả trong khung đẹp
        st.markdown(f'<div class="result-box">{st.session_state["result"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.download_button("💾 Tải file kết quả (.txt)", st.session_state['result'], "van_ban_chuan_hoa.txt")
    else:
        st.info("Kết quả sẽ hiển thị tại đây sau khi bạn nhấn nút chuẩn hóa.")
