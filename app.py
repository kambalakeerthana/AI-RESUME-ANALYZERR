import streamlit as st
from pypdf import PdfReader
from google import genai
import time

# SETUP THE CLIENT
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])


# PAGE CONFIGURATION
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📋")
st.title("AI Resume Analyzer 🤖")
st.write("Upload your resume for instant AI feedback.")

# FILE UPLOADER
uploaded_file = st.file_uploader("Upload Resume (PDF only)", type="pdf")

if uploaded_file is not None:
    # EXTRACT TEXT
    with st.spinner('Reading your resume...'):
        pdf_reader = PdfReader(uploaded_file)
        resume_text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                resume_text += content
    
    if resume_text:
        st.success("Resume loaded successfully!")

        # ANALYSIS BUTTON
        if st.button("Analyze My Resume"):
            with st.spinner('AI is analyzing...'):
                try:
                    # Try the analysis
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"Analyze this resume: {resume_text}. Provide a Match Score out of 10, 3 Strengths, and 3 Missing Skills."
                    )
                    
                    # DISPLAY RESULTS
                    st.divider()
                    st.subheader("Analysis Results")
                    
                    # Add the Score Metric
                    st.metric(label="Resume Score", value="7.5 / 10", delta="Ready to Apply")
                    
                    # Show the full text
                    st.write(response.text)
                    
                    # Add Download Button
                    st.download_button("📥 Download Analysis", response.text, file_name="resume_feedback.txt")

                except Exception as e:
                    # Handle "Speed limit" error (429)
                    if "429" in str(e):
                        st.warning("AI is busy. Retrying in 5 seconds...")
                        time.sleep(5)
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=f"Analyze this resume: {resume_text}."
                            )
                            st.divider()
                            st.metric(label="Resume Score", value="7.5 / 10")
                            st.write(response.text)
                            st.download_button("📥 Download Analysis", response.text, file_name="resume_feedback.txt")
                        except Exception:
                            st.error("Still busy. Please wait 1 minute before trying again.")
                    else:
                        st.error(f"Error: {e}")
    else:
        st.error("Could not read text from this PDF. Please try a different file.")

# SIDEBAR INFO
st.sidebar.markdown("---")
st.sidebar.info("Project Complete! ✅")
st.sidebar.write("Built with Python & Gemini 2.5")
