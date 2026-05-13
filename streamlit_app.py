import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ================= UI CONFIG =================
st.set_page_config(
    page_title="GCUH Assignment Agent",
    layout="wide",
    page_icon="💎"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

.main {
    background: #f4f7fb;
}

.block-container {
    padding-top: 2rem;
}

.stButton>button {
    width: 100%;
    height: 3.2em;
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg,#1E2D50,#324b81);
    color: white;
    font-size: 17px;
    font-weight: 700;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.01);
}

.card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border-left: 5px solid #D4AF37;
    height: 100%;
}

.title {
    text-align: center;
    color: #1E2D50;
    font-size: 42px;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    color: #5f6368;
    margin-bottom: 25px;
}

.upload-box {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='title'>💎 GCUH FINAL ASSIGNMENT AGENT</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='subtitle'>Generate Premium Assignment PDF Instantly</div>",
    unsafe_allow_html=True
)

# ================= INSTRUCTIONS =================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
    <h4>📸 Upload Order</h4>
    Code screenshot ke baad output screenshot upload karo.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
    <h4>🖼 Supported Files</h4>
    PNG, JPG, JPEG supported hain.
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
    <h4>⚡ Fast PDF Generation</h4>
    Automatic premium formatted assignment PDF.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:

    st.markdown("## 👤 Student Information")

    name = st.text_input("Full Name", "Hafiz Zohaib Memon")

    roll = st.text_input("Roll Number", "BSAI-2026-115")

    dept = st.text_input("Department", "Computer Science & AI")

    year = st.text_input("Academic Year", "2026")

    subject = st.text_input("Subject", "Programming Fundamentals")

    submitted = st.text_input("Submitted To", "Mam Sana Shaikh")

    theme = st.color_picker("Theme Color", "#1E2D50")

# ================= FILE UPLOAD =================
st.markdown("<div class='upload-box'>", unsafe_allow_html=True)

files = st.file_uploader(
    "📂 Upload All Code + Output Screenshots",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= GENERATE PDF =================
if st.button("🚀 GENERATE PDF"):

    if not files:
        st.error("⚠ Please upload screenshots first.")

    elif len(files) % 2 != 0:
        st.error("⚠ Upload even number of screenshots (Code + Output pairs).")

    else:

        with st.spinner("Generating Premium PDF..."):

            try:

                files_data = [
                    ("files", (f.name, f.getvalue(), f.type))
                    for f in files
                ]

                payload = {
                    "name": name,
                    "roll_no": roll,
                    "subject": subject,
                    "dept": dept,
                    "year": year,
                    "submitted_to": submitted,
                    "theme": theme
                }

                response = requests.post(
                    "https://memonz-pdf-generator.hf.space/generate-pdf",
                    data=payload,
                    files=files_data
                )

                if response.status_code == 200:

                    pdf_bytes = response.content

                    st.success("✅ PDF Generated Successfully!")

                    st.download_button(
                        label="⬇ DOWNLOAD PDF",
                        data=pdf_bytes,
                        file_name=f"{name}_Assignment.pdf",
                        mime="application/pdf"
                    )

                    st.balloons()

                else:
                    st.error("❌ Backend Error - FastAPI response failed")

            except Exception as e:
                st.error(f"❌ Connection Error: {e}")