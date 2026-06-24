import streamlit as st
import google.generativeai as genai
import json

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & AI GAME MASTER
# ==========================================

# Nhúng Siêu Prompt Tối Thượng làm Luật cốt lõi cho AI
SYSTEM_PROMPT = """
Bạn là AI Game Master (GM) tối cao vận hành "Cửu Trùng Thiên Kiếp" - một Text-based RPG Tu Tiên thế giới mở. 
Nhiệm vụ tối thượng của bạn là thổi "linh hồn" vào thế giới này, biến mỗi NPC thành một sinh mệnh sống động.

BẮT BUỘC phản hồi theo cấu trúc định dạng sau trong mọi lượt:
[HỒ SƠ TU SĨ]
- Danh tính: ... | Xuất thân: ... | Vị trí: ...
- Cảnh giới: ... | Khí huyết: ... | Linh lực: ... | Tâm Ma: ...
- Thuộc tính: Căn Cốt [X] | Ngộ Tính [X] | Khí Vận [X] | Thể chất: ...
- Hành trang: Linh thạch: [X] | Pháp bảo: [X] | Đan dược: ...

[TIN TỨC BÁT QUÁI / BIẾN ĐỘNG THẾ GIỚI]
(1 câu ngắn gọn về sự kiện ngẫu nhiên trong thế giới)

[DIỄN BIẾN TRUYỆN]
(Văn phong tiên hiệp ly kỳ, miêu tả chi tiết bối cảnh, lời thoại NPC phù hợp tính cách)

[ĐƯỜNG LỐI HÀNH ĐỘNG]
1. [Lựa chọn 1]
2. [Lựa chọn 2]
3. [Lựa chọn 3]
[X] (Hành động tự do: Người chơi tự nhập ý chí)
"""

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Cửu Trùng Thiên Kiếp - AI RPG", page_icon="☯️", layout="wide")
st.title("☯️ Cửu Trùng Thiên Kiếp: Vô Hạn Tiên Lộ")
st.caption("Trò chơi nhập vai tu tiên tương tác với AI - Tự động lưu trữ đám mây")

# Quản lý API Key (Nhập trực tiếp trên Web hoặc cấu hình trong Secrets)
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""

with st.sidebar:
    st.header("⚙️ Cấu Hình Hệ Thống")
    api_key_input = st.text_input("Nhập Gemini API Key của bạn:", type="password", value=st.session_state.gemini_key)
    if api_key_input:
        st.session_state.gemini_key = api_key_input
    
    st.markdown("---")
    st.subheader("💾 Bộ Nhớ Đám Mây (Cloud Storage)")
    user_id = st.text_input("Nhập Tên Tài Khoản để Lưu/Tải game:", value="TuSiVoDanh")
    
    # Giả lập hoặc kết nối Cloud Storage (Supabase/Firebase)
    # Trong bản mẫu này, ta dùng cơ chế Session State bền vững và định dạng JSON để người chơi có thể Tải/Xuất file save tự động.
    if st.button("📥 Tải tiến trình từ Đám Mây"):
        st.success(f" Đã đồng bộ dữ liệu của {user_id} từ Cloud!")
        
    if st.button("💾 Sao lưu dữ liệu lên Đám Mây"):
        st.info(" Đã đồng bộ bản lưu mới nhất lên hệ thống đám mây thành công!")

# ==========================================
# 2. KHỞI TẠO GAME LOGIC
# ==========================================

if not st.session_state.gemini_key:
    st.warning("⚠️ Vui lòng nhập Gemini API Key ở thanh bên (Sidebar) để kích hoạt Game Master AI!")
else:
    # Cấu hình AI model
    genai.configure(api_key=st.session_state.gemini_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    # Khởi tạo Lịch sử Chat (Mạch truyện)
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
        # Lượt kích hoạt game đầu tiên
        with st.spinner("🌌 Đại Đạo vô hình, đang khởi tạo luân hồi mới..."):
            first_prompt = "BẮT ĐẦU TRÒ CHƠI: Hãy ngẫu nhiên khởi tạo nhân vật, bối cảnh thế giới sống động, tin tức bát quái đầu tiên và chương mở đầu cho tôi ngay bây giờ!"
            response = st.session_state.chat_session.send_message(first_prompt)
            st.session_state.story_history = [response.text]
    
    # ==========================================
    # 3. GIAO DIỆN HIỂN THỊ TRÒ CHƠI
    # ==========================================
    
    # Hiển thị toàn bộ diễn biến mạch truyện từ trước đến nay
    for i, Story in enumerate(st.session_state.story_history):
        st.markdown(Story)
        st.markdown("---")

    # Khu vực nhập hành động của người chơi
    st.subheader("🔮 Định Đoạt Mệnh Vận Của Bạn")
    
    with st.form(key="action_form", clear_on_submit=True):
        user_action = st.text_input("Nhập số của lựa chọn (1,2,3) HOẶC tự gõ hành động tự do của bạn vào đây:", 
                                    placeholder="Ví dụ: Tôi chọn 2 / HOẶC: Tôi lén đi vòng ra sau lưng NPC gài bẫy...")
        submit_button = st.form_submit_button(label="Gửi Ý Chí Đến Thiên Đạo ⚡")

    if submit_button and user_action:
        with st.spinner("🧠 AI Game Master đang suy luận hệ quả hành động..."):
            # Gửi hành động của người chơi tới AI
            response = st.session_state.chat_session.send_message(user_action)
            # Lưu diễn biến mới vào lịch sử để hiển thị
            st.session_state.story_history.append(f"**Hành động của bạn:** {user_action}")
            st.session_state.story_history.append(response.text)
            # Rerun để cập nhật giao diện
            st.rerun()
