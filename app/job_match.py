import re


SKILL_RESOURCES = {
    "python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/"},
        {"title": "Automate the Boring Stuff", "url": "https://automatetheboringstuff.com/"},
    ],
    "javascript": [
        {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"},
        {"title": "JavaScript.info", "url": "https://javascript.info/"},
    ],
    "react": [
        {"title": "React Docs", "url": "https://react.dev/learn"},
        {"title": "Full Stack Open", "url": "https://fullstackopen.com/en/"},
    ],
    "node.js": [
        {"title": "Node.js Learn", "url": "https://nodejs.org/en/learn"},
        {"title": "Express Docs", "url": "https://expressjs.com/"},
    ],
    "sql": [
        {"title": "SQLBolt", "url": "https://sqlbolt.com/"},
        {"title": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com/"},
    ],
    "docker": [
        {"title": "Docker Get Started", "url": "https://docs.docker.com/get-started/"},
        {"title": "Play with Docker", "url": "https://labs.play-with-docker.com/"},
    ],
    "machine learning": [
        {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course"},
        {"title": "Hands-On ML Notes", "url": "https://github.com/ageron/handson-ml3"},
    ],
    "fastapi": [
        {"title": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
        {"title": "FastAPI Best Practices", "url": "https://github.com/zhanymkanov/fastapi-best-practices"},
    ],
}

GENERIC_RESOURCES = [
    {"title": "roadmap.sh", "url": "https://roadmap.sh/"},
    {"title": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/"},
]


def _distribute_skills(skills, buckets=3):
    distributed = [[] for _ in range(buckets)]
    for idx, skill in enumerate(skills):
        distributed[idx % buckets].append(skill)
    return distributed


def _resource_cards_for_skills(skills):
    cards = []
    seen = set()
    for skill in skills:
        picks = SKILL_RESOURCES.get(skill.lower(), GENERIC_RESOURCES)
        for item in picks[:2]:
            key = (skill.lower(), item["url"])
            if key in seen:
                continue
            cards.append({
                "skill": skill,
                "title": item["title"],
                "url": item["url"],
            })
            seen.add(key)
    return cards[:6]


def _build_roadmap(match_percent, missing_skills, matched_skills):
    unique_missing = list(dict.fromkeys(missing_skills))

    if unique_missing:
        total_gap = max(0, 100 - match_percent)
        improvement_cap = min(total_gap, max(8, min(35, len(unique_missing) * 4)))
    else:
        improvement_cap = 6

    phase_weights = [0.40, 0.35, 0.25]
    phase_improvements = [round(improvement_cap * w) for w in phase_weights]
    while sum(phase_improvements) < improvement_cap:
        phase_improvements[0] += 1
    while sum(phase_improvements) > improvement_cap:
        phase_improvements[0] -= 1

    if unique_missing:
        phase_skills = _distribute_skills(unique_missing, 3)
    else:
        reinforcement = list(dict.fromkeys(matched_skills[:6])) or ["core skills"]
        phase_skills = _distribute_skills(reinforcement, 3)

    phase_titles = ["Days 1-30", "Days 31-60", "Days 61-90"]
    phase_focus = [
        "Foundation and fundamentals",
        "Applied projects and depth",
        "Interview readiness and polishing",
    ]

    phases = []
    running_score = match_percent
    for i in range(3):
        skills = phase_skills[i]
        running_score = min(100, running_score + phase_improvements[i])

        if unique_missing:
            actions = [
                f"Learn and practice: {', '.join(skills) if skills else 'one core missing skill'}.",
                "Build one mini project that demonstrates these skills.",
                "Update resume bullets with measurable outcomes for the new work.",
            ]
        else:
            actions = [
                "Deepen existing strengths with an advanced project.",
                "Add quantified achievements and metrics to resume bullets.",
                "Align keywords and project summaries to target roles.",
            ]

        phases.append({
            "phase": phase_titles[i],
            "focus": phase_focus[i],
            "skills": skills,
            "actions": actions,
            "resources": _resource_cards_for_skills(skills),
            "estimated_readiness": running_score,
        })

    target = min(100, match_percent + improvement_cap)
    return {
        "current_readiness": match_percent,
        "estimated_improvement": target - match_percent,
        "target_readiness": target,
        "phases": phases,
    }

def calculate_job_match(resume_data: dict, job_description: str) -> dict:
    job_lower = job_description.lower().strip()

    # Full resume text for broader matching
    resume_text = f"""
        {' '.join(resume_data.get('skills', []))}
        {resume_data.get('projects', '')}
        {resume_data.get('experience', '')}
        {resume_data.get('education', '')}
        {resume_data.get('certifications', '')}
    """.lower()

    ROLE_SKILL_MAP = {
        # ── AI / ML ──────────────────────────────────────────────────────────
        "ai engineer":              ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "numpy", "pandas", "nlp", "computer vision", "docker", "aws", "git"],
        "machine learning engineer":["python", "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "numpy", "pandas", "docker", "aws", "git", "mlops"],
        "deep learning engineer":   ["python", "deep learning", "tensorflow", "pytorch", "keras", "numpy", "opencv", "gpu", "cuda", "docker", "git"],
        "nlp engineer":             ["python", "nlp", "tensorflow", "pytorch", "transformers", "scikit-learn", "numpy", "pandas", "spacy", "nltk", "git"],
        "computer vision engineer": ["python", "opencv", "tensorflow", "pytorch", "deep learning", "numpy", "scikit-learn", "docker", "git", "cuda"],
        "data scientist":           ["python", "machine learning", "deep learning", "tensorflow", "scikit-learn", "numpy", "pandas", "matplotlib", "seaborn", "sql", "statistics", "git"],
        "data analyst":             ["python", "sql", "pandas", "numpy", "matplotlib", "seaborn", "excel", "power bi", "tableau", "statistics", "git"],
        "data engineer":            ["python", "sql", "spark", "hadoop", "aws", "docker", "airflow", "kafka", "postgresql", "mongodb", "git"],
        "business analyst":         ["sql", "excel", "power bi", "tableau", "python", "data analysis", "statistics", "jira", "agile", "communication"],
        "research scientist":       ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "numpy", "pandas", "statistics", "research", "git"],
        "mlops engineer":           ["python", "docker", "kubernetes", "aws", "mlflow", "airflow", "git", "ci/cd", "terraform", "machine learning"],

        # ── Web Development ───────────────────────────────────────────────────
        "frontend developer":       ["javascript", "react", "html", "css", "typescript", "redux", "next.js", "git", "figma", "rest api"],
        "backend developer":        ["python", "java", "node.js", "sql", "mongodb", "postgresql", "docker", "rest api", "git", "aws", "fastapi", "django", "spring boot"],
        "full stack developer":     ["javascript", "react", "node.js", "html", "css", "sql", "mongodb", "docker", "git", "rest api", "typescript"],
        "react developer":          ["react", "javascript", "typescript", "html", "css", "redux", "git", "rest api", "node.js", "next.js"],
        "react native developer":   ["react", "react native", "javascript", "typescript", "git", "rest api", "firebase", "redux", "expo"],
        "node.js developer":        ["node.js", "javascript", "typescript", "express.js", "mongodb", "sql", "rest api", "docker", "git", "aws"],
        "python developer":         ["python", "django", "flask", "fastapi", "sql", "docker", "git", "rest api", "numpy", "pandas", "postgresql"],
        "java developer":           ["java", "spring boot", "sql", "docker", "git", "rest api", "maven", "junit", "microservices", "aws"],
        "php developer":            ["php", "laravel", "mysql", "html", "css", "javascript", "git", "rest api", "docker"],
        "django developer":         ["python", "django", "sql", "postgresql", "rest api", "docker", "git", "html", "css", "javascript"],
        "vue.js developer":         ["vue.js", "javascript", "typescript", "html", "css", "git", "rest api", "vuex", "node.js"],
        "angular developer":        ["angular", "typescript", "javascript", "html", "css", "git", "rest api", "rxjs", "node.js"],
        "next.js developer":        ["next.js", "react", "javascript", "typescript", "html", "css", "git", "rest api", "node.js", "tailwind"],
        "wordpress developer":      ["php", "wordpress", "html", "css", "javascript", "mysql", "git", "rest api"],

        # ── Mobile Development ────────────────────────────────────────────────
        "android developer":        ["kotlin", "java", "android", "git", "rest api", "sql", "firebase", "jetpack compose"],
        "ios developer":            ["swift", "xcode", "git", "rest api", "firebase", "objective-c", "uikit", "swiftui"],
        "flutter developer":        ["flutter", "dart", "git", "rest api", "firebase", "android", "ios", "state management"],
        "mobile developer":         ["flutter", "dart", "kotlin", "swift", "react native", "javascript", "git", "rest api", "firebase"],

        # ── Cloud & DevOps ────────────────────────────────────────────────────
        "devops engineer":          ["docker", "kubernetes", "aws", "azure", "linux", "ci/cd", "jenkins", "git", "terraform", "python", "bash"],
        "cloud engineer":           ["aws", "azure", "docker", "kubernetes", "linux", "terraform", "git", "ci/cd", "python", "networking"],
        "aws engineer":             ["aws", "ec2", "s3", "lambda", "docker", "kubernetes", "terraform", "python", "git", "ci/cd"],
        "azure engineer":           ["azure", "docker", "kubernetes", "terraform", "python", "git", "ci/cd", "powershell", "linux"],
        "site reliability engineer":["linux", "python", "docker", "kubernetes", "aws", "terraform", "ci/cd", "monitoring", "git", "bash"],
        "infrastructure engineer":  ["linux", "docker", "kubernetes", "terraform", "aws", "networking", "git", "bash", "python", "ci/cd"],
        "platform engineer":        ["kubernetes", "docker", "terraform", "aws", "python", "git", "ci/cd", "linux", "monitoring"],

        # ── Cybersecurity ─────────────────────────────────────────────────────
        "cybersecurity engineer":   ["linux", "python", "networking", "sql", "docker", "encryption", "penetration testing", "security", "git", "bash"],
        "security analyst":         ["linux", "python", "networking", "sql", "security", "encryption", "siem", "firewall", "vulnerability assessment"],
        "penetration tester":       ["linux", "python", "networking", "security", "kali linux", "metasploit", "burp suite", "sql injection", "git"],
        "ethical hacker":           ["linux", "python", "networking", "security", "kali linux", "metasploit", "burp suite", "penetration testing"],

        # ── Database ──────────────────────────────────────────────────────────
        "database administrator":   ["sql", "postgresql", "mongodb", "mysql", "oracle", "docker", "linux", "performance tuning", "backup", "replication"],
        "database developer":       ["sql", "postgresql", "mysql", "mongodb", "python", "stored procedures", "indexing", "git", "docker"],

        # ── Design ───────────────────────────────────────────────────────────
        "ui ux designer":           ["figma", "html", "css", "javascript", "react", "adobe xd", "wireframing", "prototyping", "user research"],
        "product designer":         ["figma", "adobe xd", "wireframing", "prototyping", "user research", "html", "css", "javascript", "react"],
        "graphic designer":         ["adobe photoshop", "illustrator", "figma", "canva", "typography", "branding", "ui design"],

        # ── Software Engineering ──────────────────────────────────────────────
        "software engineer":        ["python", "java", "javascript", "git", "sql", "docker", "rest api", "data structures", "algorithms", "agile"],
        "software developer":       ["python", "java", "javascript", "git", "sql", "docker", "rest api", "agile", "testing"],
        "systems engineer":         ["linux", "python", "c++", "docker", "networking", "git", "bash", "aws", "debugging"],
        "embedded systems engineer":["c", "c++", "embedded systems", "rtos", "linux", "python", "git", "microcontrollers", "debugging"],
        "qa engineer":              ["python", "selenium", "testing", "git", "sql", "docker", "jira", "agile", "junit", "automation"],
        "test engineer":            ["python", "selenium", "testing", "git", "sql", "jira", "agile", "automation", "cypress"],
        "blockchain developer":     ["solidity", "ethereum", "python", "javascript", "node.js", "git", "docker", "web3.js", "smart contracts"],
        "game developer":           ["c++", "unity", "unreal engine", "python", "git", "opengl", "physics simulation", "3d modeling"],

        # ── Product & Management ──────────────────────────────────────────────
        "product manager":          ["agile", "scrum", "jira", "sql", "excel", "power bi", "communication", "roadmap", "stakeholder management", "python"],
        "project manager":          ["agile", "scrum", "jira", "excel", "communication", "risk management", "budget management", "ms project", "stakeholder management"],
        "scrum master":             ["agile", "scrum", "jira", "communication", "sprint planning", "retrospectives", "kanban", "confluence"],

        # ── Data & Analytics ─────────────────────────────────────────────────
        "power bi developer":       ["power bi", "sql", "excel", "dax", "data modeling", "python", "tableau", "statistics"],
        "tableau developer":        ["tableau", "sql", "excel", "python", "data visualization", "statistics", "power bi"],
        "etl developer":            ["python", "sql", "spark", "airflow", "docker", "aws", "postgresql", "data modeling", "git"],
        "quantitative analyst":     ["python", "r", "statistics", "machine learning", "sql", "numpy", "pandas", "matlab", "excel"],

        # ── Support & Operations ──────────────────────────────────────────────
        "technical support":        ["linux", "windows", "networking", "sql", "communication", "troubleshooting", "ticketing", "python"],
        "it support":               ["linux", "windows", "networking", "troubleshooting", "ticketing", "communication", "sql", "hardware"],
        "network engineer":         ["networking", "linux", "cisco", "firewall", "tcp/ip", "routing", "switching", "python", "aws"],
    }

    # ── Match job description to a known role ─────────────────────────────────
    matched_role  = None
    required_skills = []

    for role, skills in ROLE_SKILL_MAP.items():
        if role in job_lower:
            matched_role    = role
            required_skills = skills
            break

    # ── Fallback: extract skills directly from job description ────────────────
    if not required_skills:
        ALL_SKILLS = [
            "python", "java", "javascript", "typescript", "react", "node.js", "sql",
            "mongodb", "postgresql", "docker", "kubernetes", "aws", "azure", "git",
            "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
            "numpy", "flask", "fastapi", "django", "html", "css", "c++", "c#",
            "excel", "power bi", "tableau", "spark", "hadoop", "linux", "rest api",
            "graphql", "redux", "next.js", "vue.js", "angular", "figma", "mysql",
            "opencv", "keras", "scikit-learn", "matplotlib", "seaborn", "nltk",
            "bootstrap", "tailwind", "firebase", "supabase", "spring boot",
            "random forest", "agile", "scrum", "jira", "devops", "ci/cd",
            "microservices", "testing", "data analysis", "data science", "nlp",
            "computer vision", "kotlin", "swift", "flutter", "php", "ruby",
            "scala", "selenium", "jenkins", "github actions", "terraform",
            "airflow", "kafka", "spark", "hadoop", "tableau", "power bi",
            "pytorch", "tensorflow", "keras", "scikit-learn", "opencv"
        ]
        # Only match skills that are 4+ chars or multi-word to avoid false positives
        required_skills = [
            s for s in ALL_SKILLS
            if s in job_lower and (len(s) >= 4 or " " in s)
        ]

    if not required_skills:
        roadmap = _build_roadmap(0, [], [])
        return {
            "match_percent":  0,
            "grade":          "Unable to Analyse 🔴",
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": [
                "Could not detect specific skills from the job description.",
                "Try pasting the full job description with required skills listed.",
                "Example: 'Looking for a React developer with TypeScript, Node.js, and AWS experience.'"
            ],
            "roadmap": roadmap,
        }

    # ── Compare required vs resume ────────────────────────────────────────────
    matched_skills = [s for s in required_skills if s in resume_text]
    missing_skills = [s for s in required_skills if s not in matched_skills]

    match_percent = int((len(matched_skills) / len(required_skills)) * 100)
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
    if matched_role:
        suggestions.append(f"Role detected: {matched_role.title()}")
    if missing_skills:
        suggestions.append(f"Add these missing skills to your resume: {', '.join(missing_skills[:6])}")
    if match_percent < 60:
        suggestions.append("Tailor your resume keywords to match this job description more closely.")
    if match_percent >= 80:
        suggestions.append("Strong match! Make sure your resume highlights these skills prominently.")

    roadmap = _build_roadmap(match_percent, missing_skills, matched_skills)

    return {
        "match_percent":  match_percent,
        "grade":          grade,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions":    suggestions,
        "roadmap":        roadmap,
    }