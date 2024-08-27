from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List
import json
import os

app = FastAPI()

print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir())

# Create 'static' directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")
    print("Created 'static' directory")

# Check if 'static' directory exists before mounting
if os.path.exists("static") and os.path.isdir("static"):
    print("Static directory found. Mounting...")
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    print("Warning: Unable to create or find 'static' directory. Static files will not be served.")

class ThaiElementAssessment:
    def __init__(self):
        # Load questions and clinical symptoms from JSON files
        with open('questions.json', 'r', encoding='utf-8') as f:
            self.questions = json.load(f)
        with open('clinical_symptoms.json', 'r', encoding='utf-8') as f:
            self.clinical_symptoms = json.load(f)
        self.scores = {"ปิตตะ": 0, "วาตะ": 0, "เสมหะ": 0}
        self.user_symptoms = []

    def process_answers(self, answers: Dict[str, int]):
        for category, choice in answers.items():
            selected_element = list(self.questions[category].keys())[choice - 1]
            self.scores[selected_element] += 1

    def determine_dominant_element(self):
        return max(self.scores, key=self.scores.get)

    def process_symptoms(self, symptoms: List[str]):
        self.user_symptoms = symptoms

    def analyze_correlation(self, dominant_element):
        total_score = sum(self.scores.values())
        dominant_ratio = self.scores[dominant_element] / total_score
        
        total_symptoms = len(self.clinical_symptoms[dominant_element])
        user_symptoms_count = len(self.user_symptoms)
        
        symptom_ratio = user_symptoms_count / total_symptoms if total_symptoms > 0 else 0
        
        correlation = (dominant_ratio + symptom_ratio) / 2
        return correlation

    def get_results(self):
        dominant_element = self.determine_dominant_element()
        correlation = self.analyze_correlation(dominant_element)
        
        risk_level = ""
        explanation = ""
        if 0 <= correlation <= 0.5:
            risk_level = "ไม่มีความเสี่ยงที่ควรเฝ้าระวัง"
            explanation = "ธาตุเด่นของคุณไม่มีความสัมพันธ์มากนักกับอาการทางคลินิกที่พบ คุณควรดูแลสุขภาพตามปกติและสังเกตอาการเปลี่ยนแปลงต่างๆ"
        elif 0.5 < correlation <= 0.8:
            risk_level = "มีความเสี่ยงในระดับเฝ้าระวัง"
            explanation = "ธาตุเด่นของคุณมีความสัมพันธ์ในระดับปานกลางกับอาการทางคลินิกที่พบ คุณควรเฝ้าระวังและดูแลสุขภาพอย่างใกล้ชิด หากมีอาการรุนแรงขึ้น ควรปรึกษาแพทย์"
        elif 0.8 < correlation <= 1.0:
            risk_level = "มีความเสี่ยงมาก โปรดพบแพทย์เพื่อประเมินเพิ่มเติม"
            explanation = "ธาตุเด่นของคุณมีความสัมพันธ์สูงกับอาการทางคลินิกที่พบ คุณควรพบแพทย์เพื่อรับการตรวจประเมินอย่างละเอียด อาจจำเป็นต้องได้รับการรักษาหรือการดูแลเฉพาะทาง"
        
        return {
            "dominant_element": dominant_element,
            "scores": self.scores,
            "user_symptoms": self.user_symptoms,
            "correlation": correlation,
            "risk_level": risk_level,
            "explanation": explanation
        }

class AssessmentInput(BaseModel):
    answers: Dict[str, int]
    symptoms: List[str]

@app.get("/")
async def read_index():
    return FileResponse('index.html')
    
@app.post("/assess")
async def assess(input_data: AssessmentInput):
    assessment = ThaiElementAssessment()
    assessment.process_answers(input_data.answers)
    assessment.process_symptoms(input_data.symptoms)
    results = assessment.get_results()
    return results

@app.get("/questions")
async def get_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    return questions

@app.get("/clinical_symptoms")
async def get_clinical_symptoms():
    with open('clinical_symptoms.json', 'r', encoding='utf-8') as f:
        clinical_symptoms = json.load(f)
    return clinical_symptoms

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
