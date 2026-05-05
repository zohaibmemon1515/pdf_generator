import streamlit as st
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

INSTANCE_ID = os.getenv("INSTANCE_ID")
TOKEN = os.getenv("INSTANCE_TOKEN")


def send_to_whatsapp(file_path, phone_number, student_name):
    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')

    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/document"

    custom_caption = (
        f"Salam,\n\n"
        f"Here is your final assignment PDF for {student_name}.\n\n"
        f"Best Regards,\nZohaib Memon"
    )

    payload = {
        "token": TOKEN,
        "to": phone_number,
        "filename": os.path.basename(file_path),
        "document": f"data:application/pdf;base64,{file_data}",
        "caption": custom_caption
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    return requests.post(url, data=payload, headers=headers).json()


# ================= UI SETUP =================
st.set_page_config(page_title="GCUH Assignment Agent", layout="wide", page_icon="💎")

st.markdown("""
<style>
.main { background-color: #f5f7f9; }

.stButton>button {
    width: 100%;
    border-radius: 8px;
    height: 3em;
    background-color: #1e2d50;
    color: white;
    font-weight: bold;
}

.instruction-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #d4af37;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    height: 100%;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align:center;color:#1e2d50;'>💎 GCUH FINAL ASSIGNMENT AGENT</h1>", unsafe_allow_html=True)


# ================= INSTRUCTIONS =================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="instruction-card">
    <b>📸 1. Order Matters</b><br>
    Files ko alphabet order me upload karo:<br>
    1. Code<br>
    2. Output
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="instruction-card">
    <b>📞 2. WhatsApp Format</b><br>
    Bina "+" likho:<br>
    <code>923001234567</code>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="instruction-card">
    <b>📂 3. Categories</b><br>
    Basics → Arrays → Loops → Functions
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ================= SIDEBAR =================
with st.sidebar:
    st.header("👤 Student Profile")

    name = st.text_input("Full Name", "Hafiz Zohaib Memon")
    roll = st.text_input("Roll Number", "BSAI-2026-115")
    dept = st.text_input("Department", "Computer Science & AI")
    year = st.text_input("Academic Year", "2026")
    subject = st.text_input("Subject", "Programming Fundamentals")
    submitted = st.text_input("Submitted To", "Mam Sana Shaikh")
    phone = st.text_input("WhatsApp Number", "923000000000")
    theme = st.color_picker("Theme Color", "#1E2D50")


# ================= UPLOAD =================
files = st.file_uploader(
    "Upload All Screenshots (Code + Output pairs)",
    accept_multiple_files=True,
    type=['png', 'jpg', 'jpeg']
)


# ================= ACTION =================
if st.button("🚀 GENERATE & SEND TO WHATSAPP"):

    if not files or len(files) % 2 != 0:
        st.error("⚠ Upload even number of files (Code + Output pairs)")
    else:
        with st.spinner("Generating PDF & Sending..."):

            files_data = [
                ("files", (f.name, f.getvalue(), f.type)) for f in files
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

            try:
                res = requests.post(
                    "https://memonz-pdf-generator.hf.space/generate-pdf",
                    data=payload,
                    files=files_data
                )

                if res.status_code == 200:
                    pdf_path = "temp.pdf"

                    with open(pdf_path, "wb") as f:
                        f.write(res.content)

                    wa_res = send_to_whatsapp(pdf_path, phone, name)

                    if wa_res.get("sent") == "true":
                        st.success("✅ PDF successfully sent to WhatsApp!")
                        st.balloons()
                    else:
                        st.error(f"WhatsApp Error: {wa_res}")

                else:
                    st.error("❌ Backend error - check FastAPI")

            except Exception as e:
                st.error(f"Connection Error: {e}")