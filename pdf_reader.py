import fitz  # PyMuPDF


def get_pdf_text(pdf_docs):
    text = ""


    for pdf in pdf_docs:
        pdf.seek(0)  # ✅ RESET POINTER


        doc = fitz.open(stream=pdf.read(), filetype="pdf")


        for page in doc:
            text += page.get_text()


    return text