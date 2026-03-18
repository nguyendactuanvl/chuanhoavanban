import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# --- 1. CẤU HÌNH GIAO DIỆN (GIỐNG AI STUDIO) ---
st.set_page_config(page_title="Chuẩn hóa văn bản hành chính", layout="wide", page_icon="📝")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
    .main-content {
        font-family: 'Times New Roman', serif;
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        color: black;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Cấu hình")
    user_api_key = st.text_input("Dán Gemini API Key:", type="password")
    st.info("Lấy mã tại: aistudio.google.com/app/apikey")
    st.divider()
    if st.button("🔄 Làm mới ứng dụng"):
        st.rerun()

st.markdown("<h1 style='text-align: center; color: #1565C0;'>📄 Chuẩn Hóa Văn Bản Hành Chính AI</h1>", unsafe_allow_html=True)

if not user_api_key:
    st.warning("👈 Vui lòng nhập API Key ở bên trái để bắt đầu!")
    st.stop()

# --- 2. LINH HỒN CỦA APP (PROMPT TỪ AI STUDIO CỦA THẦY) ---
@st.cache_resource
def load_model(api_key):
    try:
        genai.configure(api_key=api_key)
        
        # Nội dung này em bê nguyên từ ảnh thầy chụp sang
        instruct = """
Bạn là một chuyên gia ngôn ngữ học và chuyên gia văn thư lưu trữ tại Việt Nam.
Nhiệm vụ của bạn là:
1. Sửa lỗi chính tả, ngữ pháp, dấu câu và cải thiện văn phong cho đoạn văn bản gốc.
2. Chuẩn hóa đoạn văn bản theo đúng quy định về thể thức văn bản hành chính của Ban Quản lý dự án Đầu tư xây dựng khu vực 1 thành phố Huế và cập nhật theo Nghị định 187/2025/NĐ-CP.

YÊU CẦU VỀ THỂ THỨC (BẮT BUỘC ÁP DỤNG THEO NGHỊ ĐỊNH 187/2025/NĐ-CP):
- Trình bày kết quả dưới dạng HTML để đảm bảo định dạng chính xác khi copy sang Google Docs/Word.
- Font chữ: Times New Roman.
- Cỡ chữ nội dung chính: 14pt.
- Canh lề nội dung chính: Canh đều hai bên (justify), lùi đầu dòng (text-indent) 1.27cm, khoảng cách dòng (line-height) 1.5, khoảng cách đoạn tối thiểu 6pt. Bắt buộc sử dụng thẻ <div style="text-align: justify; text-indent: 1.27cm; margin-top: 6pt; margin-bottom: 6pt; line-height: 1.5;"> cho mỗi đoạn văn nội dung.
- Bắt buộc dùng bảng HTML không viền cho phần đầu và phần cuối văn bản.

MẪU PHẦN ĐẦU VĂN BẢN (TABLE HTML):
<table style="width: 100%; border: none; font-family: 'Times New Roman', serif;">
  <tr>
    <td style="width: 40%; text-align: center; vertical-align: top; font-size: 13pt;">
      UBND THÀNH PHỐ HUẾ<br>
      <b>BAN QUẢN LÝ DỰ ÁN<br>ĐẦU TƯ XÂY DỰNG KHU VỰC 1</b><br>
      <hr style="width: 40%; border-top: 1px solid black; margin: 5px auto;">
      Số: .../QĐ-BQLKV1
    </td>
    <td style="width: 60%; text-align: center; vertical-align: top;">
      <b style="font-size: 13pt;">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</b><br>
      <b style="font-size: 14pt;">Độc lập - Tự do - Hạnh phúc</b><br>
      <hr style="width: 50%; border-top: 1px solid black; margin: 5px auto;">
      <i style="font-size: 14pt;">Huế, ngày ... tháng ... năm 2026</i>
    </td>
  </tr>
</table>

MẪU PHẦN CUỐI VĂN BẢN (TABLE HTML):
<table style="width: 100%; border: none; font-family: 'Times New Roman', serif;">
  <tr>
    <td style="width: 50%; vertical-align: top;">
      <b style="font-size: 12pt; font-style: italic;">Nơi nhận:</b><br>
      <div style="font-size: 11pt; line-height: 1.2;">
      - Như trên;<br>
      - Lưu: VT, TCHC.
      </div>
    </td>
    <td style="width: 50%; text-align: center; vertical-align: top; font-size: 14pt;">
      <b>GIÁM ĐỐC</b><br>
      <i>(Chữ ký, dấu)</i><br><br><br><br>
      <b>Nguyễn Trần Nhật Tuấn</b>
    </td>
  </tr>
</table>

Chỉ trả về mã HTML đã được chuẩn hóa, không giải thích thêm. KHÔNG bọc block code markdown.
        """
        # Đã thêm models/ để sửa lỗi 404 cho thầy
        model = genai.GenerativeModel(
            model_name='models/gemini-1.5-flash',
            system_instruction=instruct
        )
        return model
    except Exception as e:
        return str(e)

ai_model = load_model(user_api_key)

# --- 3. GIAO DIỆN XỬ LÝ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Văn bản gốc")
    uploaded_file = st.file_uploader("Tải file .docx", type=["docx"])
    user_text = st.text_area("Hoặc dán nội dung tại đây:", height=400)
    process_btn = st.button("🚀 BẮT ĐẦU CHUẨN HÓA", type="primary", use_container_width=True)

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
            with st.spinner("Đang chuẩn hóa theo đúng AI Studio..."):
                try:
                    response = ai_model.generate_content(input_data)
                    st.session_state['output'] = response.text
                except Exception as ex:
                    st.error(f"Lỗi: {ex}")
        else:
            st.warning("Vui lòng nhập nội dung!")

    if 'output' in st.session_state:
        # Hiển thị HTML để giữ định dạng bảng 2 cột
        st.markdown(f'<div class="main-content">{st.session_state["output"]}</div>', unsafe_allow_html=True)
        st.divider()
        st.success("💡 Thầy hãy bôi đen kết quả trên, Copy và Dán vào Word/Google Docs để giữ đúng bảng 2 cột.")
        st.link_button("🌐 Mở Google Docs mới", "https://docs.new")
