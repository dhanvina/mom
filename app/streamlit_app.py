import streamlit as st
from utils.file_utils import FileHandler
from main import MoMGenerator

# page configuration
st.set_page_config(
    page_title='Minutes of Meeting Generator',
    page_icon=':memo:',
    layout='wide')
st.title("Minutes of Meeting")

# Initialize file handler and MoM generator
file_handler = FileHandler()
mom_generator = MoMGenerator()

# file upload and input section
st.sidebar.header("Upload Transcript")
uploaded_file = file_handler.upload_file()
if uploaded_file:
    st.sidebar.success(f"File '{uploaded_file.name}' uploaded successfully.")
else:
    st.sidebar.warning("Please upload a transcript file (.txt or .docx).")

# manual text input section
transcript_text = file_handler.text_input_area()
if transcript_text:
    st.sidebar.success("Text input received.")
else:
    st.sidebar.warning("Please enter the transcript text manually.")
# Combine uploaded file content and manual text input
if uploaded_file and transcript_text:   
    st.sidebar.info("Both file upload and manual text input are provided. Using file content.")
    transcript_text = file_handler.read_file_content(uploaded_file)
elif not uploaded_file and not transcript_text:
    st.sidebar.error("Please provide either a file upload or manual text input to generate MoM.")
    st.stop()

lower_text = transcript_text.lower()
location = ""
date = ""
time = ""

missing_fields = []

if "location" not in lower_text:
    location = st.sidebar.text_input("Enter Meeting Location", placeholder="e.g., Zoom / HQ")
    if not location:
        missing_fields.append("location")

if "date" not in lower_text:
    date_input = st.sidebar.date_input("Enter Meeting Date")
    date = date_input.strftime("%Y-%m-%d") if date_input else ""
    if not date:
        missing_fields.append("date")

if "time" not in lower_text:
    time = st.sidebar.text_input("Enter Meeting Time", placeholder="e.g., 10:00 AM")
    if not time:
        missing_fields.append("time")

# Only show generate button when transcript and all required info are present
if missing_fields:
    st.warning(f"Please provide missing information: {', '.join(missing_fields)}")
    st.stop()

# Setup the MoM generator
if st.button("Generate Minutes of Meeting"):
    with st.spinner("Setting up the model..."):
        ok, msg = mom_generator.setup()
        if not ok:
            st.error(msg)
        else:
            try:
                metadata = ""
                if location:
                    metadata += f"\nLocation: {location}"
                if date:
                    metadata += f"\nDate: {date}"
                if time:
                    metadata += f"\nTime: {time}"

                final_text = metadata + "\n" + transcript_text
                mom_data = mom_generator.generate_mom(final_text)

                # Display the raw text output from LLM
                st.success("Minutes of Meeting generated successfully!")
                st.subheader("Generated MoM:")
                st.markdown(mom_data)

                st.download_button(
                    label="Download Now!",
                    data=mom_data,
                    file_name="minutes_of_meeting.txt",
                    mime="text/plain"
                )
            except RuntimeError as e:
                st.error(f"Error generating MoM: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Failed {e}")