# services/db_instance.py
import streamlit as st
from database.DatabaseCRUD import DatabaseCRUD

@st.cache_resource
def get_db():
    return DatabaseCRUD()