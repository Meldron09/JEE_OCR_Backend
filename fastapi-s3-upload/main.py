from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
import boto3
import uuid
import requests
import os

from config import AWS_DEFAULT_REGION, S3_BUCKET, UPLOAD_FOLDER, PRESIGNED_URL_EXPIRATION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DYNAMODB_TABLE

app = FastAPI(title="JEE OCR Processing Service")

s3_client = boto3.client(service_name="s3", region_name=AWS_DEFAULT_REGION, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID, 
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

dynamodb = boto3.resource(service_name="dynamodb", region_name=AWS_DEFAULT_REGION, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID, 
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

table = dynamodb.Table(DYNAMODB_TABLE)

# -----------------------------
# Request Models
# -----------------------------
class PresignedUrlRequest(BaseModel):
    file_name: str
    content_type: str


# -----------------------------
# 1️⃣ Generate Presigned URL
# -----------------------------
@app.post("/generate-presigned-url")
def generate_presigned_url(payload: PresignedUrlRequest):

    try:
        task_id=str(uuid.uuid4())
        unique_file_name = f"{task_id}_{payload.file_name}"
        object_key = f"{UPLOAD_FOLDER}/{unique_file_name}"

        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": object_key,
                "ContentType": payload.content_type
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        # Create DynamoDB entry
        table.put_item(
            Item={
                "task_id": task_id,
                "status": "PENDING",
                "input_s3_key": object_key
            }
        )
        return {
            "task_id": task_id,
            "upload_url": presigned_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# 2️⃣ Upload File Using Presigned URL
# -----------------------------
@app.post("/upload-to-s3")
async def upload_to_s3(
    presigned_url: str = Form(...),
    file: UploadFile = File(...)
):

    try:
        file_content = await file.read()

        response = requests.put(
            presigned_url,
            data=file_content,
            headers={
                "Content-Type": file.content_type
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Upload to S3 failed"
            )

        return {
            "message": "File uploaded successfully",
            "file_name": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# 3️⃣ Get Processing Status
# -----------------------------
@app.get("/get-processing-status")
def get_processing_status(task_id: str):
    try:
        response = table.get_item(Key={"task_id": task_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Task not found")

        status = item["status"]

        result = {
            "task_id": item["task_id"],
            "status": status
        }

        if status == "COMPLETED":
            output_s3_key = item.get("output_s3_key")
            if not output_s3_key:
                raise HTTPException(
                    status_code=500,
                    detail="Task completed but output key is missing"
                )

            # Ensure prefix ends with /
            prefix = output_s3_key if output_s3_key.endswith("/") else output_s3_key + "/"

            # list_objects_v2 with Prefix recursively lists ALL files
            # in all subdirectories automatically
            paginator = s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)

            files = []
            for page in pages:
                for obj in page.get("Contents", []):
                    key = obj["Key"]

                    # Skip folder placeholder entries (e.g. "output/folder/")
                    if key.endswith("/"):
                        continue

                    # Get relative path from the output folder root
                    # e.g. "output/uuid_test/subdir/file.json" -> "subdir/file.json"
                    relative_path = key[len(prefix):]

                    download_url = s3_client.generate_presigned_url(
                        ClientMethod="get_object",
                        Params={"Bucket": S3_BUCKET, "Key": key},
                        ExpiresIn=PRESIGNED_URL_EXPIRATION
                    )

                    files.append({
                        "file_name": key.split("/")[-1],   # just filename
                        "relative_path": relative_path,    # path within output folder
                        "s3_key": key,                     # full S3 path
                        "download_url": download_url,      # presigned URL
                        "size_bytes": obj["Size"]          # file size
                    })

            if not files:
                raise HTTPException(
                    status_code=500,
                    detail=f"No files found in output folder: {prefix}"
                )

            result["output_folder"] = prefix
            result["files"] = files
            result["total_files"] = len(files)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))