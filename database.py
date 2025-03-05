from pymongo import MongoClient

class DatabaseConnection:
    def __init__(self, connection_string="mongodb://localhost:27017/"):
        self.client = MongoClient(connection_string)
        self.db = self.client["personality_assessment"]
        
        # Create collections
        self.user_collection = self.db["users"]
        self.questions_collection = self.db["questions"]
        self.personality_results_collection = self.db["personality_results"]
        self.feedback_collection = self.db["feedback"]

    def insert_user(self, user_data):
        return self.user_collection.insert_one(user_data)

    def insert_question_answers(self, answers_data):
        return self.questions_collection.insert_one(answers_data)

    def insert_personality_result(self, result_data):
        return self.personality_results_collection.insert_one(result_data)

    def insert_feedback(self, feedback_data):
        return self.feedback_collection.insert_one(feedback_data)