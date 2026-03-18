import streamlit as st
import google.generativeai as genai
from docx import Document

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide")

# CSS để giả lập một tờ giấy A4 trên Web, giúp thầy dễ quét khối để Copy
st.markdown("""
    <style>
    .to-giay-a4 {
        background-color: white;
        width: 100%;
        padding: 40px;
        color: black;
        font-family: 'Times New Roman', Times, serif;
        font-size: 14pt;
        line-height: 1.5;
        border: 1px solid #ccc;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        min-height: 800px;
        margin: auto;
    }
    /* Giữ nguyên định dạng bảng khi copy */
    table { border-collapse: collapse; width: 100%; border: none !important; }
    td { border: none !important; vertical-align: top; }
    b, strong { font-weight: bold !important; }
    i, em { font-style: italic !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Cấu hình App")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    if st.button("🔄 Làm mới trang"):
        st.rerun()
    st.info("Mẹo: Sau khi chuẩn hóa, hãy bôi đen toàn bộ 'tờ giấy' bên phải và dán vào Word.")

st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Thầy vui lòng nhập API Key ở bên trái!")
    st.stop()

# --- 2. KHỞI TẠO AI (BÊ NGUYÊN BÍ KÍP CỦA THẦY) ---
@st.cache_resource
def get_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Quét lấy model chuẩn
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        
        # ĐÂY LÀ ĐOẠN QUAN TRỌNG NHẤT: Ép AI trả về HTML cực chuẩn
        instruct = """
        Bạn là chuyên gia văn thư. Hãy chuẩn hóa văn bản theo Nghị định 187/2025/NĐ-CP.
        YÊU CẦU: 
        1. TRẢ VỀ DUY NHẤT MÃ HTML (KHÔNG bọc trong dấu ```html).
        2. Phần đầu và cuối văn bản BẮT BUỘC dùng thẻ <table> để chia cột.
        3. Sử dụng thẻ <b> cho in đậm, <i> cho in nghiêng.
        4. Căn lề đoạn văn bằng <div style="text-align: justify; text-indent: 1.27cm;">.
        5. Font chữ mặc định: Times New Roman, cỡ 14pt.
        """
        return genai.GenerativeModel(model_name=name, system_instruction=instruct)
    except Exception as e:
        return str(e)

ai = get_model(user_api_key)

# --- 3. GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns([1, 1.2]) # Cho cột kết quả rộng hơn một chút

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Dán nội dung:", height=450)
    process_btn = st.button("🚀 BẮT ĐẦU CHUẨN HÓA", type="primary", use_container_width=True)

with col2:
    st.subheader("📥 Kết quả (Bản thảo chuẩn)")
    input_data = ""
    if uploaded_file:
        doc_in = Document(uploaded_file)
        input_data = "\n".join([p.text for p in doc_in.paragraphs])
    elif user_text:
        input_data = user_text

    if process_btn:
        if input_data:
            with st.spinner("Đang dàn trang văn bản..."):
                try:
                    response = ai.generate_content(input_data)
                    # Hiển thị trong khung trắng giả lập A4
                    st.markdown(f'<div class="to-giay-a4">{response.text}</div>', unsafe_allow_html=True)
                    
                    st.success("✅ Đã xong! Thầy hãy bôi đen nội dung trên và dán vào Word.")
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")
