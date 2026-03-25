import re
import spacy
from skill_db import TECH_SKILLS, SOFT_SKILLS

# load NLP model
nlp = spacy.load("en_core_web_sm")


# ---------------- NAME ----------------
from skill_db import TECH_SKILLS

def looks_like_skill_line(line):
    for skill in TECH_SKILLS:
        if skill.lower() in line.lower():
            return True
    return False


def extract_name(text):

    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    # find first contact line
    contact_index = None
    for i, line in enumerate(lines[:20]):
        if "@" in line or sum(c.isdigit() for c in line) >= 5:
            contact_index = i
            break

    if contact_index is not None:

        # search upward from contact info
        for line in reversed(lines[:contact_index]):

            words = line.split()

            if 1 <= len(words) <= 3 and all(w.isalpha() for w in words):

                blacklist = [
                    "summary","profile","experience","skills",
                    "education","details","objective"
                ]

                # reject headings
                if any(b in line.lower() for b in blacklist):
                    continue

                # reject tech stack lines
                if looks_like_skill_line(line):
                    continue

                return line.title()

    # fallback to spacy
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.title()

    return None



# ---------------- EMAIL ----------------
def extract_email(text):
    pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


# ---------------- PHONE ----------------
def extract_phone(text):
    pattern = r'(\+?\d[\d\-\(\) ]{8,}\d)'
    match = re.search(pattern, text)
    return match.group(0) if match else None


# ---------------- SKILLS ----------------
def extract_skills(text):

    found_tech = []
    found_soft = []

    for skill in TECH_SKILLS:
        if skill.lower() in text:
            found_tech.append(skill.title())

    for skill in SOFT_SKILLS:
        if skill.lower() in text:
            found_soft.append(skill.title())

    return {
        "technical": list(set(found_tech)),
        "soft": list(set(found_soft))
    }


# ---------------- EDUCATION ----------------
def extract_education(text):

    degree_words = [
        "btech", "b.e", "mtech", "bsc", "msc",
        "bachelor", "master", "phd"
    ]

    edu_context = [
        "university", "college", "institute", "school",
        "engineering", "technology", "science"
    ]

    lines = text.split('\n')
    education = []

    for line in lines:

        # must contain degree word
        if any(deg in line for deg in degree_words):

            # must also look like an academic line
            if any(ctx in line for ctx in edu_context):
                education.append(line.strip())

    return list(set(education))


# ---------------- EXPERIENCE ----------------
def extract_experience(text):

    experience_keywords = [
        "experience", "worked", "intern", "developer", "engineer"
    ]

    sentences = text.split('.')
    exp = []

    for sent in sentences:
        for word in experience_keywords:
            if word in sent:
                exp.append(sent.strip())
                break

    # keep only first few meaningful lines
    return exp[:5]


# ---------------- MAIN FUNCTION ----------------
def extract_all_details(text):

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text)
    }


# test directly
if __name__ == "__main__":
    from resume_parser import extract_text_from_pdf
    from text_cleaner import clean_resume_text

    raw = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    clean = clean_resume_text(raw)

    details = extract_all_details(clean)

    print("\n===== EXTRACTED DETAILS =====\n")
    for k, v in details.items():
        print(f"{k}: {v}\n")
