# [file name]: parent_auth.py
# [file content begin]
# type:ignore
import streamlit as st
import json
import os
from datetime import datetime
from hashlib import sha256
import re

def validate_email(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def hash_password(password):
    """Hash a password for storing"""
    return sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return stored_password == sha256(provided_password.encode('utf-8')).hexdigest()

def initialize_parent_db():
    """Initialize the parent database if it doesn't exist"""
    if not os.path.exists("parents.json"):
        with open("parents.json", 'w') as f:
            json.dump({}, f)

def authenticate_parent(email, password):
    """Authenticate a parent user"""
    try:
        initialize_parent_db()
        with open("parents.json", 'r') as f:
            parents = json.load(f)
        
        if email in parents:
            parent_data = parents[email]
            if verify_password(parent_data['password'], password):
                st.session_state.parent_authenticated = True
                st.session_state.parent_email = email
                st.session_state.parent_name = parent_data.get('parent_name', 'Parent')
                st.session_state.student_ids = parent_data.get('student_ids', [])
                return True
        return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def create_parent_account(email, password, parent_name, student_ids, phone=""):
    """Create a new parent account"""
    try:
        initialize_parent_db()
        with open("parents.json", 'r') as f:
            parents = json.load(f)
        
        if not validate_email(email):
            return False, "Please use a valid email address"
        
        if email in parents:
            return False, "Email already registered. Please login instead."
        
        parents[email] = {
            "password": hash_password(password),
            "parent_name": parent_name,
            "student_ids": student_ids,
            "phone": phone,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active"
        }
        
        with open("parents.json", 'w') as f:
            json.dump(parents, f, indent=4)
        
        return True, "Parent account created successfully"
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def check_parent_authentication():
    """Check if parent is authenticated"""
    if 'parent_authenticated' not in st.session_state:
        st.session_state.parent_authenticated = False
    if 'parent_email' not in st.session_state:
        st.session_state.parent_email = None
    if 'parent_name' not in st.session_state:
        st.session_state.parent_name = None
    if 'student_ids' not in st.session_state:
        st.session_state.student_ids = []
    
    return st.session_state.parent_authenticated

def logout_parent():
    """Logout parent and clear session state"""
    st.session_state.parent_authenticated = False
    st.session_state.parent_email = None
    st.session_state.parent_name = None
    st.session_state.student_ids = []
    st.session_state.is_parent_portal = False
# [file content end]