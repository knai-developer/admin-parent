# type:ignore
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from database import load_data, update_data

def payment_verification_page():
    """Payment verification page for parents to verify and track payments"""
    
    st.title("✅ Payment Verification & Tracking")
    
    # Student selection
    student_id = st.text_input("Enter Student ID", placeholder="STUDENT_ID_HERE")
    
    if student_id:
        verify_payment_status(student_id)
        show_payment_tracking(student_id)
        show_upcoming_payments(student_id)

def verify_payment_status(student_id):
    """Verify payment status for a student"""
    
    st.subheader("🔍 Payment Status Verification")
    
    df = load_data()
    if df.empty:
        st.error("No payment records found")
        return
    
    student_records = df[df['ID'] == student_id]
    
    if student_records.empty:
        st.error("No records found for this Student ID")
        return
    
    # Get student details
    student_name = student_records.iloc[0]['Student Name']
    class_category = student_records.iloc[0]['Class Category']
    
    st.success(f"**Student:** {student_name} | **Class:** {class_category}")
    
    # Current academic year
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year+1}"
    
    # Calculate payment summary
    yearly_records = student_records[student_records['Academic Year'] == academic_year]
    
    if yearly_records.empty:
        st.warning("No payments found for current academic year")
        return
    
    # Monthly fee analysis
    monthly_payments = yearly_records[yearly_records['Monthly Fee'] > 0]
    paid_months = monthly_payments['Month'].unique().tolist()
    
    # All months in academic year
    all_months = ["APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                 "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"]
    
    unpaid_months = [month for month in all_months if month not in paid_months]
    
    # Annual and admission fees
    annual_paid = yearly_records['Annual Charges'].sum() > 0
    admission_paid = yearly_records['Admission Fee'].sum() > 0
    
    # Display status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Paid Months", len(paid_months))
        if paid_months:
            st.write("**Months:**", ", ".join(paid_months))
    
    with col2:
        st.metric("Unpaid Months", len(unpaid_months))
        if unpaid_months:
            st.write("**Months:**", ", ".join(unpaid_months))
    
    with col3:
        st.metric("Annual Fee", "✅ Paid" if annual_paid else "❌ Unpaid")
        st.metric("Admission Fee", "✅ Paid" if admission_paid else "❌ Unpaid")
    
    # Payment timeline
    st.subheader("📅 Payment Timeline")
    
    if not monthly_payments.empty:
        timeline_data = []
        for _, payment in monthly_payments.iterrows():
            timeline_data.append({
                "Month": payment['Month'],
                "Amount": payment['Monthly Fee'],
                "Date": payment['Date'],
                "Method": payment['Payment Method']
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        st.dataframe(timeline_df, use_container_width=True)
    else:
        st.info("No monthly payments recorded for current academic year")

def show_payment_tracking(student_id):
    """Show detailed payment tracking"""
    
    st.subheader("💰 Payment Tracking")
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if student_records.empty:
        return
    
    # Filter current academic year
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year+1}"
    yearly_records = student_records[student_records['Academic Year'] == academic_year]
    
    if yearly_records.empty:
        return
    
    # Total calculations
    total_monthly = yearly_records['Monthly Fee'].sum()
    total_annual = yearly_records['Annual Charges'].sum()
    total_admission = yearly_records['Admission Fee'].sum()
    total_received = yearly_records['Received Amount'].sum()
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Monthly Fees", f"₹{total_monthly:,}")
    col2.metric("Annual Charges", f"₹{total_annual:,}")
    col3.metric("Admission Fee", f"₹{total_admission:,}")
    col4.metric("Total Received", f"₹{total_received:,}")
    
    # Recent payments table
    st.subheader("📋 Recent Payment History")
    
    recent_payments = yearly_records[['Date', 'Month', 'Monthly Fee', 'Annual Charges', 
                                    'Admission Fee', 'Received Amount', 'Payment Method']].copy()
    
    # Format currency
    for col in ['Monthly Fee', 'Annual Charges', 'Admission Fee', 'Received Amount']:
        recent_payments[col] = recent_payments[col].apply(lambda x: f"₹{x:,}" if x > 0 else "-")
    
    st.dataframe(recent_payments.sort_values('Date', ascending=False), 
                use_container_width=True, hide_index=True)

def show_upcoming_payments(student_id):
    """Show upcoming payment schedule"""
    
    st.subheader("📈 Upcoming Payment Schedule")
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if student_records.empty:
        return
    
    # Get current month and year
    current_month = datetime.now().strftime('%B').upper()
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year+1}"
    
    # Paid months in current academic year
    yearly_records = student_records[student_records['Academic Year'] == academic_year]
    paid_months = yearly_records[yearly_records['Monthly Fee'] > 0]['Month'].unique().tolist()
    
    # Month order for academic year
    month_order = ["APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                  "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"]
    
    # Create payment schedule
    schedule_data = []
    for month in month_order:
        status = "✅ Paid" if month in paid_months else "❌ Unpaid"
        
        # Highlight current and upcoming months
        if month == current_month:
            status = "🔵 Current Month"
        elif month not in paid_months and month_order.index(month) > month_order.index(current_month):
            status = "🟡 Upcoming"
        
        schedule_data.append({
            "Month": month,
            "Status": status,
            "Due Date": "1st of Month",
            "Late Fee After": "10th of Month"
        })
    
    schedule_df = pd.DataFrame(schedule_data)
    st.dataframe(schedule_df, use_container_width=True, hide_index=True)
    
    # Payment recommendations
    st.subheader("💡 Payment Recommendations")
    
    unpaid_months = [month for month in month_order if month not in paid_months]
    current_month_index = month_order.index(current_month)
    
    overdue_months = []
    upcoming_months = []
    
    for month in unpaid_months:
        month_index = month_order.index(month)
        if month_index <= current_month_index:
            overdue_months.append(month)
        else:
            upcoming_months.append(month)
    
    if overdue_months:
        st.error(f"**Overdue Payments:** {', '.join(overdue_months)}")
        st.warning("Please clear overdue payments to avoid late fees")
    
    if upcoming_months:
        st.info(f"**Upcoming Payments:** {', '.join(upcoming_months[:3])}")
    
    if not overdue_months and not upcoming_months:
        st.success("🎉 All payments are up to date!")

def check_payment_eligibility(student_id, month, fee_type):
    """Check if a payment can be made for specific month/fee type"""
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if student_records.empty:
        return True  # New student
    
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year+1}"
    
    yearly_records = student_records[student_records['Academic Year'] == academic_year]
    
    if fee_type == "monthly":
        # Check if month already paid
        month_paid = yearly_records[
            (yearly_records['Month'] == month) & 
            (yearly_records['Monthly Fee'] > 0)
        ]
        return month_paid.empty
    
    elif fee_type == "annual":
        # Check if annual charges already paid
        annual_paid = yearly_records['Annual Charges'].sum() > 0
        return not annual_paid
    
    elif fee_type == "admission":
        # Check if admission fee already paid
        admission_paid = yearly_records['Admission Fee'].sum() > 0
        return not admission_paid
    
    return True

def get_payment_summary(student_id):
    """Get comprehensive payment summary for student"""
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if student_records.empty:
        return None
    
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year+1}"
    yearly_records = student_records[student_records['Academic Year'] == academic_year]
    
    # Calculate totals
    total_monthly = yearly_records['Monthly Fee'].sum()
    total_annual = yearly_records['Annual Charges'].sum()
    total_admission = yearly_records['Admission Fee'].sum()
    total_received = yearly_records['Received Amount'].sum()
    
    # Monthly breakdown
    paid_months = yearly_records[yearly_records['Monthly Fee'] > 0]['Month'].unique().tolist()
    
    # All months in academic year
    all_months = ["APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
                 "OCTOBER", "NOVEMBER", "DECEMBER", "JANUARY", "FEBRUARY", "MARCH"]
    
    unpaid_months = [month for month in all_months if month not in paid_months]
    
    return {
        "student_name": student_records.iloc[0]['Student Name'],
        "class_category": student_records.iloc[0]['Class Category'],
        "academic_year": academic_year,
        "total_monthly": total_monthly,
        "total_annual": total_annual,
        "total_admission": total_admission,
        "total_received": total_received,
        "paid_months": paid_months,
        "unpaid_months": unpaid_months,
        "annual_paid": total_annual > 0,
        "admission_paid": total_admission > 0
    }

# Main function to run the page
if __name__ == "__main__":
    payment_verification_page()