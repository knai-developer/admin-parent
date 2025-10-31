# [file name]: main.py
# [file content begin]
# type:ignore
import streamlit as st
from auth import check_authentication, logout, login_page
from home import home_page
from fees_entry import fees_entry_page
from reports import reports_page
from admin import admin_page, set_default_fees
from utils import hide_streamlit_elements, navbar_collapsible_component
from database import initialize_files, load_school_config
from datetime import datetime
from payment_config import payment_config_page
from real_payment_system import real_payment_page
from jazz_cash import jazzcash_payment_page
from easy_paisa import easypaisa_payment_page

def is_parent_portal():
    """Check if the app is being accessed via parent portal link"""
    try:
        # Use the new query_params API
        query_params = st.query_params
        # Check for parent parameter in URL
        if 'parent' in query_params and query_params['parent'].lower() in ['true', '1', 'yes']:
            return True
        
        # Check for direct parent portal access
        if 'parent_portal' in query_params and query_params['parent_portal'].lower() in ['true', '1', 'yes']:
            return True
            
    except:
        pass
    
    return st.session_state.get('is_parent_portal', False)

def main():
    # Initialize files and hide elements
    initialize_files()
    hide_streamlit_elements()
    
    school_config = load_school_config()
    school_name = school_config.get("school_name", "School Fees Management")
    
    # Initialize session state if it doesn't exist
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'is_parent_portal' not in st.session_state:
        st.session_state.is_parent_portal = is_parent_portal()
    
    # If parent portal, show parent interface
    if st.session_state.is_parent_portal:
        from parent_portal import parent_portal_page
        parent_portal_page()
        return
    
    # Check authentication status for admin portal
    is_authenticated = check_authentication()
    
    # If not authenticated, show home page or login page
    if not is_authenticated:
        if st.session_state.show_login:
            login_page()
        else:
            home_page()
        return
    
    # If authenticated, show main app with navbar
    st.set_page_config(page_title=f"{school_name} - Fees Management", layout="wide")
    
    # Define navigation options based on user role
    if st.session_state.is_admin:
        menu_options = [
            "Dashboard", 
            "Enter Fees", 
            "View All Records", 
            "Paid & Unpaid Students Record", 
            "Student Yearly Report"
        ]
        
        today = datetime.now()
        if today.day >= 8:
            menu_options.insert(1, "📢 Fee Reminder")
    else:
        # Regular users (parents/staff) see different menu
        menu_options = [
            "Parent Portal", 
            "Enter Fees", 
            "View Records"
        ]
    
    # Display navbar and get selected menu
    selected_menu = navbar_collapsible_component(menu_options)
    
    # Route to appropriate page based on navbar selection
    if selected_menu == "Dashboard":
        from admin_dashboard import admin_dashboard
        admin_dashboard()
    elif selected_menu == "Enter Fees":
        fees_entry_page()
    elif selected_menu in ["View All Records", "Paid & Unpaid Students Record", "Student Yearly Report"]:
        reports_page(selected_menu)
    elif selected_menu == "📢 Fee Reminder":
        from reminder import fee_reminder_page
        fee_reminder_page()
    elif selected_menu == "Parent Portal":
        from parent_portal import parent_portal_page
        parent_portal_page()
    elif selected_menu == "View Records":
        reports_page("View All Records")

if __name__ == "__main__":
    main()
# [file content end]