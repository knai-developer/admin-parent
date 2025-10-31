# trail day set 118
# type:ignore
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from hashlib import sha256
import re
# ________________sensitive data______________________________________
import smtplib

# Email configuration
GMAIL_ID = "nidakhurramalvi9@gmail.com"
GMAIL_PSW = "zhkk ubtv saeo huxu"

def send_signup_notification(username, user_email):
    """Send email notification when a new user signs up"""
    sub = "New User Registration - School Fees Management System"
    msg = f"""
New user registration details:

Username: {username}
User Email: {user_email}
Registration Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This is an automated notification from School Fees Management System.

Best regards,
School Management System
"""

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(GMAIL_ID, GMAIL_PSW)
        s.sendmail("School Management System", GMAIL_ID, f"Subject: {sub}\n\n{msg}")
        s.quit()
        print(f"Signup notification sent for user: {username}")
        return True
    except Exception as e:
        print(f"Failed to send signup notification: {str(e)}")
        return False
# ________________sensitive data______________________________________

def validate_email(email):
    """Validate email format and ensure it's a Gmail address"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(email_pattern, email) is not None

def hash_password(password):
    """Hash a password for storing"""
    return sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return stored_password == sha256(provided_password.encode('utf-8')).hexdigest()

def initialize_user_db():
    """Initialize the user database if it doesn't exist"""
    if not os.path.exists("users.json"):
        with open("users.json", 'w') as f:
            json.dump({}, f)

def authenticate_user(username, password):
    """Authenticate a user and check trial status"""
    try:
        initialize_user_db()
        with open("users.json", 'r') as f:
            users = json.load(f)
        
        if username in users:
            if verify_password(users[username]['password'], password):
                from database import load_school_config
                school_config = load_school_config()
                school_name = school_config.get("school_name", "Your School Name")
                
                # Set session state variables
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.is_admin = users[username].get('is_admin', False)
                st.session_state.school_name = school_name
                
                # Check trial status
                trial_end = users[username].get('trial_end')
                if trial_end:
                    trial_end_date = datetime.strptime(trial_end, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() > trial_end_date:
                        st.session_state.authenticated = False
                        st.error("Your free trial has expired. Please contact support.")
                        return False
                    remaining = trial_end_date - datetime.now()
                    st.session_state.trial_remaining = format_trial_remaining(remaining)
                else:
                    st.session_state.trial_remaining = None
                
                return True
        return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def create_user(username, password, email, is_admin=False):
    """Create a new user account with email and 1-month trial"""
    try:
        initialize_user_db()
        with open("users.json", 'r') as f:
            users = json.load(f)
        
        if not validate_email(email):
            return False, "Please use a valid Gmail address (e.g., username@gmail.com)"
        
        # Check if username already exists
        if username in users:
            return False, "Username already exists. Please choose a different username."
        
        # Check for email uniqueness
        for user in users.values():
            if 'email' in user and user['email'] == email:
                return False, "This Gmail address is already registered. Please use a different Gmail address or log in."
        
        trial_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trial_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                
        users[username] = {
            "password": hash_password(password),
            "is_admin": is_admin,
            "email": email,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trial_start": trial_start,
            "trial_end": trial_end
        }
        
        with open("users.json", 'w') as f:
            json.dump(users, f)
        
        return True, "User created successfully"
    except Exception as e:
        return False, f"Error creating user: {str(e)}"

def check_authentication():
    """Check if user is authenticated"""
    # Initialize session state if it doesn't exist
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'trial_remaining' not in st.session_state:
        st.session_state.trial_remaining = None
    if 'selected_nav_menu' not in st.session_state:
        st.session_state.selected_nav_menu = None
    if 'school_name' not in st.session_state:
        from database import load_school_config
        school_config = load_school_config()
        st.session_state.school_name = school_config.get("school_name", "Your School Name")
    
    return st.session_state.authenticated

def logout():
    """Logout user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.is_admin = False
    st.session_state.show_login = False
    st.session_state.menu = None
    st.session_state.form_key = 0
    st.session_state.available_months = []
    st.session_state.current_student_id = None
    st.session_state.last_saved_records = None
    st.session_state.last_student_name = ""
    st.session_state.last_student_phone = ""
    st.session_state.last_class_category = None
    st.session_state.last_class_section = ""
    st.session_state.trial_remaining = None
    st.session_state.selected_nav_menu = None
    from database import load_school_config
    school_config = load_school_config()
    st.session_state.school_name = school_config.get("school_name", "Your School Name")

def format_trial_remaining(remaining):
    """Format remaining trial time"""
    if remaining is None:
        return "No trial period"
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

def login_page():
    """Display login page with signup option"""
    # Add a back button with better styling
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Back to Home", use_container_width=True):
            st.session_state.show_login = False
            st.rerun()
    
    st.title("🔒 School Fees Management - Login / Sign Up")
        
    tabs = st.tabs(["✨ Sign Up", "🔐 Login"])
    
    with tabs[0]:
        with st.form("signup_form"):
            st.markdown("### Create New Account")
            new_username = st.text_input("Username*", help="Choose a unique username")
            new_email = st.text_input("Gmail Address*", placeholder="yourname@gmail.com", help="Only the Gmail address used to access this app is allowed.")
            new_password = st.text_input("Password*", type="password", key="signup_pass")
            confirm_password = st.text_input("Confirm Password*", type="password", key="signup_confirm")
            is_admin = st.checkbox("Register as Admin User")
            show_password = st.checkbox("Show Password")
            
            if show_password:
                st.text(f"Password will be: {new_password if new_password else '[not set]'}")
            
            signup_submit = st.form_submit_button("🎉 Sign Up (Start 1-month Free Trial)") 
            
            if signup_submit:
                if not new_username or not new_password or not new_email:
                    st.error("Username, password, and Gmail address are required!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long!")
                else:
                    success, message = create_user(new_username, new_password, new_email, is_admin)
                    if success:
                        st.success(f"{message} Your 1-month free trial has started!") 
                        st.info(f"User '{new_username}' created with email: {new_email}")
                        
                        # Send email notification ONLY ONCE here
                        with st.spinner("Sending registration notification..."):
                            if send_signup_notification(new_username, new_email):
                                st.success("Registration notification sent to admin!")
                            else:
                                st.warning("User created but couldn't send notification email")
                        
                        if authenticate_user(new_username, new_password):
                            st.rerun()
                    else:
                        st.error(message)

    with tabs[1]:
        with st.form("login_form"):
            st.markdown("### Login to Your Account")
            username = st.text_input("Username*", help="Enter your username")
            password = st.text_input("Password*", type="password", help="Enter your password")
            submit = st.form_submit_button("🚀 Login")
            
            if submit:
                if not username or not password:
                    st.error("Please enter username and password!")
                elif authenticate_user(username, password):
                    st.success(f"Welcome {username}! 🎊")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    # Add some helpful information
    st.markdown("---")
    st.markdown("""
    **📝 Note for new users:**
    - You must sign up with a valid Gmail address
    - Your free trial will last for 1 month (30 days)
    - After the trial period, you'll need to contact support to continue using the app
    - Keep your login credentials secure
    - Admin will be notified of your registration automatically
    """)

# Main app execution
if __name__ == "__main__":
    # Initialize session state
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    
    # Show login page if requested, otherwise show home page
    if st.session_state.show_login:
        login_page()
    else:
        # You would call your home_page() function here
        st.title("School Fees Management System")
        st.write("Welcome to the School Fees Management System")
        if st.button("Login / Sign Up"):
            st.session_state.show_login = True
            st.rerun()
