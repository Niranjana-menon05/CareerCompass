import json
from resume_parser import extract_text_from_pdf
from text_cleaner import clean_resume_text
from extractor import extract_all_details


def build_profile(pdf_path):

    # Step 1: read resume
    raw_text = extract_text_from_pdf(pdf_path)

    # Step 2: clean text
    cleaned_text = clean_resume_text(raw_text)

    # Step 3: extract information
    details = extract_all_details(cleaned_text)

    return details


def save_profile_to_json(profile, output_path="output/user_profile.json"):

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4)


# run directly
if __name__ == "__main__":

    pdf_path = "sample_resumes/sample_resume.pdf"

    profile = build_profile(pdf_path)
    save_profile_to_json(profile)

    print("\n✅ PROFILE GENERATED SUCCESSFULLY")
    print("Saved to: output/user_profile.json\n")

    print("Preview:\n")
    print(json.dumps(profile, indent=4))
