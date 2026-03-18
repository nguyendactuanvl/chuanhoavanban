import streamlit as st
import google.generativeai as genai
from docx import Document
import io

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Chuẩn hóa văn bản hành chính AI",
    page_icon="📄",
    layout="wide"
)

# Giao diện Tiêu đề
st.markdown("<h1 style='text-align: center; color: #0D47A1;'>📄 Chuẩn Hóa Văn Bản Hành Chính</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Hỗ trợ theo Nghị định 30/2020/NĐ-CP & Quy chuẩn văn thư chuyên nghiệp</p>", unsafe_allow_html=True)
st.divider()

# --- CẤU HÌNH AI (THAY API KEY TẠI ĐÂY) ---
API_KEY = "MÃ_API_KEY_CỦA_BẠN" 

if API_KEY == "AIzaSyA00LWbDGphFpsvUWdQOVAJ6K_15ckEUKg":
    st.error("⚠️ Bạn chưa điền API Key vào code! Hãy lấy mã từ AI Studio và dán vào file app.py.")
else:
    try:
        genai.configure(api_key=API_KEY)
        # Sử dụng model flash phiên bản ổn định nhất
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Lỗi cấu hình AI: {e}")

# --- CÁC HÀM TIỆN ÍCH ---
def read_docx(file):
    try:
        doc = Document(file)
        full_text = [para.text for para in doc.paragraphs]
        return '\n'.join(full_text)
    except:
        return ""

# --- GIAO DIỆN CHÍNH (CHIA 2 CỘT) ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📤 Văn bản gốc")
    
    # 1. Tải file Word
    uploaded_file = st.file_uploader("Tải lên file Word (.docx)", type=["docx"])
    
    # 2. Ô nhập văn bản thủ công
    user_content = st.text_area("Hoặc dán nội dung văn bản vào đây:", height=300, placeholder="Nhập nội dung cần chuẩn hóa...")
    
    btn_run = st.button("🚀 Bắt đầu chuẩn hóa văn bản", use_container_width=True, type="primary")

with col2:
    st.subheader("📥 Kết quả chuẩn hóa")
    
    # Xác định nội dung đầu vào (Ưu tiên file tải lên)
    input_to_process = ""
    if uploaded_file:
        input_to_process = read_docx(uploaded_file)
    elif user_content:
        input_to_process = user_content

    if btn_run:
        if not input_to_process:
            st.warning("Vui lòng cung cấp nội dung bằng cách tải file hoặc dán văn bản!")
        else:
            with st.status("Đang phân tích và chuẩn hóa...", expanded=True) as status:
                try:
                    # Câu lệnh Prompt chi tiết để AI làm việc tốt hơn
                    prompt = f"""
                    Bạn là một chuyên gia về văn thư lưu trữ. Hãy chuẩn hóa đoạn văn bản sau đây 
                    đúng theo quy định của Nghị định 30/2020/NĐ-CP về công tác văn thư. 
                    Yêu cầu: Sửa lỗi chính tả, câu cú, cách trình bày, thể thức văn bản hành chính.
                    
                    NỘI DUNG CẦN CHUẨN HÓA:
                    ---
                    {input_to_process}
                    ---
                    """
                    
                    response = model.generate_content(prompt)
                    status.update(label="Đã hoàn thành!", state="complete", expanded=False)
                    
                    # Hiển thị kết quả trong khung chuyên nghiệp
                    st.success("Kết quả chuẩn hóa:")
                    st.markdown(f"""
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #E0E0E0; color: #333; line-height: 1.6; font-family: 'Times New Roman', serif;">
                        {response.text.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Nút tải xuống
                    st.download_button(
                        label="💾 Tải kết quả về máy (.txt)",
                        data=response.text,
                        file_name="van_ban_da_chuan_hoa.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi kết nối AI: {e}")
                    st.info("Mẹo: Hãy kiểm tra lại API Key hoặc thử tạo một Key mới trên AI Studio.")
    else:
        st.info("Kết quả chuẩn hóa sẽ hiển thị tại đây.")

# Chân trang
st.divider()
st.caption("Ứng dụng được phát triển bởi Nguyễn Đắc Tuấn - Hỗ trợ chuẩn hóa văn bản tự động.")
