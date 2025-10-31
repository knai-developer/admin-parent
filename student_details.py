# type:ignore
import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    generate_student_id, save_to_csv, load_data, 
    load_student_details, save_student_details, add_student_detail,
    load_school_config
)
from utils import format_currency
import base64

def display_menu_bar():
    """Display menu bar with school name and logo"""
    school_config = load_school_config()
    school_name = school_config.get("school_name", "School Name")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        try:
            with open("school-pic.png", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            st.markdown(
                f'<img src="data:image/png;base64,{img_base64}" alt="School Logo" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">',
                unsafe_allow_html=True
            )
        except:
            st.markdown("🏫")
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <h3 style="margin: 0; color: #2c3e50;">{school_name}</h3>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">Student Management</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("")
    
    st.markdown("---")

def student_management_page():
    """Main page for managing student details"""
    display_menu_bar()
    
    st.header("Student Details Management")
    
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Students", "View Students", "Class-wise Details"])
    
    with tab1:
        add_students_section(CLASS_CATEGORIES)
    
    with tab2:
        view_students_section()
    
    with tab3:
        classwise_fee_details_section(CLASS_CATEGORIES)

def add_students_section(CLASS_CATEGORIES):
    """Section to add multiple students at once"""
    st.subheader("Add Multiple Students")
    
    st.info("You can add multiple students here at once")
    
    # Option to add students one by one or bulk upload
    add_method = st.radio("Select Method:", ["Add One by One", "Upload from CSV"])
    
    if add_method == "Add One by One":
        add_students_manually(CLASS_CATEGORIES)
    else:
        add_students_from_csv(CLASS_CATEGORIES)

def add_students_manually(CLASS_CATEGORIES):
    """Add students one by one"""
    st.markdown("### Enter Student Details")
    
    # Initialize session state for dynamic form
    if 'student_forms' not in st.session_state:
        st.session_state.student_forms = [{}]
    
    # Display form for each student
    for idx, student_form in enumerate(st.session_state.student_forms):
        with st.expander(f"Student #{idx + 1}", expanded=(idx == 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input(
                    "Student Name*",
                    placeholder="Full name",
                    key=f"student_name_{idx}",
                    value=student_form.get("student_name", "")
                )
                father_name = st.text_input(
                    "Father Name*",
                    placeholder="Father's full name",
                    key=f"father_name_{idx}",
                    value=student_form.get("father_name", "")
                )
                phone = st.text_input(
                    "Phone Number*",
                    placeholder="03001234567",
                    key=f"phone_{idx}",
                    value=student_form.get("phone", "")
                )
            
            with col2:
                class_category = st.selectbox(
                    "Class*",
                    CLASS_CATEGORIES,
                    key=f"class_{idx}",
                    index=CLASS_CATEGORIES.index(student_form.get("class_category", CLASS_CATEGORIES[0]))
                )
                age = st.number_input(
                    "Age*",
                    min_value=3,
                    max_value=25,
                    key=f"age_{idx}",
                    value=student_form.get("age", 5)
                )
                address = st.text_area(
                    "Address*",
                    placeholder="Full address",
                    key=f"address_{idx}",
                    value=student_form.get("address", ""),
                    height=80
                )
            
            # Update session state
            st.session_state.student_forms[idx] = {
                "student_name": student_name,
                "father_name": father_name,
                "phone": phone,
                "class_category": class_category,
                "age": age,
                "address": address
            }
    
    # Add more student button
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add Another Student"):
            st.session_state.student_forms.append({})
            st.rerun()
    
    with col2:
        if len(st.session_state.student_forms) > 1:
            if st.button("Remove Last Student"):
                st.session_state.student_forms.pop()
                st.rerun()
    
    with col3:
        if st.button("Save All Students"):
            save_all_students(st.session_state.student_forms)

def save_all_students(students_list):
    """Save all students to database"""
    if not students_list:
        st.error("No students to save")
        return
    
    # Validate all students
    for idx, student in enumerate(students_list):
        if not student.get("student_name") or not student.get("father_name") or not student.get("phone") or not student.get("address"):
            st.error(f"Student #{idx + 1} - Please fill all required fields")
            return
    
    # Save all students
    student_details = load_student_details()
    saved_count = 0
    
    for student in students_list:
        student_id = generate_student_id(student["student_name"], student["class_category"])
        
        if add_student_detail(
            student_id,
            student["student_name"],
            student["father_name"],
            student["class_category"],
            student["address"],
            student["phone"],
            student["age"]
        ):
            saved_count += 1
    
    if saved_count == len(students_list):
        st.success(f"Successfully saved {saved_count} students!")
        st.session_state.student_forms = [{}]
        st.rerun()
    else:
        st.error(f"Only {saved_count}/{len(students_list)} students were saved")

def add_students_from_csv(CLASS_CATEGORIES):
    """Add students from CSV file"""
    st.markdown("### Upload Students from CSV")
    
    st.info("""
    **CSV File Format Required:**
    - Student Name
    - Father Name
    - Phone
    - Class
    - Age
    - Address
    """)
    
    uploaded_file = st.file_uploader("Select CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate columns
            required_columns = ['Student Name', 'Father Name', 'Phone', 'Class', 'Age', 'Address']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing columns: {', '.join(missing_columns)}")
                return
            
            # Preview data
            st.subheader("Data Preview")
            st.dataframe(df)
            
            if st.button("Save Students from CSV"):
                saved_count = 0
                errors = []
                
                for idx, row in df.iterrows():
                    try:
                        student_id = generate_student_id(row['Student Name'], row['Class'])
                        
                        if add_student_detail(
                            student_id,
                            row['Student Name'],
                            row['Father Name'],
                            row['Class'],
                            row['Address'],
                            row['Phone'],
                            int(row['Age'])
                        ):
                            saved_count += 1
                        else:
                            errors.append(f"Row {idx + 1}: {row['Student Name']} - Could not save")
                    except Exception as e:
                        errors.append(f"Row {idx + 1}: {str(e)}")
                
                st.success(f"Successfully saved {saved_count}/{len(df)} students!")
                
                if errors:
                    st.warning("Some errors occurred:")
                    for error in errors:
                        st.write(f"- {error}")
        
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

def view_students_section():
    """View all students"""
    st.subheader("View All Students")
    
    student_details = load_student_details()
    
    if not student_details:
        st.info("No students found")
        return
    
    # Convert to DataFrame
    students_list = []
    for student_id, details in student_details.items():
        students_list.append({
            "Student ID": student_id,
            "Name": details.get("student_name", ""),
            "Father Name": details.get("father_name", ""),
            "Phone": details.get("phone", ""),
            "Class": details.get("class_category", ""),
            "Age": details.get("age", ""),
            "Address": details.get("address", "")
        })
    
    df = pd.DataFrame(students_list)
    
    # Search functionality
    search_term = st.text_input("Search student (by name or phone)")
    
    if search_term:
        df = df[
            df["Name"].str.contains(search_term, case=False, na=False) |
            df["Phone"].str.contains(search_term, case=False, na=False)
        ]
    
    st.dataframe(df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Students as CSV",
        data=csv,
        file_name=f"students_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def classwise_fee_details_section(CLASS_CATEGORIES):
    """View class-wise fee details"""
    st.subheader("Class-wise Fee Details")
    
    selected_class = st.selectbox("Select Class:", CLASS_CATEGORIES)
    
    if selected_class:
        # Load data
        df = load_data()
        student_details = load_student_details()
        
        if df.empty:
            st.info("No fee records found")
            return
        
        # Filter by class
        class_data = df[df['Class Category'] == selected_class].copy()
        
        if class_data.empty:
            st.info(f"No fee records found for {selected_class}")
            return
        
        # Get unique students in this class
        unique_students = class_data['ID'].unique()
        
        st.markdown(f"### Total Students in {selected_class}: {len(unique_students)}")
        
        # Create summary for each student
        student_summaries = []
        
        for student_id in unique_students:
            student_records = class_data[class_data['ID'] == student_id]
            student_name = student_records['Student Name'].iloc[0]
            
            # Get student details
            detail = student_details.get(student_id, {})
            father_name = detail.get("father_name", "N/A")
            phone = detail.get("phone", "N/A")
            
            # Calculate totals
            total_monthly = student_records[student_records['Month'] != 'ANNUAL'][student_records['Month'] != 'ADMISSION']['Monthly Fee'].sum()
            total_annual = student_records['Annual Charges'].sum()
            total_admission = student_records['Admission Fee'].sum()
            total_received = student_records['Received Amount'].sum()
            
            # Count paid months
            paid_months = len(student_records[student_records['Monthly Fee'] > 0])
            
            student_summaries.append({
                "Student ID": student_id,
                "Name": student_name,
                "Father Name": father_name,
                "Phone": phone,
                "Monthly Fees": format_currency(total_monthly),
                "Annual Fees": format_currency(total_annual),
                "Admission Fee": format_currency(total_admission),
                "Total Received": format_currency(total_received),
                "Paid Months": paid_months
            })
        
        summary_df = pd.DataFrame(student_summaries)
        st.dataframe(summary_df, use_container_width=True)
        
        # Class statistics
        st.markdown("### Class Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_monthly_class = class_data[class_data['Month'] != 'ANNUAL'][class_data['Month'] != 'ADMISSION']['Monthly Fee'].sum()
        total_annual_class = class_data['Annual Charges'].sum()
        total_admission_class = class_data['Admission Fee'].sum()
        total_received_class = class_data['Received Amount'].sum()
        
        col1.metric("Total Monthly Fees", format_currency(total_monthly_class))
        col2.metric("Total Annual Fees", format_currency(total_annual_class))
        col3.metric("Total Admission Fees", format_currency(total_admission_class))
        col4.metric("Total Received", format_currency(total_received_class))
        
        # Download class report
        csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {selected_class} Report",
            data=csv,
            file_name=f"{selected_class}_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def class_wise_fee_details():
    """Wrapper function for class-wise fee details"""
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    classwise_fee_details_section(CLASS_CATEGORIES)
