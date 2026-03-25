from fastapi import FastAPI
from models import Feedback
from typing import List

app = FastAPI()

feedbacks: List[dict] = []


@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    feedbacks.append(feedback.model_dump())
    return {"message": "Feedback received", "feedback": feedback}


@app.get("/feedbacks")
def get_feedbacks():
    return {"feedbacks": feedbacks, "total": len(feedbacks)}
