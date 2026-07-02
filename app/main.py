from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io

from app.parser import extract_text
from app.extractor import parse_resume
from app.exporter import to_json, to_excel, to_word, to_txt
from app.scorer import calculate_ats_score
from app.ai_feedback import get_ai_feedback
from app.job_match import calculate_job_match

app = FastAPI(title="Resume Parser API")

# ---------------------- CORS ----------------------

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://resume-parser-frontend-ig2x.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------


@app.get("/")
def root():
    return {"message": "Resume Parser API is running"}


@app.post("/parse")
async def parse(file: UploadFile = File(...)):
    if not (
        file.filename.endswith(".pdf")
        or file.filename.endswith(".docx")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    file_bytes = await file.read()

    try:
        text = extract_text(file_bytes, file.filename)
        result = parse_resume(text)
        result["ats_score"] = calculate_ats_score(result)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-feedback")
async def ai_feedback(file: UploadFile = File(...)):
    file_bytes = await file.read()

    text = extract_text(file_bytes, file.filename)
    data = parse_resume(text)

    feedback = await get_ai_feedback(data)

    return JSONResponse(
        content={
            "feedback": feedback
        }
    )


@app.post("/job-match")
async def job_match(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    file_bytes = await file.read()

    text = extract_text(file_bytes, file.filename)
    data = parse_resume(text)

    match_result = calculate_job_match(
        data,
        job_description
    )

    return JSONResponse(content=match_result)


@app.post("/export/json")
async def export_json(file: UploadFile = File(...)):
    file_bytes = await file.read()

    text = extract_text(file_bytes, file.filename)
    result = parse_resume(text)

    return StreamingResponse(
        io.BytesIO(to_json(result).encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=resume.json"
        },
    )


@app.post("/export/excel")
async def export_excel(file: UploadFile = File(...)):
    file_bytes = await file.read()

    text = extract_text(file_bytes, file.filename)
    result = parse_resume(text)

    excel_bytes = to_excel(result)

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=resume.xlsx"
        },
    )


@app.post("/export/word")
async def export_word(file: UploadFile = File(...)):
    file_bytes = await file.read()

    text = extract_text(file_bytes, file.filename)
    result = parse_resume(text)

    word_bytes = to_word(result)

    return StreamingResponse(
        io.BytesIO(word_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": "attachment; filename=resume.docx"
        },
    )


@app.post("/export/txt")
async def export_txt(file: UploadFile = File(...)):
    file_bytes = await file.read()

    text = extract_text(file_bytes, file.filename)
    result = parse_resume(text)

    txt_content = to_txt(result)

    return StreamingResponse(
        io.BytesIO(txt_content.encode()),
        media_type="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=resume.txt"
        },
    )