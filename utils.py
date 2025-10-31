# [file name]: utils.py
# [file content begin]
#type:ignore
import streamlit as st
import pandas as pd
from datetime import datetime
from database import load_data
from auth import logout

def hide_streamlit_elements():
    """Hide all Streamlit default elements including GitHub icon and deploy button"""
    st.markdown("""
    <style>
    /* Hide ALL Streamlit toolbar elements */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Hide GitHub icon */
    button[title="View app source on GitHub"] {
        display: none !important;
    }
    
    /* Hide deploy button */
    .stApp > header > div:first-child {
        display: none !important;
    }
    
    /* Hide the entire header */
    header {
        display: none !important;
    }
    
    /* Hide any remaining toolbar buttons */
    .stToolbar {
        display: none !important;
    }
    
    /* Hide the Streamlit hamburger menu */
    #MainMenu {
        display: none !important;
    }
    
    /* Alternative selectors for header elements */
    .stApp > header {
        display: none !important;
    }
    
    /* Hide any element that might contain the warning text */
    .stAlert, .stWarning, .stException {
        display: none !important;
    }
    
    /* Hide the specific warning about experimental_get_query_params */
    div[data-testid="stException"] {
        display: none !important;
    }
    
    /* Click-to-Show Navbar Styles - SIMPLIFIED */
    .navbar-toggle-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        width: 90%;
        max-width: 400px;
    }
    
    .navbar-toggle-btn {
        width: 100%;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }
    
    .navbar-toggle-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
    }
        
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translate(-50%, 20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
    
    .navbar-expanded-content {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .nav-expanded-btn {
        background: #f8f9fa;
        color: #333;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        cursor: pointer;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: left;
    }
    
    .nav-expanded-btn:hover {
        background: #e9ecef;
        border-color: #667eea;
    }
    
    .nav-expanded-btn.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    .user-info-expanded {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #e0e0e0;
    }
    
    .user-badge-expanded {
        background: #00b894;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .admin-badge {
        background: #0984e3 !important;
    }
    
    .trial-badge-expanded {
        background: #fdcb6e;
        color: #333;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .logout-btn-expanded {
        background: #e17055;
        color: white;
        border: none;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        margin-top: 5px;
    }
    
    .logout-btn-expanded:hover {
        background: #d63031;
    }
    
    /* Prevent content from being hidden behind navbar */
    .stApp {
        padding-bottom: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

def navbar_collapsible_component(menu_options):
    """Click-to-Show Navbar without purple div"""
    
    # Initialize session state variables
    if 'selected_nav_menu' not in st.session_state:
        st.session_state.selected_nav_menu = menu_options[0]
    if 'navbar_expanded' not in st.session_state:
        st.session_state.navbar_expanded = False
    
    # Toggle button (always visible at bottom)
    st.markdown('<div class="navbar-toggle-container">', unsafe_allow_html=True)
    
    toggle_icon = "🏫" if not st.session_state.navbar_expanded else "📱"
    toggle_label = "School Fees Management Menu" if not st.session_state.navbar_expanded else "Hide Menu"
    
    if st.button(f"{toggle_icon} {toggle_label}", key="navbar_toggle", use_container_width=True):
        st.session_state.navbar_expanded = not st.session_state.navbar_expanded
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Expanded navbar content
    if st.session_state.navbar_expanded:
        st.markdown('<div class="navbar-expanded">', unsafe_allow_html=True)
        
        # Navigation buttons
        icon_map = {
            "Enter Fees": "💰",
            "View All Records": "📋",
            "Paid & Unpaid Students Record": "✅",
            "Student Yearly Report": "📊",
            "User Management": "👥",
            "Set Student Fees": "💸"
        }
        
        st.markdown('<div class="navbar-expanded-content">', unsafe_allow_html=True)
        
        for option in menu_options:
            is_active = st.session_state.selected_nav_menu == option
            icon = icon_map.get(option, "📄")
            
            button_label = f"{icon} {option}"
            
            if st.button(button_label, key=f"exp_nav_{option}", use_container_width=True):
                st.session_state.selected_nav_menu = option
                st.session_state.navbar_expanded = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # User info and logout
        st.markdown('<div class="user-info-expanded">', unsafe_allow_html=True)
        
        user_type = "Admin" if st.session_state.get("is_admin", False) else "User"
        username = st.session_state.get("current_user", "")
        
        admin_class = "admin-badge" if st.session_state.get("is_admin", False) else ""
        st.markdown(
            f'<div class="user-badge-expanded {admin_class}">👤 {user_type}: {username}</div>',
            unsafe_allow_html=True
        )
        
        trial_remaining = st.session_state.get("trial_remaining", "")
        if trial_remaining:
            st.markdown(
                f'<div class="trial-badge-expanded">⏰ {trial_remaining}</div>',
                unsafe_allow_html=True
            )
        
        if st.button("🚪 Logout", key="exp_nav_logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    return st.session_state.selected_nav_menu

def navbar_component(menu_options):
    """Original top navigation bar component"""
    
    if 'selected_nav_menu' not in st.session_state:
        st.session_state.selected_nav_menu = menu_options[0]
    
    with st.container():
        st.markdown("""
        <div class="navbar">
            <div class="navbar-container">
                <div class="navbar-brand">
                    <span class="navbar-brand-icon">🏫</span>
                    School Fees Management System
                </div>
                
                <div class="navbar-menu">
        """, unsafe_allow_html=True)
        
        for option in menu_options:
            is_active = st.session_state.selected_nav_menu == option
            
            icon_map = {
                "Enter Fees": "💰",
                "View All Records": "📋", 
                "Paid & Unpaid Students Record": "✅",
                "Student Yearly Report": "📊",
                "User Management": "👥",
                "Set Student Fees": "💸"
            }
            icon = icon_map.get(option, "📄")
            
            if st.button(f"{icon} {option}", key=f"nav_{option}", 
                       use_container_width=False,
                       help=f"Go to {option}"):
                st.session_state.selected_nav_menu = option
                st.rerun()
        
        st.markdown("""</div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class="navbar-user-info">""", unsafe_allow_html=True)
        
        user_type = "Admin" if st.session_state.is_admin else "User"
        st.markdown(f'<div class="user-badge">👤 {user_type}: {st.session_state.current_user}</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.trial_remaining:
            st.markdown(f'<div class="trial-badge">⏰ {st.session_state.trial_remaining}</div>', 
                       unsafe_allow_html=True)
        
        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="navbar_logout", use_container_width=False):
            logout()
            st.rerun()
        
        st.markdown("""</div>""", unsafe_allow_html=True)
        st.markdown("""</div>""", unsafe_allow_html=True)
    
    return st.session_state.selected_nav_menu

def navbar_bottom_component(menu_options):
    """Bottom-fixed navbar"""
    if 'selected_nav_menu' not in st.session_state:
        st.session_state.selected_nav_menu = menu_options[0]

    with st.container():
        st.markdown("""
        <div class="navbar-bottom">
          <div class="navbar-container">
            <div class="navbar-menu">
        """, unsafe_allow_html=True)

        icon_map = {
            "Enter Fees": "💰",
            "View All Records": "📋",
            "Paid & Unpaid Students Record": "✅",
            "Student Yearly Report": "📊",
            "User Management": "👥",
            "Set Student Fees": "💸"
        }

        for option in menu_options:
            label = f"{icon_map.get(option, '📄')} {option}"
            if st.button(label, key=f"bnav_{option}", help=f"Go to {option}"):
                st.session_state.selected_nav_menu = option
                st.rerun()

        st.markdown("""
            </div>
            <div class="navbar-user-info">
        """, unsafe_allow_html=True)

        user_type = "Admin" if st.session_state.get("is_admin") else "User"
        st.markdown(
            f'<div class="user-badge">👤 {user_type}: {st.session_state.get("current_user","")}</div>',
            unsafe_allow_html=True
        )
        if st.session_state.get("trial_remaining"):
            st.markdown(
                f'<div class="trial-badge">⏰ {st.session_state["trial_remaining"]}</div>',
                unsafe_allow_html=True
            )

        if st.button("🚪 Logout", key="bnav_logout"):
            logout()
            st.rerun()

        st.markdown("""
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.selected_nav_menu

def format_currency(val):
    """Format currency with Pakistani Rupees symbol and thousand separators"""
    try:
        return f"Rs. {int(val):,}" if not pd.isna(val) and val != 0 else "Rs. 0"
    except:
        return "Rs. 0"

def style_row(row):
    """Apply styling to DataFrame rows based on payment status"""
    today = datetime.now()
    is_between_1st_and_10th = 1 <= today.day <= 10
    styles = [''] * len(row)
    
    if is_between_1st_and_10th:
        if row['Monthly Fee'] == 0:
            styles[0] = 'color: red'
        else:
            styles[0] = 'color: green'
    return styles

def get_academic_year(date):
    """Determine academic year based on date"""
    year = date.year
    if date.month >= 4:  # Academic year starts in April
        return f"{year}-{year+1}"
    return f"{year-1}-{year}"

def check_annual_admission_paid(student_id, academic_year):
    """Check if annual charges or admission fee have been paid for the academic year"""
    df = load_data()
    if df.empty:
        return False, False
    
    student_records = df[(df['ID'] == student_id) & (df['Academic Year'] == academic_year)]
    annual_paid = student_records['Annual Charges'].sum() > 0
    admission_paid = student_records['Admission Fee'].sum() > 0
    
    return annual_paid, admission_paid

def get_unpaid_months(student_id):
    """Get list of unpaid months for a specific student"""
    df = load_data()
    all_months = [
        "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
        "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"
    ]
    
    if df.empty or student_id is None:
        return all_months
    
    paid_months = df[(df['ID'] == student_id) & (df['Monthly Fee'] > 0)]['Month'].unique().tolist()
    
    unpaid_months = [month for month in all_months if month not in paid_months]
    
    return unpaid_months

def get_student_fee_amount(student_id, fee_type):
    """Get specific fee amount for a student from database"""
    from database import load_student_fees
    
    fees_data = load_student_fees()
    
    if student_id in fees_data:
        fee_mapping = {
            "monthly": "monthly_fee",
            "annual": "annual_charges", 
            "admission": "admission_fee"
        }
        
        if fee_type in fee_mapping:
            fee_key = fee_mapping[fee_type]
            return fees_data[student_id].get(fee_key, 0)
    
    # Default fees if not set by admin
    default_fees = {
        "monthly": 3000,
        "annual": 3500,
        "admission": 10000
    }
    return default_fees.get(fee_type, 0)
# [file content end]
def generate_combined_slip_data(records):
    """Generate combined slip data from multiple fee records"""
    if not records:
        return None
    
    # Use the first record as base
    base_record = records[0]
    
    combined_data = {
        "student_name": base_record["Student Name"],
        "class_category": base_record["Class Category"],
        "class_section": base_record.get("Class Section", ""),
        "payment_date": base_record["Date"],
        "academic_year": base_record.get("Academic Year", ""),
        "monthly_fee": 0,
        "annual_charges": 0,
        "admission_fee": 0,
        "received_amount": 0,
        "payment_method": base_record["Payment Method"],
        "signature": base_record["Signature"],
        "months": []
    }
    
    # Combine all fees
    for record in records:
        combined_data["monthly_fee"] += record.get("Monthly Fee", 0)
        combined_data["annual_charges"] += record.get("Annual Charges", 0)
        combined_data["admission_fee"] += record.get("Admission Fee", 0)
        combined_data["received_amount"] += record.get("Received Amount", 0)
        
        # Collect months
        month = record.get("Month", "")
        if month and month not in combined_data["months"]:
            combined_data["months"].append(month)
    
    return combined_data