import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import PyPDF2
import io
from collections import Counter
def type_of_pdf(file_name):
    with pdfplumber.open(file_name) as pdf:
        NumPages=6
        count=0
        cid=False
        try:
            for i in range(2, NumPages):
                text = pdf.pages[i].extract_text()
                try:
                    if 'cid:' in (Counter(text.split()).most_common())[0][0]:
                        count += 1
                    if count >2:
                        cid = True
                except:
                    pass
                if text=='':
                    count+=1
        except:
            pass

    if count>2 or cid==True:
        images = convert_from_path(file_name)
        pdf_writer = PyPDF2.PdfFileWriter()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        for image in images:
            page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf',config='-c tessedit_create_pdf=1')
            pdf = PyPDF2.PdfFileReader(io.BytesIO(page))
            pdf_writer.addPage(pdf.getPage(0))

        with open(file_name, "wb") as f:
            pdf_writer.write(f)

