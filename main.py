from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from fpdf import FPDF
import os
from PIL import Image, ImageOps
import io
import uvicorn

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
            self.set_font('Arial', 'B', 8)
            self.set_y(0)
            self.cell(0, 10, f'GCU HYDERABAD | {self.dept.upper()} | {self.year}', 0, 0, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'{self.student_name} ({self.roll_no}) | Page {self.page_no()}', 0, 0, 'C')

def create_final_pdf(name, roll_no, subject, dept, year, submitted_to, theme_hex, contents):
    h = theme_hex.lstrip('#')
    theme_rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    pdf = PREMIUM_PORTFOLIO(name, roll_no, theme_rgb, dept, year)
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- FRONT PAGE ---
    pdf.add_page()
    pdf.set_fill_color(248, 249, 252)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_fill_color(*theme_rgb)
    pdf.rect(0, 0, 6, 297, 'F')

    pdf.set_y(70)
    pdf.set_font("Arial", 'B', 40)
    pdf.set_text_color(*theme_rgb)
    pdf.cell(0, 15, "FINAL", ln=True, align='C')
    pdf.cell(0, 15, f"ASSIGNMENT {year.split()[-1]}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"COURSE: {subject.upper()}", ln=True, align='C')
    
    pdf.ln(45)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(40, 175, 130, 70, 'DF')
    pdf.set_fill_color(*theme_rgb)
    pdf.rect(40, 175, 130, 2, 'F')

    pdf.set_xy(47, 185)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(*theme_rgb)
    pdf.cell(0, 8, f"STUDENT: {name.upper()}", ln=True)
    pdf.set_x(47)
    pdf.cell(0, 8, f"ROLL NO: {roll_no}", ln=True)
    pdf.set_x(47)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, f"DEPARTMENT: {dept.upper()}", ln=True)
    pdf.set_x(47)
    pdf.cell(0, 8, "INSTITUTE: GCU HYDERABAD", ln=True)
    pdf.set_x(47)
    pdf.cell(0, 8, f"SUBMITTED TO: {submitted_to.upper()}", ln=True)

    # --- CATEGORY SETUP ---
    # 17 Basics, 8 Arrays (17+8=25), 10 Loops (25+10=35), 4 Do-While (35+4=39), 9 Func (39+9=48)
    categories = [
        (17, "BASICS & CONDITIONS"),
        (25, "ARRAYS"),
        (35, "LOOPS (FOR)"),
        (39, "DO-WHILE LOOPS"),
        (48, "FUNCTIONS")
    ]

    total_tasks = len(contents) // 2
    for t_idx in range(total_tasks):
        # Category Labeling
        current_cat = "LABORATORY WORK"
        for limit, cat_name in categories:
            if t_idx < limit:
                current_cat = cat_name
                break

        # 2 Tasks per page logic
        if t_idx % 2 == 0:
            pdf.add_page()
            y_start = 20
        else:
            y_start = 150

        # Header Bar for Task
        pdf.set_fill_color(242, 244, 247)
        pdf.rect(10, y_start, 190, 10, 'F')
        pdf.set_xy(15, y_start)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(*theme_rgb)
        pdf.cell(0, 10, f"TASK #{t_idx + 1:02} | {current_cat}")

        # Image Placement
        img_code = ImageOps.expand(Image.open(io.BytesIO(contents[t_idx*2])).convert("RGB"), border=2, fill=(220, 220, 220))
        img_out = ImageOps.expand(Image.open(io.BytesIO(contents[t_idx*2+1])).convert("RGB"), border=2, fill=(220, 220, 220))
        
        p1, p2 = f"c_{t_idx}.jpg", f"o_{t_idx}.jpg"
        img_code.save(p1, quality=85); img_out.save(p2, quality=85)
        
        pdf.image(p1, x=10, y=y_start + 15, w=92)
        pdf.image(p2, x=108, y=y_start + 15, w=92)
        
        os.remove(p1); os.remove(p2)

    output_path = f"Assignment_{roll_no.replace('-', '_')}.pdf"
    pdf.output(output_path)
    return output_path

@app.post("/generate-pdf")
async def handle_pdf(
    name: str = Form(...), roll_no: str = Form(...), 
    subject: str = Form(...), dept: str = Form(...),
    year: str = Form(...), submitted_to: str = Form(...),
    theme: str = Form(...), files: List[UploadFile] = File(...)
):
    files.sort(key=lambda x: x.filename)
    byte_data = [await f.read() for f in files]
    pdf_filename = create_final_pdf(name, roll_no, subject, dept, year, submitted_to, theme, byte_data)
    return {"status": "Success", "filename": pdf_filename}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)