# JEE OCR Backend

A FastAPI-based OCR processing service for JEE (Joint Entrance Examination) that handles file uploads to AWS S3 and tracks processing status in DynamoDB.

## Prerequisites

- Python 3.8+
- AWS account with S3 and DynamoDB access
- AWS credentials with appropriate permissions

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r fastapi-s3-upload/requirements.txt
   ```
4. Configure environment variables (see below)

## Configuration

Copy `.env.example` to `.env` and fill in your AWS credentials:

```bash
cp fastapi-s3-upload/.env.example fastapi-s3-upload/.env
```

Then edit `.env` with your actual AWS credentials.

## Running the Server

```bash
cd fastapi-s3-upload
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at http://localhost:8000/docs

## API Endpoints

### POST /generate-presigned-url

Generates a presigned S3 URL for direct client upload. Creates a DynamoDB task entry with status "PENDING".

**Request Body:**
```json
{
  "file_name": "example.pdf",
  "content_type": "application/pdf",
  "output_prefix": "results/user123/"
}
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "presigned_url": "https://bucket.s3.amazonaws.com/...",
  "s3_key": "input/uuid-string/example.pdf"
}
```

### POST /upload-to-s3

Alternative endpoint for direct file upload via presigned URL.

**Request Body:**
```json
{
  "file_name": "example.pdf",
  "content_type": "application/pdf",
  "file_content": "base64-encoded-content",
  "output_prefix": "results/user123/"
}
```

### GET /get-processing-status?task_id=X

Returns task status from DynamoDB.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "PENDING|COMPLETED|FAILED",
  "input_s3_key": "input/uuid-string/example.pdf",
  "output_s3_key": "results/user123/output.pdf",
  "output_urls": ["https://..."]  // Only when COMPLETED
}
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_DEFAULT_REGION` | AWS region | `ap-south-1` |
| `S3_BUCKET` | S3 bucket name | `jee-ocr-bucket` |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `your-secret-key` |
| `DYNAMODB_TABLE` | DynamoDB table name | `FileTasks` |

## AWS Infrastructure

- **S3 Bucket**: Files are uploaded to `input/` prefix; OCR results stored in user-specified output prefixes
- **DynamoDB Table**: Tracks task_id, status (PENDING/COMPLETED), input_s3_key, and output_s3_key
- **Region**: ap-south-1 (Mumbai)
