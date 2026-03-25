import json

ONET_FILE = "datasets/onet_clean.json"
ROADMAP_FILE = "datasets/domain_roadmap.json"


def load_onet_data():
    with open(ONET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_domain_roadmap():
    with open(ROADMAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_career_gap(user_profile, target_career):
    onet_data = load_onet_data()
    roadmap_data = load_domain_roadmap()

    target_job = next(
        (job for job in onet_data if job["career"].lower() == target_career.lower()),
        None
    )
    if not target_job:
        return {"error": "Career not found in database"}

    from career_matcher import load_skill_domain_map, convert_skills_to_domains

    skill_map = load_skill_domain_map()
    user_skills = user_profile["skills"]["technical"]

    # Use domain counter for strength-aware gap analysis
    user_domain_counts = convert_skills_to_domains(user_skills, skill_map)
    user_domains = set(user_domain_counts.keys())

    matched = []
    missing = []
    total_weight = 0
    matched_weight = 0

    for item in target_job["knowledge"]:
        domain = item["domain"]
        importance = item["importance"]
        total_weight += importance

        if domain.lower() in user_domains:
            matched.append((domain, importance))
            matched_weight += importance
        else:
            missing.append((domain, importance))

    missing.sort(key=lambda x: x[1], reverse=True)

    readiness = round((matched_weight / total_weight) * 100, 2) if total_weight else 0

    roadmap = []
    for domain, _ in missing[:5]:
        key = domain.lower()
        actions = roadmap_data.get(key, [f"Take structured courses in {domain}"])
        
        # Auto-generate search links for any domain
        query = domain.replace(" ", "+")
        coursera_link = f"https://www.coursera.org/search?query={query}"
        udemy_link = f"https://www.udemy.com/courses/search/?q={query}"
        
        roadmap.append({
            "domain": domain,
            "actions": actions,
            "coursera": coursera_link,
            "udemy": udemy_link
        })

    return {
        "career": target_job["career"],
        "readiness": readiness,
        "matched_domains": [m[0] for m in matched],
        "missing_domains": [m[0] for m in missing],
        "roadmap": roadmap
    }