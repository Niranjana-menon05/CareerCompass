import pdfplumber

def extract_text_from_pdf(pdf_path):
    """
    Reads a PDF resume and extracts all text from it.
    Returns the extracted text as a single string.
    """

    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:              # avoid None pages
                    text += page_text + "\n"

        return text

    except Exception as e:
        print("Error reading PDF:", e)
        return None


# Test the function directly
if __name__ == "__main__":
    file_path = "sample_resumes/sample_resume.pdf"
    resume_text = extract_text_from_pdf(file_path)

    print("\n===== EXTRACTED RESUME TEXT =====\n")
    print(resume_text)
