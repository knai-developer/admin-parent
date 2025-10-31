# http://localhost:8501/?parent=true

# [file content begin]
# type:ignore
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database import (
    load_data, load_student_fees, save_student_fees, generate_student_id,
    load_default_fees, save_default_fees, load_school_config, save_school_config,
    initialize_files, load_student_details
)
from utils import format_currency
import plotly.express as px
import plotly.graph_objects as go

def admin_dashboard():
    """Main admin dashboard with tabs instead of sidebar"""
    st.set_page_config(page_title="Admin Dashboard", layout="wide")
    
    # School header
    school_config = load_school_config()
    school_name = school_config.get("school_name", "School Name")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 10px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.5rem;">🏫 {school_name}</h1>
        <h2 style="margin: 0; font-size: 1.5rem;">Admin Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for all admin features
    tabs = st.tabs([
        "📊 Dashboard Overview", 
        "💰 Enter Fees", 
        "🎒 Student Management", 
        "🏫 Class-wise Details", 
        "📈 Analytics & Reports", 
        "👥 User Management", 
        "💸 Fee Settings", 
        "💳 Payment Systems",
        "⚙️ School Configuration"
    ])
    
    # Tab 1: Dashboard Overview
    with tabs[0]:
        dashboard_overview()
    
    # Tab 2: Enter Fees
    with tabs[1]:
        from fees_entry import fees_entry_page
        fees_entry_page()
    
    # Tab 3: Student Management
    with tabs[2]:
        student_management()
    
    # Tab 4: Class-wise Details
    with tabs[3]:
        class_wise_fee_details()
    
    # Tab 5: Analytics & Reports
    with tabs[4]:
        analytics_reports()
    
    # Tab 6: User Management
    with tabs[5]:
        from admin import user_management
        user_management()
    
    # Tab 7: Fee Settings
    with tabs[6]:
        fee_settings()
    
    # Tab 8: Payment Systems
    with tabs[7]:
        payment_systems()
    
    # Tab 9: School Configuration
    with tabs[8]:
        from admin import admin_page
        admin_page("School Configuration")

def dashboard_overview():
    """Dashboard overview with key metrics"""
    st.header("📊 Dashboard Overview")
    
    df = load_data()
    
    if df.empty:
        st.info("No fee records found. Start by adding student fees.")
        return
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_students = df['Student Name'].nunique()
    total_classes = df['Class Category'].nunique()
    total_collected = df['Received Amount'].sum()
    total_records = len(df)
    
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Total Classes", total_classes)
    with col3:
        st.metric("Total Collected", format_currency(total_collected))
    with col4:
        st.metric("Total Records", total_records)
    with col5:
        # Calculate collection rate
        total_expected = (df['Monthly Fee'].sum() + df['Annual Charges'].sum() + df['Admission Fee'].sum())
        collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
        st.metric("Collection Rate", f"{collection_rate:.1f}%")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Collection by Class")
        class_collection = df.groupby('Class Category')['Received Amount'].sum().sort_values(ascending=False)
        fig = px.bar(
            x=class_collection.index,
            y=class_collection.values,
            labels={'x': 'Class', 'y': 'Amount Collected (Rs.)'},
            title="Fee Collection by Class"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Collection by Month")
        month_collection = df.groupby('Month')['Received Amount'].sum()
        months_order = ["APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                       "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"]
        month_collection = month_collection.reindex([m for m in months_order if m in month_collection.index])
        fig = px.line(
            x=month_collection.index,
            y=month_collection.values,
            labels={'x': 'Month', 'y': 'Amount Collected (Rs.)'},
            title="Monthly Collection Trend",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent transactions
    st.subheader("Recent Transactions")
    recent_df = df.sort_values('Entry Timestamp', ascending=False).head(10)
    
    # Load student details to get father names
    student_details = load_student_details()
    father_names = {}
    for student_id, details in student_details.items():
        father_names[details.get('student_name', '')] = details.get('father_name', '')
    
    display_df = recent_df[[
        'Student Name', 'Class Category', 'Month', 'Monthly Fee', 
        'Annual Charges', 'Admission Fee', 'Received Amount', 'Date'
    ]].copy()
    
    # Add Father Name column
    display_df.insert(1, 'Father Name', display_df['Student Name'].map(father_names))
    
    st.dataframe(
        display_df.style.format({
            'Monthly Fee': format_currency,
            'Annual Charges': format_currency,
            'Admission Fee': format_currency,
            'Received Amount': format_currency
        }),
        use_container_width=True
    )

def student_management():
    """Student management section"""
    st.header("🎒 Student Management")
    
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Single Student", "📤 Bulk Upload", "👀 View All Students"])
    
    with tab1:
        st.subheader("Add Single Student")
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                student_name = st.text_input("Student Name*", placeholder="Full name")
                father_name = st.text_input("Father Name*", placeholder="Father's full name")
                class_category = st.selectbox("Class*", CLASS_CATEGORIES)
            with col2:
                phone = st.text_input("Phone Number*", placeholder="03001234567")
                age = st.number_input("Age*", min_value=3, max_value=25, value=10)
                address = st.text_area("Address*", placeholder="Student's address", height=80)
            
            submit = st.form_submit_button("Add Student")
            
            if submit:
                if not all([student_name, father_name, class_category, phone, address]):
                    st.error("Please fill all required fields (*)")
                else:
                    student_id = generate_student_id(student_name, class_category)
                    
                    # Save to student details JSON
                    from database import add_student_detail
                    if add_student_detail(student_id, student_name, father_name, class_category, address, phone, age):
                        st.success(f"Student '{student_name}' added successfully!")
                        st.info(f"Student ID: {student_id}")
                    else:
                        st.error("Failed to add student")
    
    with tab2:
        st.subheader("Bulk Upload Students (CSV)")
        st.info("""
        **CSV Format Required:**
        - Column 1: Student Name
        - Column 2: Father Name
        - Column 3: Class
        - Column 4: Phone Number
        - Column 5: Age
        - Column 6: Address
        """)
        
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                bulk_df = pd.read_csv(uploaded_file)
                
                # Validate columns
                required_cols = ['Student Name', 'Father Name', 'Class', 'Phone Number', 'Age', 'Address']
                if not all(col in bulk_df.columns for col in required_cols):
                    st.error(f"CSV must contain columns: {', '.join(required_cols)}")
                else:
                    st.dataframe(bulk_df, use_container_width=True)
                    
                    if st.button("Upload All Students"):
                        from database import add_student_detail
                        added_count = 0
                        
                        for _, row in bulk_df.iterrows():
                            student_id = generate_student_id(row['Student Name'], row['Class'])
                            if add_student_detail(
                                student_id,
                                row['Student Name'],
                                row['Father Name'],
                                row['Class'],
                                row['Address'],
                                str(row['Phone Number']),
                                int(row['Age'])
                            ):
                                added_count += 1
                        
                        st.success(f"{added_count} students uploaded successfully!")
            
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
    
    with tab3:
        st.subheader("All Students")
        student_details = load_student_details()
        
        if not student_details:
            st.info("No students found")
        else:
            # Convert to DataFrame
            students_list = []
            for student_id, details in student_details.items():
                students_list.append({
                    "ID": student_id,
                    "Name": details.get('student_name', ''),
                    "Father": details.get('father_name', ''),
                    "Class": details.get('class_category', ''),
                    "Phone": details.get('phone', ''),
                    "Age": details.get('age', ''),
                    "Address": details.get('address', ''),
                    "Added": details.get('created_at', '')
                })
            
            students_df = pd.DataFrame(students_list)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                selected_class = st.selectbox("Filter by Class", ["All"] + CLASS_CATEGORIES)
            with col2:
                search_name = st.text_input("Search by Name")
            
            # Apply filters
            filtered_df = students_df.copy()
            if selected_class != "All":
                filtered_df = filtered_df[filtered_df['Class'] == selected_class]
            if search_name:
                filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False)]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download option
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Students as CSV",
                data=csv,
                file_name="students_list.csv",
                mime="text/csv"
            )

def class_wise_fee_details():
    """Class-wise fee details with outstanding and paid months"""
    st.header("🏫 Class-wise Fee Details")
    
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    df = load_data()
    student_details = load_student_details()
    
    if df.empty:
        st.info("No fee records found")
        return
    
    selected_class = st.selectbox("Select Class", CLASS_CATEGORIES)
    
    class_df = df[df['Class Category'] == selected_class]
    
    if class_df.empty:
        st.info(f"No records found for {selected_class}")
        return
    
    # Class statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = class_df['Student Name'].nunique()
    total_collected = class_df['Received Amount'].sum()
    total_expected = (class_df['Monthly Fee'].sum() + 
                     class_df['Annual Charges'].sum() + 
                     class_df['Admission Fee'].sum())
    
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Total Collected", format_currency(total_collected))
    with col3:
        st.metric("Total Expected", format_currency(total_expected))
    with col4:
        collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
        st.metric("Collection Rate", f"{collection_rate:.1f}%")
    
    st.divider()
    
    # Student-wise detailed analysis
    st.subheader("📋 Student-wise Detailed Analysis")
    
    # Get all students in this class
    class_students = {}
    for student_id, details in student_details.items():
        if details.get('class_category') == selected_class:
            class_students[student_id] = details
    
    if not class_students:
        st.info(f"No students found in {selected_class}")
        return
    
    # Create detailed analysis for each student
    analysis_data = []
    
    for student_id, student_info in class_students.items():
        student_records = class_df[class_df['ID'] == student_id]
        
        # Calculate totals
        total_monthly = student_records['Monthly Fee'].sum()
        total_annual = student_records['Annual Charges'].sum()
        total_admission = student_records['Admission Fee'].sum()
        total_received = student_records['Received Amount'].sum()
        
        # Count paid months
        paid_months = student_records[student_records['Monthly Fee'] > 0]['Month'].nunique()
        
        # All possible months
        all_months = ["APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                     "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"]
        unpaid_months = 12 - paid_months
        
        # Outstanding amount
        total_due = total_monthly + total_annual + total_admission
        outstanding = max(0, total_due - total_received)
        
        analysis_data.append({
            "Student ID": student_id,
            "Student Name": student_info.get('student_name', ''),
            "Father Name": student_info.get('father_name', ''),
            "Phone": student_info.get('phone', ''),
            "Paid Months": paid_months,
            "Unpaid Months": unpaid_months,
            "Total Received": total_received,
            "Outstanding": outstanding,
            "Status": "Fully Paid" if outstanding == 0 else "Partially Paid" if total_received > 0 else "Not Paid"
        })
    
    analysis_df = pd.DataFrame(analysis_data)
    
    # Display analysis
    st.dataframe(
        analysis_df.style.format({
            'Total Received': format_currency,
            'Outstanding': format_currency
        }),
        use_container_width=True
    )
    
    # Summary statistics
    st.divider()
    st.subheader("📊 Class Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    fully_paid = len(analysis_df[analysis_df['Status'] == 'Fully Paid'])
    partially_paid = len(analysis_df[analysis_df['Status'] == 'Partially Paid'])
    not_paid = len(analysis_df[analysis_df['Status'] == 'Not Paid'])
    total_outstanding = analysis_df['Outstanding'].sum()
    
    with col1:
        st.metric("Fully Paid", fully_paid)
    with col2:
        st.metric("Partially Paid", partially_paid)
    with col3:
        st.metric("Not Paid", not_paid)
    with col4:
        st.metric("Total Outstanding", format_currency(total_outstanding))
    
    # Download option
    csv = analysis_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"Download {selected_class} Analysis",
        data=csv,
        file_name=f"{selected_class}_analysis.csv",
        mime="text/csv"
    )

def analytics_reports():
    """Analytics and reports"""
    st.header("📈 Analytics & Reports")
    
    df = load_data()
    
    if df.empty:
        st.info("No fee records found")
        return
    
    tab1, tab2, tab3 = st.tabs(["📊 Collection Analysis", "🎒 Student Analysis", "💳 Payment Methods"])
    
    with tab1:
        st.subheader("Collection Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly collection trend
            month_order = ["APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                          "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"]
            monthly_collection = df.groupby('Month')['Received Amount'].sum()
            monthly_collection = monthly_collection.reindex([m for m in month_order if m in monthly_collection.index])
            
            fig = px.line(
                x=monthly_collection.index,
                y=monthly_collection.values,
                title="Monthly Collection Trend",
                markers=True,
                labels={'x': 'Month', 'y': 'Amount (Rs.)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Fee type distribution
            fee_types = {
                'Monthly Fees': df[df['Monthly Fee'] > 0]['Monthly Fee'].sum(),
                'Annual Charges': df[df['Annual Charges'] > 0]['Annual Charges'].sum(),
                'Admission Fees': df[df['Admission Fee'] > 0]['Admission Fee'].sum()
            }
            
            fig = px.pie(
                values=list(fee_types.values()),
                names=list(fee_types.keys()),
                title="Fee Type Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Student Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Students by class
            class_students = df.groupby('Class Category')['Student Name'].nunique().sort_values(ascending=False)
            fig = px.bar(
                x=class_students.index,
                y=class_students.values,
                title="Students by Class",
                labels={'x': 'Class', 'y': 'Number of Students'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top paying students
            top_students = df.groupby('Student Name')['Received Amount'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(
                x=top_students.values,
                y=top_students.index,
                orientation='h',
                title="Top 10 Paying Students",
                labels={'x': 'Amount Paid (Rs.)', 'y': 'Student Name'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Payment Methods Analysis")
        
        payment_methods = df.groupby('Payment Method')['Received Amount'].sum().sort_values(ascending=False)
        
        fig = px.pie(
            values=payment_methods.values,
            names=payment_methods.index,
            title="Collection by Payment Method"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Payment method details
        st.subheader("Payment Method Details")
        payment_summary = df.groupby('Payment Method').agg({
            'Received Amount': 'sum',
            'ID': 'count'
        }).reset_index()
        payment_summary.columns = ['Payment Method', 'Total Amount', 'Number of Transactions']
        
        st.dataframe(
            payment_summary.style.format({
                'Total Amount': format_currency
            }),
            use_container_width=True
        )

def fee_settings():
    """Fee settings management"""
    st.header("💸 Fee Settings")
    
    tab1, tab2 = st.tabs(["⚙️ Default Fees", "🎒 Student-wise Fees"])
    
    with tab1:
        st.subheader("Default Fee Settings")
        from admin import set_default_fees
        set_default_fees()
    
    with tab2:
        st.subheader("Student-wise Fee Settings")
        from admin import set_student_fees
        set_student_fees()

def payment_systems():
    """Payment systems configuration"""
    st.header("💳 Payment Systems")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏦 Payment Configuration", "💳 Real Payment", "📱 JazzCash", "📲 EasyPaisa"])
    
    with tab1:
        st.subheader("Payment Gateway Configuration")
        from payment_config import payment_config_page
        payment_config_page()
    
    with tab2:
        st.subheader("Real Payment System")
        from real_payment_system import real_payment_page
        real_payment_page()
    
    with tab3:
        st.subheader("JazzCash Payment")
        from jazz_cash import jazzcash_payment_page
        jazzcash_payment_page()
    
    with tab4:
        st.subheader("EasyPaisa Payment")
        from easy_paisa import easypaisa_payment_page
        easypaisa_payment_page()

# For backward compatibility
def admin_dashboard_old():
    """Old admin dashboard with sidebar (for compatibility)"""
    admin_dashboard()
# [file content end]