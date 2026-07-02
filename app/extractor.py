import re
import spacy

nlp = spacy.load("en_core_web_sm")

SKILLS_DB = [
    "python", "java", "javascript", "typescript", "react", "node.js", "sql",
    "mongodb", "postgresql", "docker", "kubernetes", "aws", "azure", "git",
    "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
    "numpy", "flask", "fastapi", "django", "html", "css", "c++", "c#",
    "excel", "power bi", "tableau", "spark", "hadoop", "linux", "rest api",
    "graphql", "redux", "next.js", "vue.js", "angular", "figma", "mysql",
    "opencv", "keras", "scikit-learn", "matplotlib", "seaborn", "nltk",
    "bootstrap", "tailwind", "firebase", "supabase", "spring boot",
    "random forest", "fastapi", "rest api","scikit-learn", "random forest", "feature engineering", "model evaluation",
"spring boot", "github actions", "jupyter", "intellij", "vs code",
"node.js", "react.js", "express.js", "ai", "ml", "render",
]

EXPERIENCE_HEADERS     = ["experience", "work experience", "employment", "work history", "professional experience", "internship", "internships"]
EDUCATION_HEADERS      = ["education", "academic background", "qualifications", "academic qualifications"]
PROJECTS_HEADERS       = ["projects", "personal projects", "academic projects", "project work", "key projects"]
CERTIFICATIONS_HEADERS = ["certifications", "certification", "certificates", "certificate", "courses", "licenses"]
ACHIEVEMENTS_HEADERS   = ["achievements", "activities", "achievements & activities", "achievements and activities", "awards", "accomplishments", "honors", "extracurricular"]

FALSE_NAMES = {
    "django", "react", "flask", "python", "java", "node", "angular", "vue",
    "docker", "linux", "aws", "azure", "html", "css", "git", "github",
    "tensorflow", "pytorch", "keras", "bootstrap", "tailwind", "figma",
    "mongodb", "mysql", "postgresql", "firebase", "supabase", "opencv",
    "career analyzer", "professional summary", "summary", "objective",
    "resume", "curriculum vitae", "cv", "spring boot"
}

EXCLUDED_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "mail.com"]

ALL_STOP_KEYWORDS = [
    "education", "experience", "work experience", "skills", "projects",
    "certifications", "certification", "certificates", "awards", "languages",
    "hobbies", "summary", "professional summary", "objective", "references",
    "internship", "internships", "courses", "achievements", "accomplishments",
    "licenses", "activities", "achievements and activities",
    "achievements & activities", "work history", "employment",
    "extracurricular", "honors", "declaration"
]


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    return match.group().strip() if match else ""


def extract_name(text: str) -> str:
    lines = text.split("\n")
    for line in lines[:10]:
        line = line.strip()
        if not line:
            continue
        if any(c in line for c in ["@", "+", "/", "|", "http"]):
            continue
        words = line.split()
        if (2 <= len(words) <= 5
                and line.isupper()
                and all(w.isalpha() for w in words)
                and line.lower() not in FALSE_NAMES):
            return line.title()

    for line in lines[:10]:
        line = line.strip()
        if not line:
            continue
        if any(c in line for c in ["@", "+", "/", "|", "http"]):
            continue
        words = line.split()
        if (2 <= len(words) <= 5
                and all(w[0].isupper() for w in words if w)
                and all(w.isalpha() for w in words)
                and line.lower() not in FALSE_NAMES):
            return line

    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            if name.lower() not in FALSE_NAMES and len(name.split()) >= 2:
                return name
    return ""


def extract_links(text: str) -> dict:
    github   = re.search(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9_.\-]+", text)
    linkedin = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_.\-/]+", text)

    portfolio_found = None
    portfolio_matches = re.findall(r"https?://[A-Za-z0-9_.\-/]+\.[A-Za-z]{2,}[^\s|,]*", text)
    for url in portfolio_matches:
        is_excluded = any(ex in url for ex in EXCLUDED_DOMAINS)
        is_known    = any(k in url for k in ["github.com", "linkedin.com"])
        if not is_excluded and not is_known:
            portfolio_found = url
            break

    return {
        "github":    github.group() if github else "Not Available",
        "linkedin":  linkedin.group().rstrip("/|, ") if linkedin else "Not Available",
        "portfolio": portfolio_found if portfolio_found else "Not Available",
    }


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    return list(set(skill for skill in SKILLS_DB if skill in text_lower))


def clean_line(line: str) -> str:
    """Lowercase, strip special chars for comparison"""
    return re.sub(r"[:\-_]", " ", line.strip().lower()).strip()


def split_on_section_keywords(line: str) -> list:
    """
    If a line contains multiple section headers merged together
    (e.g. 'June 2025ACHIEVEMENTS & ACTIVITIES'), split them apart.
    Returns list of sub-lines.
    """
    # Insert newline before any known section keyword found mid-line
    pattern = r'(?i)(' + '|'.join(
        re.escape(k) for k in sorted(ALL_STOP_KEYWORDS, key=len, reverse=True)
    ) + r')'
    parts = re.split(pattern, line, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def is_exact_header(line: str, headers: list) -> bool:
    """Check if line exactly matches one of the headers (case-insensitive)"""
    cleaned = clean_line(line)
    for h in headers:
        h_clean = re.sub(r"[:\-_]", " ", h).strip().lower()
        if cleaned == h_clean:
            return True
    return False


def is_any_section_header(line: str) -> bool:
    """Check if line is ANY known section header"""
    cleaned = clean_line(line)
    for kw in ALL_STOP_KEYWORDS:
        kw_clean = re.sub(r"[:\-_]", " ", kw).strip().lower()
        if cleaned == kw_clean:
            return True
    return False


def preprocess_text(text: str) -> str:
    """
    Fix merged lines like 'June 2025ACHIEVEMENTS & ACTIVITIES'
    by inserting newlines before section keywords found mid-line.
    """
    pattern = r'(?i)(' + '|'.join(
        re.escape(k) for k in sorted(ALL_STOP_KEYWORDS, key=len, reverse=True)
    ) + r')'

    fixed_lines = []
    for line in text.split("\n"):
        # Check if a section keyword appears mid-line (not at start)
        match = re.search(pattern, line, flags=re.IGNORECASE)
        if match and match.start() > 0:
            before = line[:match.start()].strip()
            keyword_onwards = line[match.start():].strip()
            if before:
                fixed_lines.append(before)
            fixed_lines.append(keyword_onwards)
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)


def extract_section(text: str, headers: list) -> str:
    lines = text.split("\n")
    capture = False
    section_lines = []

    for line in lines:
        line_stripped = line.strip()

        if is_exact_header(line_stripped, headers):
            capture = True
            continue

        if capture:
            if line_stripped and not is_exact_header(line_stripped, headers) and is_any_section_header(line_stripped):
                break
            section_lines.append(line)

    result = "\n".join(section_lines).strip()
    return result if result else "None"


def remove_years(text: str) -> str:
    """Remove standalone years and date ranges like 2024, 2024-2025, 2024–2025"""
    text = re.sub(r'\b(19|20)\d{2}\s*[–\-]\s*(19|20)\d{2}\b', '', text)
    text = re.sub(r'\b(19|20)\d{2}\b', '', text)
    return text


def extract_projects(text: str) -> str:
    """
    Extract projects as clean summary:
    Project Name | Tech Stack
    instead of full paragraphs.
    """
    raw = extract_section(text, PROJECTS_HEADERS)
    if raw == "None":
        return "None"

    lines = raw.split("\n")
    projects = []
    current_project = None
    current_tech    = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove bullet characters
        line_clean = re.sub(r'^[•\-\*]\s*', '', line).strip()

        # Detect project title line — usually has | or — separating name from tech
        is_title = (
            "|" in line_clean or
            "—" in line_clean or
            re.match(r'^[A-Z][A-Za-z0-9\s&\-]+[|—]', line_clean)
        )

        if is_title:
            # Save previous project
            if current_project:
                tech_str = f" | {current_tech}" if current_tech else ""
                projects.append(f"• {current_project}{tech_str}")

            # Parse new project title
            parts = re.split(r'[|—]', line_clean)
            current_project = parts[0].strip()
            current_project = remove_years(current_project).strip()

            # Extract tech from second part if available
            if len(parts) > 1:
                tech_raw = parts[1].strip()
                tech_raw = remove_years(tech_raw).strip().rstrip(",").strip()
                current_tech = tech_raw
            else:
                current_tech = None

    # Add last project
    if current_project:
        tech_str = f" | {current_tech}" if current_tech else ""
        projects.append(f"• {current_project}{tech_str}")

    return "\n".join(projects) if projects else raw


def extract_certifications(text: str) -> str:
    """Extract certifications, one per line, no dates"""
    raw = extract_section(text, CERTIFICATIONS_HEADERS)
    if raw == "None":
        return "None"

    lines = raw.split("\n")
    certs = []
    for line in lines:
        line = re.sub(r'^[•\-\*]\s*', '', line.strip()).strip()
        if not line:
            continue
        # Remove dates like "April 2026", "June 2025", "March 2026"
        line = re.sub(r'[-–—]\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*(19|20)\d{2}', '', line)
        line = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s*(19|20)\d{2}\b', '', line)
        line = remove_years(line).strip().rstrip("—-–").strip()
        if line:
            certs.append(f"• {line}")

    return "\n".join(certs) if certs else "None"


def extract_achievements(text: str) -> str:
    """Extract achievements, one per line"""
    raw = extract_section(text, ACHIEVEMENTS_HEADERS)
    if raw == "None":
        return "None"

    lines = raw.split("\n")
    items = []
    for line in lines:
        line = re.sub(r'^[•\-\*]\s*', '', line.strip()).strip()
        line = remove_years(line).strip()
        if line:
            items.append(f"• {line}")

    return "\n".join(items) if items else "None"


def parse_resume(text: str) -> dict:
    # Fix merged lines before parsing
    text = preprocess_text(text)

    return {
        "name":           extract_name(text),
        "email":          extract_email(text),
        "phone":          extract_phone(text),
        "links":          extract_links(text),
        "skills":         extract_skills(text),
        "experience":     extract_section(text, EXPERIENCE_HEADERS),
        "education":      extract_section(text, EDUCATION_HEADERS),
        "projects":       extract_projects(text),
        "certifications": extract_certifications(text),
        "achievements":   extract_achievements(text),
    }