import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Run the Streamlit app
import streamlit.web.cli as stcli
import streamlit as st

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app/streamlit_app.py"]
    sys.exit(stcli.main())