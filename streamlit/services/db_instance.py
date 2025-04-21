# services/db_instance.py
import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database.DatabaseCRUD import DatabaseCRUD

@st.cache_resource
def get_db():
    return DatabaseCRUD()