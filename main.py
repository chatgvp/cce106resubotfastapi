from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from io import BytesIO
import PyPDF2
import openai
import json
import _firebasepy
api_key = "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"
openai.api_key = api_key
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"], 
)

@app.post("/add")
async def create_job(
    job_title: str = Form(...),
    job_qualifications: str = Form(...),
    candidate1: UploadFile = File(...)
):
    candidate1_bytes = await candidate1.read()
    candidate1_stream = BytesIO(candidate1_bytes)
    pdf_reader1 = PyPDF2.PdfReader(candidate1_stream)
    extracted_text = ""
    for page in pdf_reader1.pages:
        extracted_text += page.extract_text()
    response_data = chatgptanalyzer(
                    job_title, job_qualifications, extracted_text
                )
    json_object = json.loads(response_data)
    return JSONResponse(content=_firebasepy.add(json_object, candidate1))

@app.get("/get")
async def get():
    return _firebasepy.fetch_all_data()

@app.delete("/delete")
async def delete(key: str):
    _firebasepy.delete(key)
    return {"message": "Item deleted successfully"}


def chatgptanalyzer(job_title, job_qualifications, candidate1):
    json_format = """
                    {
                    "job_title": "",
                    "job_qualifications": "",
                    "candidate1": {
                        "name":"",
                        "strengths": [],
                        "weaknesses": [],
                        "qualification_percentage": ""
                    },
                    "summary": ""
                    }
                """
    chatgpt_prompt = (
        f"""
        Instructions:
        1. You are a very strict and meticulous human resource manager that oversee the recruitment process and thoroughly and strictly selects the job applicants who best fit the organization's requirements.
        ----------------------------------
        2. This is the resume of an applicant applying for the position of {job_title}: "{candidate1}"
        ----------------------------------
        3. Please analyze the applicant's resume 10 times, and determine how well their skills and experience match the given job qualifications below:
        {job_qualifications}
        ----------------------------------
        4. The JSON format provided below includes fields for a job title, job qualifications, a applicant's information, and a summary of the analysis:
        {json_format}
        ----------------------------------
        5. Replace the empty strings under the "job_title", "job_qualifications", and "candidate1" sections with relevant information from the job qualifications and a job applicant's resume, respectively.
        ----------------------------------
        6. For the "candidate1" section, you are required to analyze the applicant's skills and experience based on their resume, and determine their strengths and weaknesses as compared to the job qualifications.
            "name": The applicant's name.
            "strengths": A list of the applicant's strengths that align with the job qualifications make the explanation long .
            "weaknesses": A list of areas where the applicant's skills and experience may not fully match the job requirements, a list of lacking skills, or a list of lacking experience in specific areas of expertise make the explanation long .
            "qualification_percentage": A rating representing how well the applicant's skills and experience match the provided job requirements.
                Give a "Very Low" rating if the applicant's skills and experience matches only 0% to 20% of the provided job requirements and the position of {job_title}.
                Give a "Low" rating if the applicant's skills and experience matches only 21% to 39% of the provided job requirements and the position of {job_title}.
                Give an "Average" rating if the applicant's skills and experience matches only 40% to 60% of the provided job requirements and the position of {job_title}.
                Give a "High" rating if the applicant's skills and experience matches 61% to 79% of the provided job requirements and the position of {job_title}.
                Give a "Very High" rating if the applicant's skills and experience matches 80% to 100% of the provided job requirements and the position of {job_title}.
        ----------------------------------
        7. Use the provided format to summarize the analysis results in the "summary" section. This summary should highlight the applicant's suitability for the job based on their skills, experience, strengths, and areas for improvement. This should be 280 characters (Ensure that the summary provides constructive criticism of the candidate's resume to evaluate its suitability highlight whats lacking in the resume refering to the {job_title}).
        ----------------------------------
        8. After completing the JSON format, you can create a sample job listing and applicant's qualifications to populate the fields. Use your creativity to come up with realistic data for the analysis.
        ----------------------------------
        9. Make sure to complete the JSON format and leave nothing unanswered.
        """
    )
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a very strict and meticulous human resource manager that oversee the recruitment process and thoroughly and strictly selects the job applicants who best fit the organization's requirements."},
                {"role": "user", "content": chatgpt_prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
    return response["choices"][0]["message"]["content"] 