from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from typing_extensions import Annotated

# Pydantic Base User Model
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    user_type: str = Field(..., description="Type of user (Student/Faculty/Visitor/Other)")
    roll_number: Optional[str] = Field(None, description="Roll number for students")

    @validator('user_type')
    def validate_user_type(cls, v):
        valid_types = ['Student', 'Faculty', 'Visitor', 'Other']
        if v not in valid_types:
            raise ValueError(f"User type must be one of {valid_types}")
        return v

# Pydantic Model for Assessment Submission
class AssessmentSubmissionModel(BaseModel):
    user: UserBase
    question_answers: List[str] = Field(..., min_items=6, max_items=6, 
                                        description="6 question answers (A/B/C/D)")
    image_answers: List[str] = Field(default_factory=list, 
                                     description="Image perception test answers")

    @validator('question_answers')
    def validate_question_answers(cls, v):
        valid_options = ['A', 'B', 'C', 'D']
        for answer in v:
            if answer not in valid_options:
                raise ValueError(f"Invalid option. Must be one of {valid_options}")
        return v

# Pydantic Model for Personality Result
class PersonalityResultModel(BaseModel):
    user_id: str
    dominant_trait: Optional[str] = None
    detailed_result: str
    assessment_date: datetime = Field(default_factory=datetime.utcnow)

class FeedbackSubmission(BaseModel):
    feedbackScores: Dict[str, int] = Field(
        ..., 
        description="Feedback scores for different aspects of the assessment"
    )
    additionalComments: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Optional additional feedback comments"
    )

    @validator('feedbackScores')
    def validate_feedback_scores(cls, v):
        # Required keys for feedback
        required_keys = [
            'personalityRating', 
            'scenarioRating', 
            'accuracyRating', 
            'engagementRating', 
            'insightRating', 
            'recommendRating'
        ]
        
        # Check that all required keys are present
        missing_keys = set(required_keys) - set(v.keys())
        if missing_keys:
            raise ValueError(f"Missing feedback keys: {missing_keys}")
        
        # Validate each score
        for key, score in v.items():
            if not 1 <= score <= 5:
                raise ValueError(f"Score for {key} must be between 1 and 5")
        
        return v
# MongoDB Document Models (for PyMongo)
class MongoUserDocument:
    def __init__(self, user_data: UserBase):
        self.document = {
            "_id": str(ObjectId()),
            "name": user_data.name,
            "user_type": user_data.user_type,
            "roll_number": user_data.roll_number,
            "created_at": datetime.utcnow()
        }

class MongoAssessmentDocument:
    def __init__(self, assessment: AssessmentSubmissionModel, personality_result: str):
        self.document = {
            "_id": str(ObjectId()),
            "user_id": str(ObjectId()),
            "question_answers": assessment.question_answers,
            "image_answers": assessment.image_answers,
            "personality_result": personality_result,
            "assessment_date": datetime.utcnow()
        }

class MongoFeedbackDocument:
    def __init__(self, feedback: FeedbackModel):
        self.document = {
            "_id": str(ObjectId()),
            "user_id": feedback.userId,
            "feedback_scores": feedback.feedbackScores,
            "additional_comments": feedback.additionalComments,
            "submission_date": feedback.submissionDate
        }

# Custom Type for MongoDB Object ID
PyObjectId = Annotated[str, Field(alias="_id")]

# Validation Utility Functions
def validate_assessment_data(data: dict):
    """
    Validate raw assessment data before database insertion
    """
    try:
        return AssessmentSubmissionModel(**data)
    except Exception as e:
        raise ValueError(f"Invalid assessment data: {str(e)}")

def validate_feedback_data(data: dict):
    """
    Validate raw feedback data before database insertion
    """
    try:
        return FeedbackModel(**data)
    except Exception as e:
        raise ValueError(f"Invalid feedback data: {str(e)}")

# Enum-like Constants
class AssessmentConstants:
    VALID_QUESTION_OPTIONS = ['A', 'B', 'C', 'D']
    USER_TYPES = ['Student', 'Faculty', 'Visitor', 'Other']
    FEEDBACK_SCALE = range(1, 6)  # 1 to 5