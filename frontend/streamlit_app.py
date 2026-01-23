"""Streamlit UI for Resume Extraction System"""
import streamlit as st
import sys
import os
import tempfile
import importlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and force reload to clear any cached modules
from backend.app.tools import resume_extractor_tool
importlib.reload(resume_extractor_tool)
from backend.app.tools.resume_extractor_tool import extract_resume_data

st.set_page_config(page_title="Resume Extraction System", page_icon="📄", layout="centered")

st.title("📄 Resume Extraction System")
st.markdown("Upload a resume to extract **name, ID, password, and skills**")

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "doc"])

if uploaded_file is not None:
    if st.button("Extract Data", type="primary"):
        with st.spinner("Extracting data from resume..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            try:
                # Extract data
                result = extract_resume_data(resume_file_path=tmp_path)
                
                # Clean up
                os.remove(tmp_path)
                
                # Debug: Show the actual result structure
                st.write("DEBUG - Result keys:", list(result.keys()) if result else "None")
                st.write("DEBUG - Full result:", result)
                
                if result.get("status") == "error":
                    st.error(f"❌ Error: {result.get('message')}")
                else:
                    st.success("✅ Resume extracted successfully!")
                    
                    # Create a nice card layout
                    st.markdown("---")
                    
                    # Display extracted data
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Name", result.get("name", "N/A"))
                        st.metric("User ID", result.get("id", "N/A"))
                    
                    with col2:
                        st.metric("Password", result.get("password", "N/A"))
                        st.metric("Skills Found", len(result.get("skills", [])))
                    
                    # Display skills
                    st.markdown("### 🎯 Skills")
                    skills = result.get("skills", [])
                    if skills:
                        # Display skills as tags
                        skill_tags = " ".join([f"`{skill}`" for skill in skills])
                        st.markdown(skill_tags)
                    else:
                        st.info("No skills found")
                    
                    # Download credentials as text
                    st.markdown("---")
                    credentials_text = f"""Resume Extraction Results
=========================

Name: {result.get('name', 'N/A')}
ID: {result.get('id', 'N/A')}
Password: {result.get('password', 'N/A')}

Skills ({len(skills)}):
{chr(10).join([f'- {skill}' for skill in skills])}
"""
                    st.download_button(
                        label="📥 Download Credentials",
                        data=credentials_text,
                        file_name=f"{result.get('id', 'user')}_credentials.txt",
                        mime="text/plain"
                    )
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

# Footer
st.markdown("---")
st.markdown("**Note:** Keep your credentials secure. This system generates a unique ID and password for each resume.")
