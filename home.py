# type:ignore
import streamlit as st
import base64
from database import load_school_config

def home_page():
    """Display beautiful home page with logo and school name"""
    st.set_page_config(page_title="School Fees Management", layout="wide", page_icon="🏫")
    
    # Initialize session state if it doesn't exist
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .title-text {
        font-size: 3.5rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    .subtitle-text {
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #7f8c8d !important;
        text-align: center;
        margin-bottom: 2rem !important;
    }
    .feature-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #3498db;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #2c3e50;
    }
    .feature-desc {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    .login-btn {
        background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem;
        border-radius: 8px !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }
    .circle-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background-color: white;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }
    .circle img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)
    
    school_config = load_school_config()
    school_name = school_config.get("school_name", "Name Of School")
    
    # Logo at the very top
    st.markdown('<div class="circle-container">', unsafe_allow_html=True)
    
    try:
        with open("school-pic.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        img_html = f'<img src="data:image/png;base64,{img_base64}" alt="School Logo">'
    except:
        img_html = '<div style="color: gray; text-align: center; padding: 20px;">School Logo</div>'
    
    st.markdown(
        f"""
        <div class="circle">
            {img_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # School Name and Subtitle
    st.markdown(f'<h1 class="title-text">{school_name}</h1>', unsafe_allow_html=True)
    st.markdown('<h1 class="title-text">Fees Management System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Streamline your school\'s fee collection and tracking process with a 1-month free trial!</p>', unsafe_allow_html=True) 
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3 class="feature-title">Fee Collection</h3>
            <p class="feature-desc">Easily record and track student fee payments with a simple, intuitive interface.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Reports</h3>
            <p class="feature-desc">Generate detailed reports on fee collection, outstanding payments, and student records.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3 class="feature-title">Secure Access</h3>
            <p class="feature-desc">Role-based authentication ensures only authorized staff can access sensitive data.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Login Button
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    if st.button("Sign Up for Free Trial / Login", key="home_login_btn", help="Click to sign up or login"):
        st.session_state.show_login = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #7f8c8d; font-size: 0.8rem;">
        <p>© 2025 School Fees Management System | Developed with ❤️ for educational institutions</p>
        <p>Start your 1-month free trial today!</p> 
    </div>
    """, unsafe_allow_html=True)
