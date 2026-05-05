from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from fpdf import FPDF
from PIL import Image, ImageOps
import io, os, uvicorn
from fastapi.responses import FileResponse

app = FastAPI()


class PREMIUM_PORTFOLIO(FPDF):
    def __init__(self, student_name, roll_no, theme_rgb, dept, year):
        super().__init__()
        self.student_name = student_name
        self.roll_no = roll_no
        self.theme_color = theme_rgb
        self.dept = dept
        self.year = year

    def header(self):
        if self.page_no() > 1:
            self.set_fill_color(*self.theme_color)
            self.rect(0, 0, 210, 10, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font('Helvetica', 'B', 8)
            self.set_y(0)
            self.cell(0, 10, f'GCU HYDERABAD | {self.dept.upper()} | {self.year}', 0, 0, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'{self.student_name} ({self.roll_no}) | Page {self.page_no()}', 0, 0, 'C')


def create_pdf(name, roll_no, subject, dept, year, submitted_to, theme_hex, contents):
    theme_rgb = tuple(int(theme_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    pdf = PREMIUM_PORTFOLIO(name, roll_no, theme_rgb, dept, year)
    pdf.set_auto_page_break(auto=True, margin=15)

    # FRONT PAGE
    pdf.add_page()
    pdf.set_fill_color(248, 249, 252)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_y(70)
    pdf.set_font("Helvetica", 'B', 30)
    pdf.set_text_color(*theme_rgb)
    pdf.cell(0, 15, "FINAL ASSIGNMENT", ln=True, align='C')

    pdf.set_font("Helvetica", '', 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, f"{subject}", ln=True, align='C')

    pdf.ln(30)
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 8, f"Name: {name}", ln=True, align='C')
    pdf.cell(0, 8, f"Roll No: {roll_no}", ln=True, align='C')
    pdf.cell(0, 8, f"Department: {dept}", ln=True, align='C')
    pdf.cell(0, 8, f"Submitted To: {submitted_to}", ln=True, align='C')

    # TASK PAGES
    total_tasks = len(contents) // 2

    for i in range(total_tasks):
        pdf.add_page()

        img1 = Image.open(io.BytesIO(contents[i*2])).convert("RGB")
        img2 = Image.open(io.BytesIO(contents[i*2+1])).convert("RGB")

        p1 = f"/tmp/c{i}.jpg"
        p2 = f"/tmp/o{i}.jpg"

        img1.save(p1)
        img2.save(p2)

        pdf.image(p1, x=10, y=30, w=90)
        pdf.image(p2, x=110, y=30, w=90)

        os.remove(p1)
        os.remove(p2)

    output_path = f"/tmp/Assignment_{roll_no.replace('-', '_')}.pdf"
    pdf.output(output_path)

    return output_path


@app.post("/generate-pdf")
async def generate_pdf(
    name: str = Form(...),
    roll_no: str = Form(...),
    subject: str = Form(...),
    dept: str = Form(...),
    year: str = Form(...),
    submitted_to: str = Form(...),
    theme: str = Form(...),
    files: List[UploadFile] = File(...)
):
    files.sort(key=lambda x: x.filename)
    contents = [await f.read() for f in files]

    pdf_path = create_pdf(
        name, roll_no, subject, dept, year, submitted_to, theme, contents
    )

    return FileResponse(pdf_path, filename=os.path.basename(pdf_path))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)