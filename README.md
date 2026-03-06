# Compass AI - Resume Extraction System

An AI-powered resume parser that extracts key information and generates user credentials.

## Features

-  **Resume Parsing**: Extracts data from PDF and DOCX files
-  **AI-Powered**: Uses Groq LLM (Llama 3.3 70B) for intelligent extraction
-  **Auto-Generate Credentials**: Creates user ID from initials and password
-  **Skills Extraction**: Identifies all technical and soft skills
-  **Multiple Interfaces**: FastAPI backend + Streamlit UI

## Output Format

The system returns a simplified JSON response:

```json
{
  "name": "John Doe",
  "id": "JD457",
  "password": "Xy8Kp2Qm",
  "skills": [
    "Python",
    "Machine Learning",
    "FastAPI",
    "Docker",
    "AWS"
  ]
}
```

- **name**: Full name from resume
- **id**: Auto-generated from name initials + random 3-digit number
- **password**: Auto-generated 8-character password
- **skills**: All detected technical and soft skills

## Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -r backend/app/requirements.txt
```

## Configuration

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0
MAX_TOKENS=8000
UPLOAD_DIR=temp
MAX_FILE_SIZE=10485760
```

## Usage

### Option 1: FastAPI Backend (API)

```bash
# Run the backend server
python backend/app/main.py
```

Server will start at `http://localhost:8000`

**API Endpoint:**

```bash
curl -X POST "http://localhost:8000/api/upload-resume" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "name": "Jane Smith",
  "id": "JS742",
  "password": "Zk3Lm9Rt",
  "skills": ["AWS", "Docker", "FastAPI", "Python"]
}
```

**API Documentation:** Visit `http://localhost:8000/docs`

### Option 2: Streamlit UI

```bash
# Run Streamlit interface
streamlit run frontend/streamlit_app.py
```

Features:
- 📤 Upload resume (PDF/DOCX)
- 👀 View extracted data with metrics
- 📥 Download credentials as text file
- 🎯 Skills displayed as tags

### Option 3: Python Script

```python
from backend.app.tools.resume_extractor_tool import extract_resume_data

result = extract_resume_data(resume_file_path="resume.pdf")
print(f"Name: {result['name']}")
print(f"ID: {result['id']}")
print(f"Password: {result['password']}")
print(f"Skills: {result['skills']}")
```

## Project Structure

```
compass_agent/
├── backend/
│   └── app/
│       ├── agents/          # AI agents
│       │   ├── resume_parser_agent.py       # Resume extraction
│       │   └── data_aggregation_agent.py    # Data merging
│       ├── api/             # FastAPI routes
│       │   ├── routes.py
│       │   └── schemas.py   # Pydantic models
│       ├── services/        # Core services
│       │   ├── llm_service.py              # Groq LLM
│       │   └── manager.py                  # Workflow orchestration
│       ├── tools/           # Reusable tools
│       │   └── resume_extractor_tool.py
│       ├── config.py        # Configuration
│       └── main.py          # API entrypoint
├── frontend/
│   └── streamlit_app.py     # Streamlit UI
├── .env                     # Environment variables
├── test_api.py              # API test script
└── README.md
```

## How It Works

1. **Upload Resume**: User uploads PDF/DOCX file via API or UI
2. **Text Extraction**: PyPDF2/python-docx extracts raw text
3. **Pattern Matching**: Regex extracts URLs, email, phone
4. **LLM Processing**: Groq LLM extracts structured data (skills, experience, education)
5. **Data Aggregation**: Merges and deduplicates all information
6. **Credential Generation**: Creates ID from initials and generates password
7. **Return Response**: Returns name, ID, password, and skills

## Technologies

- **FastAPI**: Modern web framework
- **Streamlit**: Interactive web UI
- **Groq**: LLM API (Llama 3.3 70B)
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX text extraction
- **Pydantic**: Data validation

## Example Flow

```
Resume File (PDF/DOCX)
    ↓
FastAPI Upload Endpoint
    ↓
Resume Parser Agent
    ├─ Text Extraction
    ├─ Regex Pattern Matching
    └─ LLM Extraction (Groq)
    ↓
Data Aggregation Agent
    ├─ Merge all data
    └─ Deduplicate skills
    ↓
Credential Generation
    ├─ ID: Initials + 3-digit number
    └─ Password: 8-char random
    ↓
JSON Response
{
  "name": "...",
  "id": "...",
  "password": "...",
  "skills": [...]
}
```

## API Testing

### Using Python requests:

```python
import requests

url = "http://localhost:8000/api/upload-resume"
files = {"file": open("resume.pdf", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

### Using httpx:

```python
import httpx

async with httpx.AsyncClient() as client:
    files = {"file": open("resume.pdf", "rb")}
    response = await client.post(
        "http://localhost:8000/api/upload-resume",
        files=files
    )
    print(response.json())
```

## Troubleshooting

### Streamlit showing "N/A" values
If the Streamlit UI shows "N/A" for all fields, restart the Streamlit server to clear module cache:
```bash
# Stop the server (Ctrl+C) and restart
streamlit run frontend/streamlit_app.py
```

### Module not found errors
Ensure you're running commands from the project root directory:
```bash
cd compass_agent
python backend/app/main.py  # or streamlit run frontend/streamlit_app.py
```

### API endpoint not responding
1. Check if the FastAPI server is running: `http://localhost:8000/docs`
2. Verify `.env` file contains valid `GROQ_API_KEY`
3. Check server logs for errors

### Resume extraction fails
- Ensure resume is in PDF or DOCX format
- Check file is not corrupted
- Verify file size is under 10MB
- Check Groq API key is valid and has quota
