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
    response = requests.post(url, data=payload, headers=headers)
    return response.json()

st.set_page_config(page_title="GCUH Assignment Agent", layout="wide", page_icon="💎")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1e2d50; color: white; }
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

st.markdown('<h1 style="text-align: center; color: #1e2d50;">💎 GCUH FINAL ASSIGNMENT AGENT</h1>', unsafe_allow_html=True)

# --- INSTRUCTIONS SECTION ---
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="instruction-card"><b>📸 1. Order Matters</b><br>Files ko alphabet order mein rakhein.<br>1. Task Code<br>2. Task Output</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="instruction-card"><b>📞 2. WhatsApp Format</b><br>Bina "+" ke likhein.<br>Example: <code>923001234567</code></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="instruction-card"><b>📂 3. Categories</b><br>Basics (1-17), Arrays (18-25), Loops & Functions (26-48).</div>', unsafe_allow_html=True)

st.markdown("---")

with st.sidebar:
    st.header("👤 Student Profile")
    user_name = st.text_input("Full Name", "Hafiz Zohaib Memon")
    user_roll = st.text_input("Roll Number", "BSAI-2026-115")
    user_dept = st.text_input("Department", "Computer Science & AI")
    user_year = st.text_input("Academic Year", "2026")
    user_sub = st.text_input("Subject Name", "Programming Fundamentals")
    user_to = st.text_input("Submitted To", "Mam Sana Shaikh")
    whatsapp_num = st.text_input("WhatsApp (923xxxxxxxxx)", "923000000000")
    theme_color = st.color_picker("Pick Accent Color", "#1E2D50")

uploaded_files = st.file_uploader("Upload All Screenshots", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if st.button("🚀 GENERATE & SEND TO WHATSAPP"):
    if not uploaded_files or len(uploaded_files) % 2 != 0:
        st.error("Please upload an even number of files (1 Code + 1 Output per task).")
    elif not whatsapp_num:
        st.error("Please provide a WhatsApp number.")
    else:
        with st.spinner("Processing PDF and Sending..."):
            files_data = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
            payload = {
                "name": user_name, "roll_no": user_roll, "subject": user_sub,
                "dept": user_dept, "year": user_year, "submitted_to": user_to, "theme": theme_color
            }
            try:
                res = requests.post("https://memonz-pdf-generator.hf.space/generate-pdf", data=payload, files=files_data)
                if res.status_code == 200:
                    pdf_filename = res.json()['filename']
                    wa_res = send_to_whatsapp(pdf_filename, whatsapp_num, user_name)
                    if wa_res.get('sent') == 'true':
                        st.success(f"✅ PDF sent to {whatsapp_num}!")
                        st.balloons()
                    else:
                        st.error(f"WhatsApp Error: {wa_res}")
                else:
                    st.error("Check if backend.py is running.")
            except Exception as e:
                st.error(f"Connection Error: {e}")