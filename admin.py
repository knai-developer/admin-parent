# type:ignore
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from database import (
    load_data, load_student_fees, save_student_fees, generate_student_id,
    load_default_fees, save_default_fees, load_school_config, save_school_config,
    load_student_details, add_student_detail
)
from utils import format_currency

def user_management():
    """User management section for admin"""
    st.header("User Management")
    
    tab1, tab2, tab3 = st.tabs(["View Users", "Add User", "Manage Permissions"])
    
    with tab1:
        st.subheader("Registered Users")
        
        # Load users from JSON
        users_data = load_users()
        
        if not users_data:
            st.info("No users registered yet")
        else:
            # Convert to DataFrame for display
            users_list = []
            for user_id, user_info in users_data.items():
                users_list.append({
                    "User ID": user_id,
                    "Email": user_info.get('email', ''),
                    "Role": user_info.get('role', 'User'),
                    "Status": user_info.get('status', 'Active'),
                    "Created": user_info.get('created_at', ''),
                    "Last Login": user_info.get('last_login', 'Never')
                })
            
            users_df = pd.DataFrame(users_list)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                role_filter = st.selectbox("Filter by Role", ["All", "Admin", "User", "Accountant"])
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
            
            # Apply filters
            filtered_df = users_df.copy()
            if role_filter != "All":
                filtered_df = filtered_df[filtered_df['Role'] == role_filter]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # User statistics
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", len(users_df))
            with col2:
                admin_count = len(users_df[users_df['Role'] == 'Admin'])
                st.metric("Admins", admin_count)
            with col3:
                active_count = len(users_df[users_df['Status'] == 'Active'])
                st.metric("Active Users", active_count)
            with col4:
                inactive_count = len(users_df[users_df['Status'] == 'Inactive'])
                st.metric("Inactive Users", inactive_count)
    
    with tab2:
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email Address*", placeholder="user@example.com")
                password = st.text_input("Password*", type="password", placeholder="Enter password")
            
            with col2:
                role = st.selectbox("User Role*", ["User", "Admin", "Accountant"])
                confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Confirm password")
            
            full_name = st.text_input("Full Name", placeholder="User's full name")
            phone = st.text_input("Phone Number", placeholder="03001234567")
            
            submit = st.form_submit_button("Add User")
            
            if submit:
                # Validation
                if not email or not password or not confirm_password:
                    st.error("Email and password are required")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif "@" not in email:
                    st.error("Please enter a valid email address")
                else:
                    # Check if user already exists
                    users_data = load_users()
                    if email in users_data:
                        st.error("User with this email already exists")
                    else:
                        # Add new user
                        from hashlib import md5
                        hashed_password = md5(password.encode()).hexdigest()
                        
                        users_data[email] = {
                            "email": email,
                            "password": hashed_password,
                            "role": role,
                            "full_name": full_name,
                            "phone": phone,
                            "status": "Active",
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "last_login": "Never"
                        }
                        
                        if save_users(users_data):
                            st.success(f"User '{email}' added successfully with role '{role}'")
                        else:
                            st.error("Failed to add user")
    
    with tab3:
        st.subheader("Manage User Permissions")
        
        users_data = load_users()
        
        if not users_data:
            st.info("No users to manage")
        else:
            selected_email = st.selectbox(
                "Select User",
                list(users_data.keys())
            )
            
            if selected_email:
                user_info = users_data[selected_email]
                
                st.write(f"**User:** {user_info.get('full_name', 'N/A')}")
                st.write(f"**Email:** {selected_email}")
                st.write(f"**Current Role:** {user_info.get('role', 'User')}")
                
                st.divider()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_role = st.selectbox(
                        "Change Role",
                        ["User", "Admin", "Accountant"],
                        index=["User", "Admin", "Accountant"].index(user_info.get('role', 'User'))
                    )
                
                with col2:
                    new_status = st.selectbox(
                        "Change Status",
                        ["Active", "Inactive"],
                        index=["Active", "Inactive"].index(user_info.get('status', 'Active'))
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Update User", use_container_width=True):
                        users_data[selected_email]['role'] = new_role
                        users_data[selected_email]['status'] = new_status
                        
                        if save_users(users_data):
                            st.success(f"User '{selected_email}' updated successfully")
                        else:
                            st.error("Failed to update user")
                
                with col2:
                    if st.button("Delete User", use_container_width=True):
                        if st.confirm("Are you sure you want to delete this user?"):
                            del users_data[selected_email]
                            if save_users(users_data):
                                st.success(f"User '{selected_email}' deleted successfully")
                            else:
                                st.error("Failed to delete user")

def set_default_fees():
    """Set default fees for all classes"""
    st.subheader("Set Default Fees")
    
    # Load current default fees
    default_fees = load_default_fees()
    
    st.info("These are the default fees applied to all students unless they have custom fees set")
    
    with st.form("default_fees_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            monthly_fee = st.number_input(
                "Monthly Fee (Rs.)*",
                min_value=0,
                value=int(default_fees.get('monthly_fee', 3000)),
                step=100
            )
        
        with col2:
            annual_charges = st.number_input(
                "Annual Charges (Rs.)*",
                min_value=0,
                value=int(default_fees.get('annual_charges', 3500)),
                step=100
            )
        
        with col3:
            admission_fee = st.number_input(
                "Admission Fee (Rs.)*",
                min_value=0,
                value=int(default_fees.get('admission_fee', 10000)),
                step=100
            )
        
        st.divider()
        
        # Display total
        total_default = monthly_fee + annual_charges + admission_fee
        st.metric("Total Default Fees", format_currency(total_default))
        
        submit = st.form_submit_button("Update Default Fees")
        
        if submit:
            new_fees = {
                "monthly_fee": monthly_fee,
                "annual_charges": annual_charges,
                "admission_fee": admission_fee
            }
            
            if save_default_fees(new_fees):
                st.success("Default fees updated successfully!")
                st.balloons()
            else:
                st.error("Failed to update default fees")
    
    st.divider()
    
    # Show current default fees summary
    st.subheader("Current Default Fees Summary")
    
    summary_data = {
        "Fee Type": ["Monthly Fee", "Annual Charges", "Admission Fee", "Total"],
        "Amount (Rs.)": [
            format_currency(default_fees.get('monthly_fee', 0)),
            format_currency(default_fees.get('annual_charges', 0)),
            format_currency(default_fees.get('admission_fee', 0)),
            format_currency(
                default_fees.get('monthly_fee', 0) + 
                default_fees.get('annual_charges', 0) + 
                default_fees.get('admission_fee', 0)
            )
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

def set_student_fees():
    """Set custom fees for individual students"""
    st.subheader("Set Student-wise Fees")
    
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    tab1, tab2, tab3 = st.tabs(["Add/Update Student Fee", "View Student Fees", "Bulk Update"])
    
    with tab1:
        st.subheader("Add or Update Student Fee")
        
        # Load student details
        student_details = load_student_details()
        
        if not student_details:
            st.warning("No students found. Please add students first in Student Management.")
        else:
            # Create student list for selection
            student_options = {}
            for student_id, details in student_details.items():
                student_name = details.get('student_name', '')
                father_name = details.get('father_name', '')
                class_cat = details.get('class_category', '')
                student_options[f"{student_name} (Father: {father_name}) - {class_cat}"] = student_id
            
            selected_student = st.selectbox(
                "Select Student*",
                list(student_options.keys())
            )
            
            if selected_student:
                student_id = student_options[selected_student]
                student_info = student_details[student_id]
                
                # Display student info with father name
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**Name:** {student_info.get('student_name', '')}")
                with col2:
                    st.write(f"**Father:** {student_info.get('father_name', '')}")
                with col3:
                    st.write(f"**Class:** {student_info.get('class_category', '')}")
                with col4:
                    st.write(f"**Phone:** {student_info.get('phone', '')}")
                
                st.divider()
                
                # Load current student fees if exists
                student_fees = load_student_fees()
                current_fees = student_fees.get(student_id, {})
                
                # Load default fees for reference
                default_fees = load_default_fees()
                
                with st.form("student_fee_form"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        monthly_fee = st.number_input(
                            "Monthly Fee (Rs.)*",
                            min_value=0,
                            value=int(current_fees.get('monthly_fee', default_fees.get('monthly_fee', 3000))),
                            step=100
                        )
                    
                    with col2:
                        annual_charges = st.number_input(
                            "Annual Charges (Rs.)*",
                            min_value=0,
                            value=int(current_fees.get('annual_charges', default_fees.get('annual_charges', 3500))),
                            step=100
                        )
                    
                    with col3:
                        admission_fee = st.number_input(
                            "Admission Fee (Rs.)*",
                            min_value=0,
                            value=int(current_fees.get('admission_fee', default_fees.get('admission_fee', 10000))),
                            step=100
                        )
                    
                    st.divider()
                    
                    # Display total
                    total_student_fee = monthly_fee + annual_charges + admission_fee
                    st.metric("Total Student Fees", format_currency(total_student_fee))
                    
                    submit = st.form_submit_button("Save Student Fees")
                    
                    if submit:
                        student_fees[student_id] = {
                            "student_name": student_info.get('student_name', ''),
                            "father_name": student_info.get('father_name', ''),
                            "class_category": student_info.get('class_category', ''),
                            "monthly_fee": monthly_fee,
                            "annual_charges": annual_charges,
                            "admission_fee": admission_fee,
                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        if save_student_fees(student_fees):
                            st.success(f"Fees for '{student_info.get('student_name', '')}' updated successfully!")
                            st.balloons()
                        else:
                            st.error("Failed to save student fees")
    
    with tab2:
        st.subheader("View All Student Fees")
        
        student_fees = load_student_fees()
        
        if not student_fees:
            st.info("No custom student fees set yet. All students are using default fees.")
        else:
            # Convert to DataFrame
            fees_list = []
            for student_id, fees_info in student_fees.items():
                fees_list.append({
                    "Student Name": fees_info.get('student_name', ''),
                    "Father Name": fees_info.get('father_name', ''),
                    "Class": fees_info.get('class_category', ''),
                    "Monthly Fee": fees_info.get('monthly_fee', 0),
                    "Annual Charges": fees_info.get('annual_charges', 0),
                    "Admission Fee": fees_info.get('admission_fee', 0),
                    "Total": fees_info.get('monthly_fee', 0) + fees_info.get('annual_charges', 0) + fees_info.get('admission_fee', 0),
                    "Updated": fees_info.get('updated_at', '')
                })
            
            fees_df = pd.DataFrame(fees_list)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                selected_class = st.selectbox("Filter by Class", ["All"] + CLASS_CATEGORIES)
            with col2:
                search_name = st.text_input("Search by Name")
            
            # Apply filters
            filtered_df = fees_df.copy()
            if selected_class != "All":
                filtered_df = filtered_df[filtered_df['Class'] == selected_class]
            if search_name:
                filtered_df = filtered_df[filtered_df['Student Name'].str.contains(search_name, case=False)]
            
            # Display with formatting
            display_df = filtered_df.copy()
            
            st.dataframe(
                display_df.style.format({
                    'Monthly Fee': format_currency,
                    'Annual Charges': format_currency,
                    'Admission Fee': format_currency,
                    'Total': format_currency
                }),
                use_container_width=True
            )
            
            # Summary statistics
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Students with Custom Fees", len(filtered_df))
            with col2:
                avg_total = filtered_df['Total'].mean()
                st.metric("Average Total Fees", format_currency(avg_total))
            with col3:
                total_all = filtered_df['Total'].sum()
                st.metric("Total All Fees", format_currency(total_all))
    
    with tab3:
        st.subheader("Bulk Update Student Fees")
        
        st.info("""
        **CSV Format Required:**
        - Column 1: Student Name
        - Column 2: Father Name
        - Column 3: Class
        - Column 4: Monthly Fee
        - Column 5: Annual Charges
        - Column 6: Admission Fee
        """)
        
        uploaded_file = st.file_uploader("Choose CSV file for bulk update", type="csv")
        
        if uploaded_file is not None:
            try:
                bulk_df = pd.read_csv(uploaded_file)
                
                # Validate columns
                required_cols = ['Student Name', 'Father Name', 'Class', 'Monthly Fee', 'Annual Charges', 'Admission Fee']
                if not all(col in bulk_df.columns for col in required_cols):
                    st.error(f"CSV must contain columns: {', '.join(required_cols)}")
                else:
                    st.dataframe(bulk_df, use_container_width=True)
                    
                    if st.button("Update All Student Fees"):
                        student_details = load_student_details()
                        student_fees = load_student_fees()
                        updated_count = 0
                        
                        for _, row in bulk_df.iterrows():
                            student_id = generate_student_id(row['Student Name'], row['Class'])
                            
                            student_fees[student_id] = {
                                "student_name": row['Student Name'],
                                "father_name": row['Father Name'],
                                "class_category": row['Class'],
                                "monthly_fee": int(row['Monthly Fee']),
                                "annual_charges": int(row['Annual Charges']),
                                "admission_fee": int(row['Admission Fee']),
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            updated_count += 1
                        
                        if save_student_fees(student_fees):
                            st.success(f"{updated_count} student fees updated successfully!")
                            st.balloons()
                        else:
                            st.error("Failed to update student fees")
            
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

def admin_page(section_name):
    """Admin page for school configuration"""
    st.header(section_name)
    
    # Load current config
    config = load_school_config()
    
    with st.form("school_config_form"):
        school_name = st.text_input(
            "School Name*",
            value=config.get('school_name', 'Your School Name')
        )
        
        school_address = st.text_area(
            "School Address",
            value=config.get('school_address', ''),
            height=100
        )
        
        school_phone = st.text_input(
            "School Phone Number",
            value=config.get('school_phone', '')
        )
        
        school_email = st.text_input(
            "School Email",
            value=config.get('school_email', '')
        )
        
        principal_name = st.text_input(
            "Principal Name",
            value=config.get('principal_name', '')
        )
        
        academic_year = st.text_input(
            "Academic Year",
            value=config.get('academic_year', '2024-2025')
        )
        
        submit = st.form_submit_button("Update School Configuration")
        
        if submit:
            if not school_name:
                st.error("School name is required")
            else:
                config.update({
                    'school_name': school_name,
                    'school_address': school_address,
                    'school_phone': school_phone,
                    'school_email': school_email,
                    'principal_name': principal_name,
                    'academic_year': academic_year
                })
                
                if save_school_config(config):
                    st.success("School configuration updated successfully!")
                    st.balloons()
                else:
                    st.error("Failed to update school configuration")

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists("users.json"):
            with open("users.json", 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return {}

def save_users(users_data):
    """Save users to JSON file"""
    try:
        with open("users.json", 'w') as f:
            json.dump(users_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving users: {str(e)}")
        return False
