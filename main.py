import os

from datetime import datetime, timedelta  
from typing import List, Optional, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html
)
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import custom modules
from pymongo import MongoClient
from personality_processing import process_personality_assessment

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Personality Assessment API",
    description="Backend server for personality assessment application",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# CORS Middleware Configuration
# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# MongoDB Connection
def get_mongodb_connection():
    """
    Establish MongoDB connection
    
    Returns:
        pymongo.database.Database: Connected MongoDB database instance
    """
    try:
        # Get MongoDB connection string from environment variable
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        database_name = os.getenv("DATABASE_NAME", "personality_assessment")
        
        # Create MongoDB client
        client = MongoClient(mongo_uri)
        db = client[database_name]
        
        return db
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        raise

# Database Connection (Global Variable)
db = get_mongodb_connection()

# Pydantic Models
class UserData(BaseModel):
    name: str
    userType: str
    rollNumber: Optional[str] = None

class AssessmentSubmission(BaseModel):
    user: UserData
    questionAnswers: List[str]
    imageAnswers: List[str]

# Corrected Feedback Model
class FeedbackSubmission(BaseModel):
    feedbackScores: Dict[str, int]
    additionalComments: Optional[str] = None

# Custom OpenAPI Documentation Routes
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Personality Assessment API Docs",
        oauth2_redirect_url="/docs/oauth2-redirect"
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def oauth2_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    return get_openapi(
        title="Personality Assessment API",
        version="1.0.0",
        description="Backend server for personality assessment application",
        routes=app.routes
    )

@app.get("/get-assessment/{user_identifier}")
async def get_assessment(user_identifier: str):
    try:
        assessment = db.assessments.find_one({"user_id": user_identifier})
        
        if not assessment:
            user = db.users.find_one(
                {"name": user_identifier},
                sort=[("created_at", -1)]
            )
            
            if user:
                assessment = db.assessments.find_one(
                    {"user_id": str(user['_id'])},
                    sort=[("assessment_date", -1)]
                )
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return {
            "personality_result": assessment.get("personality_result", ""),
            "question_answers": assessment.get("question_answers", []),
            "image_answers": assessment.get("image_answers", [])
        }
    
    except Exception as e:
        print(f"Error fetching assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Personality Assessment API is running"}


# Add these new endpoints
@app.get("/api/admin/analytics/users")
async def get_user_analytics():
    pipeline = [
        {"$group": {
            "_id": "$user_type",
            "count": {"$sum": 1},
            "last_week": {
                "$sum": {"$cond": [{"$gte": ["$created_at", datetime.utcnow() - timedelta(days=7)]}, 1, 0]}
            }
        }},
        {"$project": {
            "userType": "$_id",
            "total": "$count",
            "lastWeek": "$last_week",
            "_id": 0
        }}
    ]
    return list(db.users.aggregate(pipeline))

@app.get("/api/admin/analytics/assessments")
async def get_assessment_analytics():
    pipeline = [
        {"$group": {
            "_id": "$dominant_trait",
            "count": {"$sum": 1},
            "avg_answers": {"$avg": {"$size": "$question_answers"}}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    return list(db.assessments.aggregate(pipeline))

@app.get("/api/admin/analytics/feedback")
async def get_feedback_analytics():
    pipeline = [
        {"$unwind": "$feedback_scores"},
        {"$group": {
            "_id": "$feedback_scores.k",
            "avg": {"$avg": "$feedback_scores.v"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "question": "$_id",
            "average": {"$round": ["$avg", 2]},
            "responses": "$count",
            "_id": 0
        }}
    ]
    return list(db.feedback.aggregate(pipeline))
@app.post("/submit-assessment")
async def submit_assessment(assessment_data: AssessmentSubmission):
    try:
        if len(assessment_data.questionAnswers) != 6:
            raise HTTPException(
                status_code=400, 
                detail="Exactly 6 question answers are required"
            )
        
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_api_key:
            raise HTTPException(
                status_code=500, 
                detail="Mistral API key not configured"
            )
        
        existing_user = db.users.find_one({
            "name": assessment_data.user.name,
            "user_type": assessment_data.user.userType
        })
        
        if existing_user:
            user_id = str(existing_user['_id'])
        else:
            user_data = {
                "name": assessment_data.user.name,
                "user_type": assessment_data.user.userType,
                "roll_number": assessment_data.user.rollNumber,
                "created_at": datetime.utcnow()
            }
            
            user_result = db.users.insert_one(user_data)
            user_id = str(user_result.inserted_id)
        
        personality_result = process_personality_assessment(
            assessment_data.questionAnswers, 
            mistral_api_key
        )
        
        assessment_record = {
            "user_id": user_id,
            "question_answers": assessment_data.questionAnswers,
            "image_answers": assessment_data.imageAnswers,
            "personality_result": personality_result,
            "assessment_date": datetime.utcnow()
        }
        
        db.assessments.insert_one(assessment_record)
        
        return {
            "message": "Assessment submitted successfully",
            "user_id": user_id,
            "personality_result": personality_result
        }
    
    except Exception as e:
        print(f"Assessment submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/users")
async def get_all_users():
    try:
        users = list(db.users.find({}, {"password": 0}))  # Exclude sensitive data
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/assessments")
async def get_all_assessments():
    try:
        assessments = list(db.assessments.find())
        # Convert ObjectId to string
        for assessment in assessments:
            assessment['_id'] = str(assessment['_id'])
            assessment['user_id'] = str(assessment['user_id'])
        return assessments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/feedbacks")
async def get_all_feedbacks():
    try:
        feedbacks = list(db.feedback.find())
        # Convert ObjectId to string
        for feedback in feedbacks:
            feedback['_id'] = str(feedback['_id'])
        return feedbacks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))# Corrected Feedback Endpoint
@app.post("/submit-feedback")
async def submit_feedback(feedback_data: FeedbackSubmission):
    try:
        feedback_record = {
            "feedback_scores": feedback_data.feedbackScores,
            "additional_comments": feedback_data.additionalComments,
            "timestamp": datetime.utcnow()
        }
        
        db.feedback.insert_one(feedback_record)
        
        return {
            "message": "Feedback submitted successfully"
        }
    
    except Exception as e:
        print(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )

@app.on_event("startup")
async def startup_event():
    print("Personality Assessment API is starting up")

@app.on_event("shutdown")
async def shutdown_event():
    print("Personality Assessment API is shutting down")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=os.getenv("SERVER_HOST", "0.0.0.0"), 
        port=int(os.getenv("SERVER_PORT", 8000)), 
        reload=True
    )
