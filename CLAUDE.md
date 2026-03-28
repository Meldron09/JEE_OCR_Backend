# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based OCR processing service for JEE (Joint Entrance Examination) that handles file uploads to AWS S3 and tracks processing status in DynamoDB.

## Common Commands

```bash
# Install dependencies
pip install -r fastapi-s3-upload/requirements.txt

# Run the server
cd fastapi-s3-upload && uvicorn main:app --reload

# The API runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

## Architecture

The application lives in `fastapi-s3-upload/`:

- **main.py** - FastAPI application with two endpoints:
  - `POST /upload-file` - Accepts a multipart file upload, stores it in S3 under `input/`, and creates a DynamoDB task entry with status "PENDING"
  - `GET /get-processing-status?task_id=X` - Returns task status from DynamoDB; when "COMPLETED", lists all output files with presigned download URLs

- **config.py** - Loads AWS credentials and configuration from environment variables via `python-dotenv`

## AWS Infrastructure

- **S3 Bucket**: Files are uploaded to `input/` prefix; OCR results stored in user-specified output prefixes
- **DynamoDB Table**: Tracks task_id, status (PENDING/COMPLETED), input_s3_key, and output_s3_key
- **Region**: ap-south-1 (Mumbai)

## Environment Variables

Configuration is loaded from `fastapi-s3-upload/.env`:
- `AWS_DEFAULT_REGION`, `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DYNAMODB_TABLE`
