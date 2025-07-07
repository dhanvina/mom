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

# Setup the MoM generator
if st.button("Generate Minutes of Meeting"):
    with st.spinner("Setting up the model..."):
        ok, msg = mom_generator.setup()
        if not ok:
            st.error(msg)
        else:
            try:
                result = mom_generator.generate_mom(transcript_text)
                st.success("Minutes of Meeting generated successfully!")
                st.subheader("Structured:")
                st.markdown(result)

                st.download_button(
                    label="Download Now!",
                    data=result,
                    file_name="minutes_of_meeting.txt",
                    mime="text/plain"
                )

                st.subheader("Raw Transcript:")
                st.markdown(transcript_text)        
            except RuntimeError as e:
                st.error(f"Error generating MoM: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Failed {e}")
            else:
                st.info("please upload or paste the transcript text to generate MoM.")

