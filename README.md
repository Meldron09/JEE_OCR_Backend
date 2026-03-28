# JEE OCR Processing Service

FastAPI-based OCR processing service for JEE (Joint Entrance Examination) that handles file uploads to AWS S3 and tracks processing status in DynamoDB.

## Architecture

```
Client → FastAPI → S3 (input/) → External OCR Processor → S3 (output/)
                → DynamoDB (status tracking) ← External OCR Processor
```

### Workflow

1. **Upload File** (`POST /upload-file`): Client uploads a file, which is stored in S3 under `input/`. A task entry is created in DynamoDB with status `PENDING`.
2. **External OCR Processor**: Reads files from S3 `input/`, processes them, writes results to `output/{task_id}/`, and updates DynamoDB status to `COMPLETED`.
3. **Get Status** (`GET /get-processing-status`): Returns current task status and, when completed, lists all output files with presigned download URLs.

## API Endpoints

### `POST /upload-file`

Upload a file for OCR processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary file data)

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully"
}
```

### `GET /get-processing-status`

Check the processing status of a task.

**Query Parameters:**
- `task_id` (required): The UUID returned from the upload endpoint

**Response (Pending):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING"
}
```

**Response (Completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "output_folder": "output/550e8400-e29b-41d4-a716-446655440000/",
  "files": [
    {
      "file_name": "result.json",
      "relative_path": "result.json",
      "s3_key": "output/550e8400-e29b-41d4-a716-446655440000/result.json",
      "download_url": "https://s3.ap-south-1.amazonaws.com/...",
      "size_bytes": 1234
    }
  ],
  "total_files": 1
}
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `fastapi-s3-upload/` directory:

```env
AWS_DEFAULT_REGION=ap-south-1
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
DYNAMODB_TABLE=your-table-name
```

### 3. Run the Server

```bash
uvicorn main:app --reload
```

The API runs on `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

## AWS Infrastructure

| Component | Details |
|-----------|---------|
| S3 Bucket | Files uploaded to `input/` prefix; OCR results stored in `output/{task_id}/` |
| DynamoDB Table | Tracks `task_id`, `status` (PENDING/COMPLETED), `input_s3_key`, `output_s3_key` |
| Region | ap-south-1 (Mumbai) |

## Project Structure

```
fastapi-s3-upload/
├── main.py          # FastAPI application with endpoints
├── config.py        # AWS configuration from environment variables
├── requirements.txt # Python dependencies
├── .env.example     # Example environment variables
└── README.md        # This file
```
