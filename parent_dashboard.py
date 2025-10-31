#type:ignore
import streamlit as st
import pandas as pd
from datetime import datetime
from parent_database import (
    get_student_fee_summary, 
    get_payment_history, 
    record_payment_request,
    get_payment_requests,
    export_payment_history_csv,
    get_unpaid_months,
    get_paid_months
)

def show_fee_summary(student_id):
    """Display fee summary for student with annual/admission fees"""
    try:
        summary = get_student_fee_summary(student_id)
        
        if not summary:
            st.error("❌ Student fee details not found")
            return
        
        st.subheader(f"📚 Fee Summary - {summary['student_name']}")
        
        # Main fee cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Fee", f"₹{summary['monthly_fee']:,}")
        
        with col2:
            st.metric("Admission Fee", f"₹{summary['admission_fee']:,}")
        
        with col3:
            st.metric("Annual Fee", f"₹{summary['annual_fee']:,}")
        
        with col4:
            st.metric("Total Due", f"₹{summary['total_yearly_due']:,}")
        
        # Payment progress
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Paid", f"₹{summary['total_received']:,}", delta=f"{summary['percentage_paid']}%")
        
        with col2:
            st.metric("Balance Due", f"₹{summary['balance_due']:,}")
        
        with col3:
            if summary['balance_due'] == 0:
                st.metric("Status", "🟢 PAID", delta="Complete")
            else:
                st.metric("Status", "🔴 PENDING", delta=f"₹{summary['balance_due']:,} due")
        
        # Progress bar
        progress = summary['percentage_paid'] / 100
        st.progress(progress, text=f"Payment Progress: {summary['percentage_paid']}%")
        
    except Exception as e:
        st.error(f"Error loading fee summary: {str(e)}")

def show_paid_unpaid_status(student_id):
    """Show paid and unpaid months clearly"""
    st.subheader("📊 Monthly Fee Status")
    
    try:
        paid_months = get_paid_months(student_id)
        unpaid_months = get_unpaid_months(student_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"✅ PAID MONTHS ({len(paid_months)})")
            if paid_months:
                for month_data in paid_months:
                    st.write(f"**{month_data['month']}** - ₹{month_data['amount']:,} ({month_data['date']})")
            else:
                st.info("No months paid yet")
        
        with col2:
            st.error(f"❌ UNPAID MONTHS ({len(unpaid_months)})")
            if unpaid_months:
                for month in unpaid_months:
                    st.write(f"**{month}** - Payment Pending")
            else:
                st.success("🎉 All months paid!")
                
    except Exception as e:
        st.error(f"Error loading payment status: {str(e)}")

def show_monthly_payment_section(student_id, parent_email):
    """Show monthly fee payment with month selection"""
    st.subheader("💳 Pay Monthly Fees")
    
    try:
        unpaid_months = get_unpaid_months(student_id)
        summary = get_student_fee_summary(student_id)
        
        if not summary:
            st.error("Cannot load fee details")
            return
            
        if not unpaid_months:
            st.success("✅ All monthly fees are paid! No payment required.")
            return
        
        monthly_fee = summary['monthly_fee']
        
        # Display current fee info
        st.info(f"**Monthly Fee Amount:** ₹{monthly_fee:,} per month")
        st.warning(f"**Unpaid Months Available:** {len(unpaid_months)} months")
        
        # Month selection
        st.write("### Select Months to Pay:")
        selected_months = st.multiselect(
            "Choose one or multiple months:",
            unpaid_months,
            help="You can select 1, 2, 3 or more months to pay at once"
        )
        
        if selected_months:
            total_amount = monthly_fee * len(selected_months)
            
            st.success(f"**Selected Months:** {', '.join(selected_months)}")
            st.success(f"**Total Amount to Pay:** ₹{total_amount:,}")
            
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
            
            # Confirm and submit
            st.write("### Confirm Payment")
            if st.button(f"🚀 Pay ₹{total_amount:,} via {payment_method}", type="primary", use_container_width=True):
                request_id = record_payment_request(
                    student_id,
                    parent_email,
                    total_amount,
                    f"Monthly Fee - {', '.join(selected_months)}",
                    payment_method,
                    selected_months
                )
                
                if request_id:
                    st.success("✅ Payment Request Submitted Successfully!")
                    st.balloons()
                    st.info(f"**Request ID:** {request_id}")
                    st.info("School will verify your payment and update the status within 24 hours.")
                else:
                    st.error("❌ Failed to submit payment request. Please try again.")
                    
    except Exception as e:
        st.error(f"Error in payment section: {str(e)}")

def show_annual_admission_payment(student_id, parent_email):
    """Show annual and admission fee payment options"""
    st.subheader("🎓 Pay Other Fees")
    
    try:
        summary = get_student_fee_summary(student_id)
        if not summary:
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Annual Fee Payment
            if summary['annual_fee'] > 0:
                st.write(f"**Annual Fee:** ₹{summary['annual_fee']:,}")
                
                payment_method_annual = st.selectbox(
                    "Payment Method for Annual Fee:",
                    ["JazzCash", "EasyPaisa", "Bank Transfer", "Credit/Debit Card"],
                    key="annual_method"
                )
                
                if st.button(f"💳 Pay Annual Fee - ₹{summary['annual_fee']:,}", key="pay_annual", use_container_width=True):
                    request_id = record_payment_request(
                        student_id,
                        parent_email,
                        summary['annual_fee'],
                        "Annual Fee",
                        payment_method_annual
                    )
                    if request_id:
                        st.success("✅ Annual fee payment request submitted!")
        
        with col2:
            # Admission Fee Payment  
            if summary['admission_fee'] > 0:
                st.write(f"**Admission Fee:** ₹{summary['admission_fee']:,}")
                
                payment_method_admission = st.selectbox(
                    "Payment Method for Admission Fee:",
                    ["JazzCash", "EasyPaisa", "Bank Transfer", "Credit/Debit Card"],
                    key="admission_method"
                )
                
                if st.button(f"💳 Pay Admission Fee - ₹{summary['admission_fee']:,}", key="pay_admission", use_container_width=True):
                    request_id = record_payment_request(
                        student_id,
                        parent_email,
                        summary['admission_fee'],
                        "Admission Fee", 
                        payment_method_admission
                    )
                    if request_id:
                        st.success("✅ Admission fee payment request submitted!")
                        
    except Exception as e:
        st.error(f"Error in annual/admission payment: {str(e)}")

def show_payment_history(student_id):
    """Display payment history"""
    st.subheader("📋 Payment History")
    
    try:
        history = get_payment_history(student_id)
        
        if not history:
            st.info("No payment history found")
            return
        
        # Create DataFrame
        df = pd.DataFrame(history)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date', ascending=False)
            
            # Display table
            st.dataframe(
                df[['date', 'amount', 'payment_method', 'reference', 'remarks']].rename(
                    columns={
                        'date': 'Date',
                        'amount': 'Amount (₹)',
                        'payment_method': 'Method',
                        'reference': 'Reference',
                        'remarks': 'Remarks'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv_data = export_payment_history_csv(student_id)
            st.download_button(
                label="📥 Download Payment History",
                data=csv_data,
                file_name=f"payment_history_{student_id}.csv",
                mime="text/csv"
            )
        else:
            st.info("No payment records available")
            
    except Exception as e:
        st.error(f"Error loading payment history: {str(e)}")

def show_pending_requests(student_id):
    """Show pending payment requests"""
    st.subheader("⏳ Pending Payment Requests")
    
    try:
        requests = get_payment_requests(student_id)
        
        pending_requests = [req for req in requests if req['status'] == 'pending']
        
        if not pending_requests:
            st.info("No pending payment requests")
            return
        
        for req in pending_requests:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,2,1])
                
                with col1:
                    st.write(f"**Request ID:** {req['request_id']}")
                    st.write(f"**Amount:** ₹{req['amount']:,}")
                    st.write(f"**Type:** {req['payment_type']}")
                
                with col2:
                    st.write(f"**Method:** {req['payment_method']}")
                    st.write(f"**Requested:** {req['requested_at']}")
                    if req.get('selected_months'):
                        st.write(f"**Months:** {', '.join(req['selected_months'])}")
                
                with col3:
                    st.write(f"**Status:** 🟡 PENDING")
                    
    except Exception as e:
        st.error(f"Error loading pending requests: {str(e)}")

# Main parent dashboard function
def show_parent_dashboard(student_id, parent_email):
    """Main parent dashboard with all features"""
    
    try:
        # Show fee summary
        show_fee_summary(student_id)
        
        st.divider()
        
        # Show paid/unpaid status
        show_paid_unpaid_status(student_id)
        
        st.divider()
        
        # Show payment options in tabs
        tab1, tab2, tab3 = st.tabs(["💳 Pay Monthly Fees", "🎓 Pay Other Fees", "📋 Payment History"])
        
        with tab1:
            show_monthly_payment_section(student_id, parent_email)
        
        with tab2:
            show_annual_admission_payment(student_id, parent_email)
        
        with tab3:
            show_payment_history(student_id)
            st.divider()
            show_pending_requests(student_id)
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# Test function
if __name__ == "__main__":
    st.title("Parent Portal - Test")
    show_parent_dashboard("TEST123", "parent@test.com")