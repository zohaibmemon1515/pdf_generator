import streamlit as st
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

INSTANCE_ID = os.getenv("INSTANCE_ID")
TOKEN = os.getenv("INSTANCE_TOKEN")


def send_to_whatsapp(file_path, phone, name):
    with open(file_path, "rb") as f:
        file_data = base64.b64encode(f.read()).decode()

    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/document"

    payload = {
        "token": TOKEN,
        "to": phone,
        "filename": "Assignment.pdf",
        "document": f"data:application/pdf;base64,{file_data}",
        "caption": f"📄 Assignment for {name}"
    }

    return requests.post(url, data=payload).json()


st.title("💎 GCU Assignment Generator")

name = st.text_input("Name")
roll = st.text_input("Roll No")
subject = st.text_input("Subject")
dept = st.text_input("Department")
year = st.text_input("Year")
submitted = st.text_input("Submitted To")
phone = st.text_input("WhatsApp (923xxxxxxxxx)")
theme = st.color_picker("Theme", "#1E2D50")

files = st.file_uploader(
    "Upload Images (Code + Output pairs)",
    accept_multiple_files=True
)

if st.button("🚀 Generate & Send"):
    if len(files) % 2 != 0:
        st.error("Upload even number of files (code + output)")
    else:
        with st.spinner("Processing..."):
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

            res = requests.post(
                "https://memonz-pdf-generator.hf.space/generate-pdf",
                data=payload,
                files=files_data
            )

            if res.status_code == 200:
                pdf_path = "temp.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(res.content)

                wa = send_to_whatsapp(pdf_path, phone, name)

                if wa.get("sent", "false") == "true":
                    st.success("✅ Sent to WhatsApp!")
                else:
                    st.error(wa)
            else:
                st.error("Backend error")