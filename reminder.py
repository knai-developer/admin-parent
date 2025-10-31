# type:ignore
import streamlit as st
import pandas as pd
from datetime import datetime
from database import load_data, load_student_details
from utils import format_currency

def fee_reminder_page():
    """Fee reminder page showing unpaid students when date is 8th or later"""
    
    st.header("Fee Payment Reminder")
    
    # Get current date
    today = datetime.now()
    current_date = today.day
    current_month = today.strftime("%B").upper()
    
    # Check if date is 8th or later
    if current_date < 8:
        st.info(f"📅 Reminders will be shown from the 8th of each month. Current date: {current_date}")
        return
    
    st.warning(f"⏰ Reminder Period Active - {current_month} {current_date}, {today.year}")
    st.write("Students who have NOT paid full fees for this month:")
    
    st.divider()
    
    # Load data
    df = load_data()
    student_details = load_student_details()
    
    if df.empty:
        st.info("No fee records found")
        return
    
    # Get students who have paid full amount this month
    paid_full_this_month = set()
    
    for student_name in df['Student Name'].unique():
        student_records = df[(df['Student Name'] == student_name) & (df['Month'] == current_month)]
        
        if not student_records.empty:
            total_received = student_records['Received Amount'].sum()
            total_expected = (student_records['Monthly Fee'].sum() + 
                            student_records['Annual Charges'].sum() + 
                            student_records['Admission Fee'].sum())
            
            # Only mark as paid if received amount >= expected amount
            if total_received >= total_expected and total_expected > 0:
                paid_full_this_month.add(student_name)
    
    # Get all students who have records in the system
    all_students_with_records = set(df['Student Name'].unique())
    
    # Get unpaid students (those who haven't paid full amount)
    unpaid_students = all_students_with_records - paid_full_this_month
    
    if not unpaid_students:
        st.success("✅ All students have paid their fees for this month!")
        return
    
    # Create unpaid students list with details
    unpaid_list = []
    for student_id, details in student_details.items():
        student_name = details.get('student_name', '')
        if student_name in unpaid_students:
            unpaid_list.append({
                "Student Name": student_name,
                "Father Name": details.get('father_name', ''),
                "Class": details.get('class_category', ''),
                "Phone": details.get('phone', ''),
                "Address": details.get('address', '')
            })
    
    # Sort by class
    unpaid_df = pd.DataFrame(unpaid_list)
    unpaid_df = unpaid_df.sort_values('Class')
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Students with Records", len(all_students_with_records))
    with col2:
        st.metric("Paid Students", len(paid_full_this_month))
    with col3:
        st.metric("Unpaid Students", len(unpaid_students))
    
    st.divider()
    
    # Display unpaid students
    st.subheader(f"Unpaid Students List ({len(unpaid_students)} students)")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_class = st.selectbox(
            "Filter by Class",
            ["All"] + sorted(unpaid_df['Class'].unique().tolist())
        )
    with col2:
        search_name = st.text_input("Search by Student Name")
    
    # Apply filters
    filtered_df = unpaid_df.copy()
    if selected_class != "All":
        filtered_df = filtered_df[filtered_df['Class'] == selected_class]
    if search_name:
        filtered_df = filtered_df[filtered_df['Student Name'].str.contains(search_name, case=False)]
    
    # Display table
    st.dataframe(
        filtered_df[['Student Name', 'Father Name', 'Class', 'Phone', 'Address']],
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Class-wise summary
    st.subheader("Unpaid Students by Class")
    
    class_summary = unpaid_df.groupby('Class').size().reset_index(name='Count')
    class_summary = class_summary.sort_values('Count', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(class_summary, use_container_width=True, hide_index=True)
    
    with col2:
        # Chart
        import plotly.express as px
        fig = px.bar(
            class_summary,
            x='Class',
            y='Count',
            title='Unpaid Students by Class',
            labels={'Count': 'Number of Students', 'Class': 'Class'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Export option
    st.subheader("Export Reminder List")
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Unpaid Students List (CSV)",
        data=csv,
        file_name=f"unpaid_students_{current_month}_{today.year}.csv",
        mime="text/csv"
    )
    
    # WhatsApp message template
    st.subheader("WhatsApp Message Template")
    
    message_template = f"""
Dear Parent,

This is a friendly reminder that the fee payment for {current_month} is due.

Please arrange to pay the outstanding fees at your earliest convenience.

For any queries, please contact the school office.

Thank you!
"""
    
    st.text_area("Message Template", value=message_template, height=150, disabled=True)
