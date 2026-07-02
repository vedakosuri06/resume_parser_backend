import re

ACTION_VERBS = [
    "built", "developed", "designed", "implemented", "created", "led", "managed",
    "improved", "optimized", "deployed", "integrated", "automated", "analyzed",
    "collaborated", "researched", "architected", "delivered", "launched", "reduced",
    "increased", "achieved", "coordinated", "established", "generated", "streamlined",
    "enhanced", "contributed", "engineered", "solved", "maintained", "tested",
    "trained", "presented", "published", "mentored", "spearheaded", "produced"
]

def calculate_ats_score(data: dict) -> dict:
    score       = 0
    breakdown   = {}
    suggestions = []

    # 1. Contact Info (15 pts)
    contact_score = 0
    if data.get("name"):
        contact_score += 5
    else:
        suggestions.append("Add your full name at the top of the resume.")
    if data.get("email"):
        contact_score += 5
    else:
        suggestions.append("Add a professional email address.")
    if data.get("phone"):
        contact_score += 5
    else:
        suggestions.append("Add a phone number.")
    breakdown["Contact Info"] = {"score": contact_score, "max": 15}
    score += contact_score

    # 2. Links (10 pts)
    links_score = 0
    links = data.get("links", {})
    if links.get("github") and links["github"] != "Not Available":
        links_score += 5
    else:
        suggestions.append("Add your GitHub profile link.")
    if links.get("linkedin") and links["linkedin"] != "Not Available":
        links_score += 5
    else:
        suggestions.append("Add your LinkedIn profile link.")
    breakdown["Links"] = {"score": links_score, "max": 10}
    score += links_score

    # 3. Skills (20 pts)
    skills       = data.get("skills", [])
    skills_count = len(skills)
    if skills_count >= 10:
        skills_score = 20
    elif skills_count >= 6:
        skills_score = 14
    elif skills_count >= 3:
        skills_score = 8
    else:
        skills_score = 0
        suggestions.append("Add more technical skills (aim for at least 8-10).")
    if skills_count < 10:
        suggestions.append(f"You have {skills_count} skills detected. Try to list at least 10 relevant skills.")
    breakdown["Skills"] = {"score": skills_score, "max": 20}
    score += skills_score

    # 4. Projects (15 pts)
    projects = data.get("projects", "None")
    if projects != "None" and len(projects) > 50:
        projects_score = 15
    elif projects != "None":
        projects_score = 8
        suggestions.append("Expand your projects section with more detail.")
    else:
        projects_score = 0
        suggestions.append("Add a projects section to showcase your work.")
    breakdown["Projects"] = {"score": projects_score, "max": 15}
    score += projects_score

    # 5. Certifications (10 pts)
    certs = data.get("certifications", "None")
    if certs != "None" and len(certs) > 10:
        certs_score = 10
    else:
        certs_score = 0
        suggestions.append("Add certifications to strengthen your resume.")
    breakdown["Certifications"] = {"score": certs_score, "max": 10}
    score += certs_score

    # 6. Achievements (10 pts)
    achievements = data.get("achievements", "None")
    if achievements != "None" and len(achievements) > 10:
        achievements_score = 10
    else:
        achievements_score = 0
        suggestions.append("Add achievements or extracurricular activities.")
    breakdown["Achievements"] = {"score": achievements_score, "max": 10}
    score += achievements_score

    # 7. Education (10 pts)
    education = data.get("education", "None")
    if education != "None" and len(education) > 10:
        education_score = 10
    else:
        education_score = 0
        suggestions.append("Add your education details.")
    breakdown["Education"] = {"score": education_score, "max": 10}
    score += education_score

    # 8. Action Verbs (10 pts)
    full_text   = f"{data.get('projects','')} {data.get('experience','')} {data.get('achievements','')}".lower()
    verbs_found = [v for v in ACTION_VERBS if v in full_text]
    if len(verbs_found) >= 5:
        verbs_score = 10
    elif len(verbs_found) >= 3:
        verbs_score = 6
    elif len(verbs_found) >= 1:
        verbs_score = 3
    else:
        verbs_score = 0
        suggestions.append("Use strong action verbs like 'Built', 'Developed', 'Optimized' in your descriptions.")
    breakdown["Action Verbs"] = {"score": verbs_score, "max": 10}
    score += verbs_score

    # Grade
    if score >= 85:
        grade = "Excellent"
    elif score >= 70:
        grade = "Good"
    elif score >= 50:
        grade = "Average"
    else:
        grade = "Needs Work"

    return {
        "score":       score,
        "max":         max_score,
        "grade":       grade,
        "breakdown":   breakdown,
        "suggestions": suggestions
    }

max_score = 100