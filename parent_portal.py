# type:ignore
import streamlit as st
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from parent_auth import (
    authenticate_parent, 
    create_parent_account, 
    check_parent_authentication,
    logout_parent
)
from database import load_school_config, load_data, load_student_details, load_student_fees
from utils import format_currency

# Page configuration for parent portal
st.set_page_config(
    page_title="Parent Portal - School Fees Management",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_parent_info(email):
    """Get parent information from database"""
    try:
        with open("parents.json", 'r') as f:
            parents = json.load(f)
        
        if email in parents:
            return parents[email]
        return {}
    except Exception as e:
        print(f"Error getting parent info: {str(e)}")
        return {}

def get_parent_students(email):
    """Get student IDs linked to parent"""
    try:
        with open("parents.json", 'r') as f:
            parents = json.load(f)
        
        if email in parents:
            return parents[email].get('student_ids', [])
        return []
    except Exception as e:
        print(f"Error getting student list: {str(e)}")
        return []

def get_student_monthly_fee(student_id):
    """Get student's monthly fee amount"""
    try:
        student_fees = load_student_fees()
        if student_id in student_fees:
            return student_fees[student_id].get('monthly_fee', 3000)
        
        # Default fee if not set
        from database import load_default_fees
        default_fees = load_default_fees()
        return default_fees.get('monthly_fee', 3000)
    except:
        return 3000

def get_student_annual_fee(student_id):
    """Get student's annual fee amount"""
    try:
        student_fees = load_student_fees()
        if student_id in student_fees:
            return student_fees[student_id].get('annual_fee', 3500)
        
        from database import load_default_fees
        default_fees = load_default_fees()
        return default_fees.get('annual_charges', 3500)
    except:
        return 3500

def get_student_admission_fee(student_id):
    """Get student's admission fee amount"""
    try:
        student_fees = load_student_fees()
        if student_id in student_fees:
            return student_fees[student_id].get('admission_fee', 10000)
        
        from database import load_default_fees
        default_fees = load_default_fees()
        return default_fees.get('admission_fee', 10000)
    except:
        return 10000

def get_student_fee_details(student_id):
    """Get comprehensive fee details for student including paid/unpaid months"""
    try:
        df = load_data()
        student_details = load_student_details()
        
        if student_id not in student_details:
            return None
        
        student_info = student_details[student_id]
        student_records = df[df['ID'] == student_id]
        
        # All months in academic year
        all_months = [
            "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
            "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"
        ]
        
        # Get fee amounts
        monthly_fee_amount = get_student_monthly_fee(student_id)
        annual_fee_amount = get_student_annual_fee(student_id)
        admission_fee_amount = get_student_admission_fee(student_id)
        
        # Calculate paid and unpaid months
        paid_months = []
        unpaid_months = []
        
        for month in all_months:
            month_records = student_records[
                (student_records['Month'] == month) & 
                (student_records['Monthly Fee'] > 0)
            ]
            if not month_records.empty:
                paid_months.append({
                    'month': month,
                    'amount': month_records['Monthly Fee'].iloc[0],
                    'date': month_records['Date'].iloc[0] if 'Date' in month_records.columns else 'N/A'
                })
            else:
                unpaid_months.append(month)
        
        # Check if annual and admission fees are paid
        annual_paid = not student_records[student_records['Annual Charges'] > 0].empty
        admission_paid = not student_records[student_records['Admission Fee'] > 0].empty
        
        # Calculate totals
        total_monthly = student_records['Monthly Fee'].sum() if not student_records.empty else 0
        total_annual = student_records['Annual Charges'].sum() if not student_records.empty else 0
        total_admission = student_records['Admission Fee'].sum() if not student_records.empty else 0
        total_received = student_records['Received Amount'].sum() if not student_records.empty else 0
        
        # Calculate outstanding
        total_paid_months = len(paid_months)
        total_unpaid_months = len(unpaid_months)
        total_monthly_due = monthly_fee_amount * 12
        total_annual_due = annual_fee_amount if not annual_paid else 0
        total_admission_due = admission_fee_amount if not admission_paid else 0
        
        total_due = total_monthly_due + total_annual_due + total_admission_due
        balance_due = max(0, total_due - total_received)
        
        return {
            "student_id": student_id,
            "student_name": student_info.get('student_name', 'N/A'),
            "father_name": student_info.get('father_name', 'N/A'),
            "class": student_info.get('class_category', 'N/A'),
            "phone": student_info.get('phone', 'N/A'),
            "monthly_fee": monthly_fee_amount,
            "annual_fee": annual_fee_amount,
            "admission_fee": admission_fee_amount,
            "total_monthly": total_monthly,
            "total_annual": total_annual,
            "total_admission": total_admission,
            "total_received": total_received,
            "total_due": total_due,
            "balance_due": balance_due,
            "percentage_paid": round((total_received / total_due * 100) if total_due > 0 else 0, 1),
            "paid_months": paid_months,
            "unpaid_months": unpaid_months,
            "total_paid_months": total_paid_months,
            "total_unpaid_months": total_unpaid_months,
            "annual_paid": annual_paid,
            "admission_paid": admission_paid
        }
    except Exception as e:
        print(f"Error getting fee details: {str(e)}")
        return None

def add_back_button():
    """Add back button to return to dashboard"""
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.current_parent_page = "📊 Dashboard"
        st.rerun()

def show_payment_interface(student_id, fee_details):
    """Show complete payment interface with all fee options"""
    st.subheader("💳 Make Payment")
    
    if fee_details['balance_due'] == 0:
        st.success("""
        # 🎉 All Fees Paid!
        
        ### Your account is up to date. No payment required at this time.
        
        Thank you for your timely payments!
        """)
        return
    
    # Payment header with balance
    st.warning(f"""
    # 💰 Payment Required
    
    ### Current Balance Due: **Rs. {fee_details['balance_due']:,}**
    
    Please choose what you want to pay:
    """)
    
    # Payment type selection
    payment_type = st.radio(
        "Select Payment Type:",
        ["Monthly Fees", "Annual Fee", "Admission Fee", "Custom Amount"],
        horizontal=True
    )
    
    amount = 0
    description = ""
    
    if payment_type == "Monthly Fees":
        if not fee_details['unpaid_months']:
            st.success("✅ All monthly fees are paid! No payment required.")
            return
        
        monthly_fee = fee_details['monthly_fee']
        
        # Display current fee info
        st.info(f"**Monthly Fee Amount:** Rs. {monthly_fee:,} per month")
        st.warning(f"**Unpaid Months Available:** {len(fee_details['unpaid_months'])} months")
        
        # Month selection
        st.write("### Select Months to Pay:")
        selected_months = st.multiselect(
            "Choose one or multiple months:",
            fee_details['unpaid_months'],
            help="You can select 1, 2, 3 or more months to pay at once"
        )
        
        if selected_months:
            amount = monthly_fee * len(selected_months)
            description = f"Monthly Fee - {', '.join(selected_months)}"
            st.success(f"**Selected Months:** {', '.join(selected_months)}")
            st.success(f"**Total Amount to Pay:** Rs. {amount:,}")
    
    elif payment_type == "Annual Fee":
        if fee_details['annual_paid']:
            st.success("✅ Annual Fee Already Paid")
            return
        
        amount = fee_details['annual_fee']
        description = "Annual Fee"
        st.info(f"**Annual Fee Amount:** Rs. {amount:,}")
        st.success(f"**Amount to Pay:** Rs. {amount:,}")
    
    elif payment_type == "Admission Fee":
        if fee_details['admission_paid']:
            st.success("✅ Admission Fee Already Paid")
            return
        
        amount = fee_details['admission_fee']
        description = "Admission Fee"
        st.info(f"**Admission Fee Amount:** Rs. {amount:,}")
        st.success(f"**Amount to Pay:** Rs. {amount:,}")
    
    else:  # Custom Amount
        amount = st.number_input(
            "Enter Amount to Pay:",
            min_value=1,
            max_value=int(fee_details['balance_due']),
            value=min(1000, int(fee_details['balance_due']))
        )
        description = "Custom Payment"
        st.success(f"**Amount to Pay:** Rs. {amount:,}")
    
    # Show payment method only if amount is selected
    if amount > 0:
        # Payment method selection
        st.write("### Choose Payment Method:")
        payment_method = st.radio(
            "Select payment option:",
            ["JazzCash", "EasyPaisa", "Bank Transfer", "Credit/Debit Card"],
            horizontal=True
        )
        
        # Show payment instructions based on method
        if payment_method == "JazzCash":
            st.info("""
            **JazzCash Payment Instructions:**
            - Send payment to: **0300-1234567**
            - Account Name: **School Fees Account**
            - Include Student ID in transaction
            """)
        elif payment_method == "EasyPaisa":
            st.info("""
            **EasyPaisa Payment Instructions:**
            - Send payment to: **0312-7654321**  
            - Account Name: **School Fees Account**
            - Include Student ID in transaction
            """)
        elif payment_method == "Bank Transfer":
            st.info("""
            **Bank Transfer Instructions:**
            - Bank: **HBL**
            - Account #: **12345678901**
            - Account Name: **School Fees Account**
            - Include Student ID in remarks
            """)
        else:
            st.info("""
            **Card Payment:**
            - Secure payment gateway
            - You will be redirected to payment page
            - Transaction fee may apply
            """)
        
        # Payment confirmation form
        with st.form("payment_form"):
            st.write("### Confirm Payment")
            
            transaction_id = st.text_input("Transaction ID*", placeholder="e.g., TXN123456789")
            payment_date = st.date_input("Payment Date*", value=datetime.now())
            parent_name = st.text_input("Your Name*", placeholder="Enter your full name")
            
            submitted = st.form_submit_button(f"🚀 Pay Rs. {amount:,} via {payment_method}", use_container_width=True)
            
            if submitted:
                if not transaction_id or not parent_name:
                    st.error("❌ Please fill all required fields")
                else:
                    # Save payment record
                    try:
                        # Create payment record
                        payment_data = {
                            "student_id": student_id,
                            "student_name": fee_details['student_name'],
                            "amount": amount,
                            "payment_method": payment_method,
                            "transaction_id": transaction_id,
                            "parent_name": parent_name,
                            "payment_date": payment_date.strftime("%Y-%m-%d"),
                            "description": description,
                            "selected_months": fee_details['unpaid_months'] if payment_type == "Monthly Fees" else [],
                            "status": "pending",
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Save to parent payments file
                        payment_file = "data/parent_payments.json"
                        os.makedirs("data", exist_ok=True)
                        
                        if os.path.exists(payment_file):
                            with open(payment_file, 'r') as f:
                                payments = json.load(f)
                        else:
                            payments = {}
                        
                        if student_id not in payments:
                            payments[student_id] = []
                        
                        payments[student_id].append(payment_data)
                        
                        with open(payment_file, 'w') as f:
                            json.dump(payments, f, indent=2)
                        
                        st.success("""
                        ✅ Payment Request Submitted Successfully!
                        
                        **Next Steps:**
                        1. School will verify your payment
                        2. You'll receive confirmation within 24 hours
                        3. Check payment history for updates
                        
                        Thank you for your payment!
                        """)
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Payment processing error: {str(e)}")

def show_parent_login():
    """Show parent login/signup interface"""
    
    # School header
    school_config = load_school_config()
    school_name = school_config.get("school_name", "School Name")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.5rem;">🏫 {school_name}</h1>
        <h2 style="margin: 0; font-size: 1.5rem;">Parent Portal</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        st.markdown("""
        <div style="text-align: center;">
            <h3>📱 Parent Features</h3>
            <p>• View Fee Details</p>
            <p>• Check Payment History</p>
            <p>• Make Online Payments</p>
            <p>• Download Receipts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Parent Login")
            
            with st.form("parent_login_form"):
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                login_btn = st.form_submit_button("🚀 Login to Portal", use_container_width=True)
                
                if login_btn:
                    if email and password:
                        if authenticate_parent(email, password):
                            st.session_state.parent_authenticated = True
                            st.session_state.parent_email = email
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    else:
                        st.error("⚠️ Please enter email and password")
        
        with tab2:
            st.subheader("Create Parent Account")
            
            with st.form("parent_signup_form"):
                signup_email = st.text_input("📧 Email Address*", placeholder="your.email@example.com")
                parent_name = st.text_input("👤 Parent Name*", placeholder="Your full name")
                signup_password = st.text_input("🔒 Password*", type="password", placeholder="Minimum 6 characters")
                confirm_password = st.text_input("🔒 Confirm Password*", type="password", placeholder="Re-enter password")
                phone = st.text_input("📱 Phone Number*", placeholder="03001234567")
                student_ids = st.text_area(
                    "🎓 Student IDs*", 
                    placeholder="Enter one student ID per line\nExample:\nSTU001\nSTU002",
                    help="Contact school administration to get your student's ID"
                )
                
                signup_btn = st.form_submit_button("🎉 Create Account", use_container_width=True)
                
                if signup_btn:
                    if signup_email and parent_name and signup_password and phone and student_ids:
                        if signup_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(signup_password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        else:
                            # Process student IDs
                            student_id_list = [s.strip() for s in student_ids.split('\n') if s.strip()]
                            
                            if not student_id_list:
                                st.error("❌ Please enter at least one student ID")
                            else:
                                success, message = create_parent_account(
                                    signup_email,
                                    signup_password,
                                    parent_name,
                                    student_id_list,
                                    phone
                                )
                                if success:
                                    st.success("✅ Account created successfully! Please login.")
                                    st.balloons()
                                else:
                                    st.error(f"❌ {message}")
                    else:
                        st.error("⚠️ Please fill all required fields (*)")

def show_parent_dashboard():
    """Show parent dashboard after login"""
    
    # School header
    school_config = load_school_config()
    school_name = school_config.get("school_name", "School Name")
    
    # Sidebar with collapsible design
    with st.sidebar:
        # Parent info section
        parent_info = get_parent_info(st.session_state.parent_email)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
            <h3 style="margin: 0; font-size: 1.2rem;">👋 Welcome!</h3>
            <p style="margin: 5px 0; font-size: 1rem;"><strong>{parent_info.get('parent_name', 'Parent')}</strong></p>
            <p style="margin: 5px 0; font-size: 0.8rem;">{st.session_state.parent_email}</p>
            <p style="margin: 5px 0; font-size: 0.8rem;">📱 {parent_info.get('phone', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Student selection
        students = get_parent_students(st.session_state.parent_email)
        
        if not students:
            st.warning("⚠️ No students linked to your account")
            selected_student = None
        else:
            selected_student = st.selectbox(
                "🎒 Select Student:",
                students,
                key="student_selector"
            )
            st.session_state.selected_student = selected_student
        
        st.divider()
        
        # Navigation with better styling
        st.markdown("### 🧭 Navigation")
        
        # Initialize session state for current page
        if 'current_parent_page' not in st.session_state:
            st.session_state.current_parent_page = "📊 Dashboard"
        
        # Page selection buttons
        pages = {
            "📊 Dashboard": "📊",
            "💰 Fee Details": "💰", 
            "📋 Payment History": "📋",
            "💳 Make Payment": "💳"
        }
        
        for page_name, icon in pages.items():
            if st.button(
                f"{icon} {page_name}", 
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if st.session_state.current_parent_page == page_name else "secondary"
            ):
                st.session_state.current_parent_page = page_name
                st.rerun()
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout_parent()
            st.rerun()
    
    # Main content area
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #2c3e50;">{school_name} - Parent Portal</h1>
        <p style="margin: 0; color: #7f8c8d;">{st.session_state.current_parent_page}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not students:
        st.info("📝 No students are linked to your account. Please contact school administration to link your students.")
        return
    
    if not selected_student:
        st.info("👆 Please select a student from the sidebar")
        return
    
    # Show selected page based on session state
    if st.session_state.current_parent_page == "📊 Dashboard":
        show_dashboard_page(selected_student)
    elif st.session_state.current_parent_page == "💰 Fee Details":
        show_fee_details_page(selected_student)
    elif st.session_state.current_parent_page == "📋 Payment History":
        show_payment_history_page(selected_student)
    elif st.session_state.current_parent_page == "💳 Make Payment":
        show_make_payment_page(selected_student)

def show_dashboard_page(student_id):
    """Show dashboard with overview"""
    
    fee_details = get_student_fee_details(student_id)
    
    if not fee_details:
        st.error("❌ Student information not found")
        return
    
    # Quick stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎒 Student", 
            value=fee_details['student_name'],
            help="Student Name"
        )
    with col2:
        st.metric(
            label="🏫 Class", 
            value=fee_details['class'],
            help="Current Class"
        )
    with col3:
        st.metric(
            label="👨 Father", 
            value=fee_details['father_name'],
            help="Father's Name"
        )
    with col4:
        st.metric(
            label="📱 Phone", 
            value=fee_details['phone'],
            help="Contact Number"
        )
    
    st.divider()
    
    # Fee summary cards - INCLUDING ANNUAL & ADMISSION FEES
    st.subheader("💰 Fee Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Fee", f"Rs. {fee_details['monthly_fee']:,}")
    with col2:
        st.metric("Annual Fee", f"Rs. {fee_details['annual_fee']:,}")
    with col3:
        st.metric("Admission Fee", f"Rs. {fee_details['admission_fee']:,}")
    with col4:
        st.metric("Total Due", f"Rs. {fee_details['total_due']:,}")
    
    st.divider()
    
    # Payment status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Amount Paid", 
            value=f"Rs. {fee_details['total_received']:,}",
            delta=f"{fee_details['percentage_paid']}%"
        )
    with col2:
        st.metric(
            label="Balance Due", 
            value=f"Rs. {fee_details['balance_due']:,}",
            delta_color="inverse"
        )
    with col3:
        # Status badge
        if fee_details['balance_due'] == 0:
            st.success("✅ All Paid")
        elif fee_details['balance_due'] < fee_details['total_due'] * 0.5:
            st.warning("🟡 Partial Paid")
        else:
            st.error("🔴 Payment Due")
    
    # Progress bar with better styling
    st.markdown(f"**Payment Progress: {fee_details['percentage_paid']}%**")
    st.progress(fee_details['percentage_paid'] / 100)
    
    # Monthly fee status - PAID & UNPAID CLEARLY SHOWN
    st.divider()
    st.subheader("📅 Monthly Fee Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### ✅ Paid Months ({len(fee_details['paid_months'])})")
        if fee_details['paid_months']:
            for paid in fee_details['paid_months']:
                st.success(f"**{paid['month']}** - Rs. {paid['amount']:,} ({paid['date']})")
        else:
            st.info("No months paid yet")
    
    with col2:
        st.markdown(f"### ❌ Unpaid Months ({len(fee_details['unpaid_months'])})")
        if fee_details['unpaid_months']:
            for month in fee_details['unpaid_months']:
                st.error(f"**{month}** - Rs. {fee_details['monthly_fee']:,}")
        else:
            st.success("All months paid! 🎉")
    
    # Annual & Admission Fee Status
    st.divider()
    st.subheader("🎓 Other Fees Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if fee_details['annual_paid']:
            st.success(f"✅ Annual Fee Paid - Rs. {fee_details['annual_fee']:,}")
        else:
            st.error(f"❌ Annual Fee Due - Rs. {fee_details['annual_fee']:,}")
    
    with col2:
        if fee_details['admission_paid']:
            st.success(f"✅ Admission Fee Paid - Rs. {fee_details['admission_fee']:,}")
        else:
            st.error(f"❌ Admission Fee Due - Rs. {fee_details['admission_fee']:,}")
    
    # Quick actions
    st.divider()
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View Detailed History", use_container_width=True, icon="📋"):
            st.session_state.current_parent_page = "📋 Payment History"
            st.rerun()
    
    with col2:
        if st.button("💳 Make Payment", use_container_width=True, icon="💳"):
            st.session_state.current_parent_page = "💳 Make Payment"
            st.rerun()
    
    with col3:
        if st.button("📊 Fee Breakdown", use_container_width=True, icon="📊"):
            st.session_state.current_parent_page = "💰 Fee Details"
            st.rerun()

def show_fee_details_page(student_id):
    """Show detailed fee breakdown with all months"""
    
    # Add back button at the top
    add_back_button()
    
    fee_details = get_student_fee_details(student_id)
    
    if not fee_details:
        st.error("❌ Student information not found")
        return
    
    st.subheader(f"💰 Detailed Fee Breakdown - {fee_details['student_name']}")
    
    # All fees display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Monthly Fee", f"Rs. {fee_details['monthly_fee']:,}")
    with col2:
        st.metric("Annual Fee", f"Rs. {fee_details['annual_fee']:,}")
    with col3:
        st.metric("Admission Fee", f"Rs. {fee_details['admission_fee']:,}")
    with col4:
        st.metric("Total Due", f"Rs. {fee_details['total_due']:,}")
    
    # All months display in a grid
    st.subheader("📅 Complete Monthly Status")
    
    # Create columns for months (4 months per row)
    months = [
        "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
        "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"
    ]
    
    # Create 4 columns for better layout
    cols = st.columns(4)
    
    for i, month in enumerate(months):
        col_idx = i % 4
        with cols[col_idx]:
            # Check if month is paid
            is_paid = any(p['month'] == month for p in fee_details['paid_months'])
            
            if is_paid:
                # Find paid month details
                paid_month = next((p for p in fee_details['paid_months'] if p['month'] == month), None)
                st.success(f"""
                **{month}**
                ✅ PAID
                Amount: Rs. {paid_month['amount']:,}
                """)
            else:
                st.error(f"""
                **{month}**
                ❌ UNPAID
                Due: Rs. {fee_details['monthly_fee']:,}
                """)

def show_payment_history_page(student_id):
    """Show payment history"""
    
    # Add back button at the top
    add_back_button()
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if student_records.empty:
        st.info("ℹ️ No payment history found")
        return
    
    # Summary stats
    total_payments = len(student_records)
    total_received = student_records['Received Amount'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Transactions", total_payments)
    with col2:
        st.metric("Total Amount Paid", f"Rs. {total_received:,}")
    
    st.divider()
    
    # Display payment history
    st.subheader("📋 Payment History")
    
    display_columns = ['Date', 'Month', 'Monthly Fee', 'Annual Charges', 'Admission Fee', 'Received Amount', 'Payment Method']
    available_columns = [col for col in display_columns if col in student_records.columns]
    display_df = student_records[available_columns].copy()
    
    # Format dates and amounts
    if 'Date' in display_df.columns:
        display_df['Date'] = pd.to_datetime(display_df['Date'], errors='coerce').dt.strftime('%d-%m-%Y')
    display_df = display_df.sort_values('Date' if 'Date' in display_df.columns else available_columns[0], ascending=False)
    
    # Format currency display
    def format_rs(val):
        return f"Rs. {val:,}" if pd.notna(val) and val != 0 else "Rs. 0"
    
    st.dataframe(
        display_df.style.format({
            'Monthly Fee': format_rs,
            'Annual Charges': format_rs,
            'Admission Fee': format_rs,
            'Received Amount': format_rs
        }),
        use_container_width=True,
        height=400
    )

def show_make_payment_page(student_id):
    """Show payment options with all fee types in one interface"""
    
    add_back_button()
    
    fee_details = get_student_fee_details(student_id)
    
    if not fee_details:
        st.error("❌ Student information not found")
        return
    
    # Show complete payment interface
    show_payment_interface(student_id, fee_details)

def parent_portal_page():
    """Main parent portal page"""
    # Remove Streamlit warnings and headers
    st.markdown("""
    <style>
    /* Hide Streamlit header and warnings */
    header {
        display: none !important;
    }
    .stAlert, .stWarning, .stException {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Set parent portal flag
    st.session_state.is_parent_portal = True
    
    # Check if parent is authenticated
    if not check_parent_authentication():
        show_parent_login()
    else:
        show_parent_dashboard()

if __name__ == "__main__":
    parent_portal_page()