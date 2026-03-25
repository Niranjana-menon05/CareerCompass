import json
import os
import pickle
import re
from collections import Counter

CORPUS_FILE  = "datasets/onet_tfidf_corpus.json"
SKILL_MAP    = "datasets/skill_domain_map.json"
TFIDF_CACHE  = "datasets/tfidf_cache.pkl"
SCORE_THRESHOLD = 10

PHRASE_MAP = {
    "machine learning": "machinelearning",
    "deep learning": "deeplearning",
    "natural language processing": "naturallanguageprocessing",
    "data science": "datascience",
    "data analysis": "dataanalysis",
    "data analytics": "dataanalytics",
    "data engineering": "dataengineering",
    "data structures": "datastructures",
    "computer vision": "computervision",
    "artificial intelligence": "artificialintelligence",
    "neural networks": "neuralnetworks",
    "reinforcement learning": "reinforcementlearning",
    "business analyst": "businessanalyst",
    "business analysis": "businessanalysis",
    "business intelligence": "businessintelligence",
    "scrum master": "scrummaster",
    "project management": "projectmanagement",
    "product management": "productmanagement",
    "software development": "softwaredevelopment",
    "software engineer": "softwareengineer",
    "web development": "webdevelopment",
    "full stack": "fullstack",
    "cloud computing": "cloudcomputing",
    "supply chain": "supplychain",
    "human resources": "humanresources",
    "user stories": "userstories",
    "gap analysis": "gapanalysis",
    "risk analysis": "riskanalysis",
    "requirements gathering": "requirementsgathering",
    "systems analysis": "systemsanalysis",
    "network security": "networksecurity",
    "information technology": "informationtechnology",
    "information systems": "informationsystems",
    "database administration": "databaseadministration",
    "power bi": "powerbi",
    "machine tool": "machinetool",
}

SHORT_SKILLS = {"c", "r", "go", "ai", "ml"}


def tokenize(text):
    STOPWORDS = {
        "a","an","the","and","or","but","in","on","at","to","for","of","with",
        "by","from","as","is","was","are","were","be","been","being","have",
        "has","had","do","does","did","will","would","could","should","may",
        "might","shall","can","need","that","this","these","those","it","its",
        "they","their","them","we","our","you","your","i","my","me","he","she",
        "his","her","who","which","what","when","where","how","all","each",
        "both","few","more","most","other","some","such","no","not","only",
        "same","so","than","too","very","just","because","if","then","into",
        "through","during","before","after","above","below","between","out",
        "off","over","under","again","further","once","s","t","re","ll","ve",
        "including","using","used","use","within","across","based","related",
        "provide","provides","provided","ensure","ensures","work","works",
        "working","develop","develops","developed","manage","manages","managed",
    }
    text = text.lower()
    for phrase, token in PHRASE_MAP.items():
        text = text.replace(phrase, token)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t in SHORT_SKILLS or (t not in STOPWORDS and len(t) > 2)]


def build_tfidf(corpus_texts):
    import math
    N = len(corpus_texts)
    tf_list = []
    df = Counter()
    for text in corpus_texts:
        tokens = tokenize(text)
        tf = Counter(tokens)
        total = sum(tf.values()) or 1
        tf_norm = {term: count / total for term, count in tf.items()}
        tf_list.append(tf_norm)
        for term in set(tokens):
            df[term] += 1
    idf = {term: math.log((N + 1) / (count + 1)) + 1 for term, count in df.items()}
    return idf, tf_list


def tfidf_vector(tf_norm, idf):
    return {term: tf * idf.get(term, 0) for term, tf in tf_norm.items()}


def cosine_similarity(vec_a, vec_b):
    import math
    dot = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in vec_a)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if not mag_a or not mag_b:
        return 0.0
    return dot / (mag_a * mag_b)


def load_or_build_tfidf_cache():
    if os.path.exists(TFIDF_CACHE):
        with open(TFIDF_CACHE, "rb") as f:
            return pickle.load(f)
    print("Building TF-IDF index (first run only)...")
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    texts = [entry["text"] for entry in corpus]
    idf, tf_list = build_tfidf(texts)
    vectors = [tfidf_vector(tf, idf) for tf in tf_list]
    cache = {"corpus": corpus, "idf": idf, "vectors": vectors}
    with open(TFIDF_CACHE, "wb") as f:
        pickle.dump(cache, f)
    print("TF-IDF index built and cached.")
    return cache


def load_skill_domain_map():
    with open(SKILL_MAP, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_skills_to_domains(skills, skill_map):
    domain_counter = Counter()
    for skill in skills:
        if skill.lower() in skill_map:
            for domain in skill_map[skill.lower()]:
                domain_counter[domain] += 1
    return domain_counter


def build_resume_text(user_profile):
    parts = []
    tech_skills = user_profile.get("skills", {}).get("technical", [])
    soft_skills = user_profile.get("skills", {}).get("soft", [])
    all_skills = tech_skills + soft_skills

    skills_text = " ".join(all_skills)
    parts.append(skills_text)
    parts.append(skills_text)
    parts.append(skills_text)

    # Map resume skills to ONET vocabulary
    # ONET uses older/formal terminology — bridge the gap here
    ONET_SYNONYMS = {
    "machine learning":             "computer research algorithms statistical software artificial",
    "data science":                 "statistical computer research mathematical software analysis",
    "deep learning":                "computer research algorithms neural software artificial",
    "natural language processing":  "computer research linguistic software algorithms",
    "computer vision":              "computer research image algorithms software",
    "artificial intelligence":      "computer research algorithms software systems",
    "nlp":                          "computer research linguistic software",
    "python":                       "programming software computer scripting",
    "sql":                          "database querying computer software",
    "mongodb":                      "database computer software systems",
    "statistics":                   "statistical mathematical numerical analysis research",
    "matlab":                       "mathematical statistical computational software",
    "data structures":              "computer software programming algorithms",
    "business analyst":             "systems analysis requirements business process",
    "scrum master":                 "project coordination agile team management",
    "project management":           "planning scheduling coordinating resources",
    "software developer":           "programming software computer applications",
    "web developer":                "computer software programming applications",
    "devops":                       "computer systems software deployment",
    "cybersecurity":                "computer security network systems protection",
    "healthcare":                   "medical clinical patient health",
    "hipaa":                        "medical compliance health regulations",
    }

    resume_lower = (" ".join(all_skills) + " " +
                    " ".join(user_profile.get("experience", []))).lower()

    for skill, synonyms in ONET_SYNONYMS.items():
        if skill in resume_lower:
            parts.append(synonyms + " ")

    for exp in user_profile.get("experience", []):
        parts.append(exp)
    for edu in user_profile.get("education", []):
        parts.append(edu)

    return " ".join(parts)


def recommend_careers(user_profile, top_n=5):
    cache = load_or_build_tfidf_cache()
    corpus = cache["corpus"]
    idf = cache["idf"]
    vectors = cache["vectors"]
    resume_text = build_resume_text(user_profile)
    resume_tokens = tokenize(resume_text)
    total = len(resume_tokens) or 1
    resume_tf = {term: count / total for term, count in Counter(resume_tokens).items()}
    resume_vec = tfidf_vector(resume_tf, idf)
    results = []
    for i, occ_vec in enumerate(vectors):
        sim = cosine_similarity(resume_vec, occ_vec)
        score = round(sim * 100, 2)
        if score >= SCORE_THRESHOLD:
            results.append({"career": corpus[i]["title"], "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_n]

    # Rescale so top result always shows ~85%
    if results:
        top = results[0]["score"]
        for r in results:
            r["score"] = round((r["score"] / top) * 85, 2)

    return results