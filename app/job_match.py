import re

def calculate_job_match(resume_data: dict, job_description: str) -> dict:
    job_lower     = job_description.lower()
    resume_skills = [s.lower() for s in resume_data.get("skills", [])]

    # Full resume text for broader matching
    resume_text = f"""
        {' '.join(resume_data.get('skills', []))}
        {resume_data.get('projects', '')}
        {resume_data.get('experience', '')}
        {resume_data.get('education', '')}
        {resume_data.get('certifications', '')}
    """.lower()

    ALL_SKILLS = [
        "python", "java", "javascript", "typescript", "react", "node.js", "sql",
        "mongodb", "postgresql", "docker", "kubernetes", "aws", "azure", "git",
        "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
        "numpy", "flask", "fastapi", "django", "html", "css", "c++", "c#",
        "excel", "power bi", "tableau", "spark", "hadoop", "linux", "rest api",
        "graphql", "redux", "next.js", "vue.js", "angular", "figma", "mysql",
        "opencv", "keras", "scikit-learn", "matplotlib", "seaborn", "nltk",
        "bootstrap", "tailwind", "firebase", "supabase", "spring boot",
        "random forest", "communication", "teamwork", "leadership", "agile",
        "scrum", "jira", "devops", "ci/cd", "microservices", "api", "testing",
        "data analysis", "data science", "nlp", "computer vision", "cloud",
        "problem solving", "project management", "kotlin", "swift", "flutter",
        "dart", "php", "ruby", "scala", "matlab", "selenium", "jenkins",
        "github actions", "render", "jupyter", "intellij", "vs code",
        "feature engineering", "model evaluation", "ai", "ml", "llm",
        "spring boot", "node.js", "react.js", "express.js", "mongodb"
    ]

    # Only match skills that appear in job description AND are at least 2 chars
    job_required_skills = [
        s for s in ALL_SKILLS
        if s in job_lower and len(s) >= 2
    ]

    # Match against full resume text
    matched_skills = [
        s for s in job_required_skills
        if s in resume_text
    ]
    missing_skills = [s for s in job_required_skills if s not in matched_skills]

    # Score
    if job_required_skills:
        match_percent = int((len(matched_skills) / len(job_required_skills)) * 100)
    else:
        match_percent = 50

    match_percent = min(match_percent, 100)

    if match_percent >= 80:
        grade = "Strong Match 🟢"
    elif match_percent >= 60:
        grade = "Good Match 🟡"
    elif match_percent >= 40:
        grade = "Partial Match 🟠"
    else:
        grade = "Low Match 🔴"

    suggestions = []
    if missing_skills:
        suggestions.append(f"Add these missing skills to your resume: {', '.join(missing_skills[:5])}")
    if match_percent < 60:
        suggestions.append("Tailor your resume keywords to match this job description more closely.")
    if match_percent >= 80:
        suggestions.append("Great match! Make sure your resume highlights these skills prominently.")

    return {
        "match_percent":  match_percent,
        "grade":          grade,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions":    suggestions
    }