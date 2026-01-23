"""Simple test script for the Resume Extraction API"""
import requests
import json

# API endpoint
url = "http://localhost:8000/api/upload-resume"

# Test with a resume file
# Replace 'path/to/your/resume.pdf' with actual resume path
resume_path = r"C:\Users\njana\Desktop\Jan_resume.pdf"

print("Testing Resume Extraction API")
print("=" * 50)

try:
    # Open and upload the resume file
    with open(resume_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        
        print("\n✓ Success! Extracted Data:")
        print("-" * 50)
        print(f"Name: {result['name']}")
        print(f"ID: {result['id']}")
        print(f"Password: {result['password']}")
        print(f"\nSkills ({len(result['skills'])}):")
        for skill in result['skills']:
            print(f"  • {skill}")
        
        print("\n" + "=" * 50)
        print("\nFull JSON Response:")
        print(json.dumps(result, indent=2))
        
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)
        
except FileNotFoundError:
    print(f"\n✗ Error: Resume file not found at '{resume_path}'")
    print("\nPlease update the 'resume_path' variable with a valid resume file path.")
except requests.exceptions.ConnectionError:
    print("\n✗ Error: Could not connect to API server")
    print("\nMake sure the server is running:")
    print("  python backend/app/main.py")
except Exception as e:
    print(f"\n✗ Error: {e}")
