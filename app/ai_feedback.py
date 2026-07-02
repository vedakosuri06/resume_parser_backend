import httpx

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

async def get_ai_feedback(data: dict) -> list:
    resume_summary = f"""
Name: {data.get('name', 'N/A')}
Email: {data.get('email', 'N/A')}
Phone: {data.get('phone', 'N/A')}
Skills: {', '.join(data.get('skills', []))}
Projects: {data.get('projects', 'None')}
Experience: {data.get('experience', 'None')}
Education: {data.get('education', 'None')}
Certifications: {data.get('certifications', 'None')}
Achievements: {data.get('achievements', 'None')}
"""

    prompt = f"""You are a professional resume reviewer and career coach.
Analyze this resume data and give exactly 6 specific, actionable feedback points.
Be direct and helpful. Focus on what can be improved.
Return ONLY a JSON array of 6 strings, nothing else. No explanation, no markdown.
Example format: ["feedback 1", "feedback 2", "feedback 3", "feedback 4", "feedback 5", "feedback 6"]

Resume Data:
{resume_summary}"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "x-api-key": "YOUR_API_KEY_HERE"
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            result  = response.json()
            content = result["content"][0]["text"].strip()
            import json
            feedback_list = json.loads(content)
            return feedback_list
    except Exception as e:
        return [
            "Quantify your achievements with numbers and percentages.",
            "Add more industry-relevant keywords for ATS optimization.",
            "Use strong action verbs at the start of each bullet point.",
            "Keep your resume to one page if under 2 years of experience.",
            "Add a professional summary at the top of your resume.",
            "Tailor your skills section to match the job you're applying for."
        ]