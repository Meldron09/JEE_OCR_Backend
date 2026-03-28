import os
from dotenv import load_dotenv

load_dotenv()

AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
UPLOAD_FOLDER = "input"
PRESIGNED_URL_EXPIRATION = 300
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
