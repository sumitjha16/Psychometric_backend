from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("DATABASE_NAME", "personality_assessment")

client = MongoClient(mongo_uri)
db = client[database_name]

# Fetch the latest submitted assessment
latest_assessment = db.assessments.find_one(sort=[("_id", -1)])

if latest_assessment:
    print("✅ Latest Assessment Data:")
    print(latest_assessment)
else:
    print("⚠ No data found in the 'assessments' collection.")
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("DATABASE_NAME", "personality_assessment")

client = MongoClient(mongo_uri)
db = client[database_name]

# Fetch the latest submitted assessment
latest_assessment = db.assessments.find_one(sort=[("_id", -1)])

if latest_assessment:
    print("✅ Latest Assessment Data:")
    print(latest_assessment)
else:
    print("⚠ No data found in the 'assessments' collection.")
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
database_name = os.getenv("DATABASE_NAME", "personality_assessment")

client = MongoClient(mongo_uri)
db = client[database_name]

# Fetch the latest submitted assessment
latest_assessment = db.assessments.find_one(sort=[("_id", -1)])

if latest_assessment:
    print("✅ Latest Assessment Data:")
    print(latest_assessment)
else:
    print("⚠ No data found in the 'assessments' collection.")
