import re

def clean_resume_text(text):
    """
    Cleans resume text while preserving line structure.
    """

    if not text:
        return ""

    # keep lines
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:

        line = line.lower()

        # remove bullets
        line = re.sub(r'[•➢►●▪]', ' ', line)

        # remove long separators
        line = re.sub(r'[_\-]{2,}', ' ', line)

        # remove unwanted characters (keep @ and .)
        line = re.sub(r'[^a-z0-9@.+# ]', ' ', line)

        # remove extra spaces
        line = re.sub(r'\s+', ' ', line).strip()

        if line:  # keep non-empty lines
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# test
if __name__ == "__main__":
    from resume_parser import extract_text_from_pdf

    raw_text = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    cleaned_text = clean_resume_text(raw_text)

    print("\n===== CLEANED TEXT =====\n")
    print(cleaned_text[:1500])
