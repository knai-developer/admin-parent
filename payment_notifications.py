# [file name]: payment_notifications.py
# [file content begin]
# type:ignore
import streamlit as st
import json
import os
from datetime import datetime
from database import format_currency

def get_pending_parent_payments():
    """Get all pending parent payments for notifications"""
    try:
        parent_payments_file = "parent_payments_history.json"
        if not os.path.exists(parent_payments_file):
            return []
        
        with open(parent_payments_file, 'r') as f:
            payments = json.load(f)
        
        pending_payments = []
        for student_id, student_payments in payments.items():
            for payment in student_payments:
                if payment.get('status') == 'pending_verification':
                    pending_payments.append(payment)
        
        # Sort by date (newest first)
        pending_payments.sort(key=lambda x: x.get('payment_date', ''), reverse=True)
        return pending_payments
    except Exception as e:
        print(f"Error getting pending payments: {e}")
        return []

def verify_parent_payment(payment_data):
    """Verify a parent payment"""
    try:
        parent_payments_file = "parent_payments_history.json"
        
        if not os.path.exists(parent_payments_file):
            return False
            
        with open(parent_payments_file, 'r') as f:
            payments = json.load(f)
        
        # Update payment status
        for student_id, student_payments in payments.items():
            for i, payment in enumerate(student_payments):
                if payment.get('transaction_id') == payment_data.get('transaction_id'):
                    payments[student_id][i]['status'] = 'verified'
                    payments[student_id][i]['verified_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    payments[student_id][i]['verified_by'] = st.session_state.get('current_user', 'Admin')
                    break
        
        with open(parent_payments_file, 'w') as f:
            json.dump(payments, f, indent=4)
        
        return True
    except Exception as e:
        st.error(f"Verification error: {str(e)}")
        return False

def reject_parent_payment(payment_data):
    """Reject a parent payment"""
    try:
        parent_payments_file = "parent_payments_history.json"
        
        if not os.path.exists(parent_payments_file):
            return False
            
        with open(parent_payments_file, 'r') as f:
            payments = json.load(f)
        
        # Update payment status to rejected
        for student_id, student_payments in payments.items():
            for i, payment in enumerate(student_payments):
                if payment.get('transaction_id') == payment_data.get('transaction_id'):
                    payments[student_id][i]['status'] = 'rejected'
                    payments[student_id][i]['rejected_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    payments[student_id][i]['rejected_by'] = st.session_state.get('current_user', 'Admin')
                    payments[student_id][i]['rejection_reason'] = "Manual rejection by admin"
                    break
        
        with open(parent_payments_file, 'w') as f:
            json.dump(payments, f, indent=4)
        
        return True
    except Exception as e:
        st.error(f"Rejection error: {str(e)}")
        return False

def show_parent_payment_notifications():
    """Show parent payment notifications in admin dashboard"""
    try:
        pending_payments = get_pending_parent_payments()
        
        if pending_payments:
            # Notification Badge with Count
            st.warning(f"🔔 **{len(pending_payments)} Pending Parent Payments Need Verification**")
            
            # Quick summary
            total_amount = sum(payment.get('amount', 0) for payment in pending_payments)
            st.write(f"**Total Pending Amount:** {format_currency(total_amount)}")
            
            # Show recent pending payments in expander
            with st.expander("📋 View Pending Payments", expanded=True):
                for i, payment in enumerate(pending_payments[:5]):  # Show only first 5
                    with st.container():
                        st.markdown("---")
                        
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        
                        with col1:
                            st.write(f"**{payment.get('student_name', 'N/A')}**")
                            st.write(f"*Student ID:* {payment.get('student_id', 'N/A')}")
                            st.write(f"*Transaction:* `{payment.get('transaction_id', 'N/A')}`")
                        
                        with col2:
                            st.write(f"**Amount:** {format_currency(payment.get('amount', 0))}")
                            st.write(f"**Method:** {payment.get('payment_method', 'N/A')}")
                        
                        with col3:
                            st.write(f"**Date:** {payment.get('payment_date', 'N/A')}")
                            status = payment.get('status', 'pending')
                            if status == 'pending_verification':
                                st.error("⏳ Pending")
                        
                        with col4:
                            # Action buttons
                            btn_col1, btn_col2 = st.columns(2)
                            
                            with btn_col1:
                                if st.button("✅ Verify", key=f"verify_{payment.get('transaction_id')}", use_container_width=True):
                                    if verify_parent_payment(payment):
                                        st.success(f"✅ Payment verified for {payment.get('student_name')}!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Verification failed")
                            
                            with btn_col2:
                                if st.button("❌ Reject", key=f"reject_{payment.get('transaction_id')}", use_container_width=True):
                                    if reject_parent_payment(payment):
                                        st.warning(f"❌ Payment rejected for {payment.get('student_name')}")
                                        st.rerun()
                                    else:
                                        st.error("❌ Rejection failed")
                        
                        # Show all payments link if more than 5
                        if len(pending_payments) > 5 and i == 4:
                            st.info(f"📄 And {len(pending_payments) - 5} more pending payments...")
                            if st.button("View All Pending Payments", key="view_all_pending"):
                                st.session_state.show_all_pending = True
                                st.rerun()
            
            # If user clicked "View All"
            if st.session_state.get('show_all_pending', False):
                st.subheader("📋 All Pending Parent Payments")
                
                for payment in pending_payments:
                    with st.container():
                        st.markdown("---")
                        
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        
                        with col1:
                            st.write(f"**{payment.get('student_name', 'N/A')}**")
                            st.write(f"*Student ID:* {payment.get('student_id', 'N/A')}")
                            st.write(f"*Transaction:* `{payment.get('transaction_id', 'N/A')}`")
                        
                        with col2:
                            st.write(f"**Amount:** {format_currency(payment.get('amount', 0))}")
                            st.write(f"**Method:** {payment.get('payment_method', 'N/A')}")
                        
                        with col3:
                            st.write(f"**Date:** {payment.get('payment_date', 'N/A')}")
                            st.error("⏳ Pending Verification")
                        
                        with col4:
                            btn_col1, btn_col2 = st.columns(2)
                            
                            with btn_col1:
                                if st.button("✅ Verify", key=f"verify_all_{payment.get('transaction_id')}", use_container_width=True):
                                    if verify_parent_payment(payment):
                                        st.success(f"✅ Verified {payment.get('student_name')}!")
                                        st.rerun()
                            
                            with btn_col2:
                                if st.button("❌ Reject", key=f"reject_all_{payment.get('transaction_id')}", use_container_width=True):
                                    if reject_parent_payment(payment):
                                        st.warning(f"❌ Rejected {payment.get('student_name')}")
                                        st.rerun()
                
                if st.button("⬅️ Back to Summary", key="back_to_summary"):
                    st.session_state.show_all_pending = False
                    st.rerun()
        
        else:
            st.success("🎉 No pending parent payments!")
            
    except Exception as e:
        st.error(f"Error loading payment notifications: {str(e)}")

def get_payment_stats():
    """Get payment statistics for dashboard"""
    try:
        parent_payments_file = "parent_payments_history.json"
        if not os.path.exists(parent_payments_file):
            return {
                'total_pending': 0,
                'total_verified': 0,
                'total_rejected': 0,
                'pending_amount': 0,
                'verified_amount': 0
            }
        
        with open(parent_payments_file, 'r') as f:
            payments = json.load(f)
        
        stats = {
            'total_pending': 0,
            'total_verified': 0,
            'total_rejected': 0,
            'pending_amount': 0,
            'verified_amount': 0
        }
        
        for student_id, student_payments in payments.items():
            for payment in student_payments:
                status = payment.get('status', 'pending')
                amount = payment.get('amount', 0)
                
                if status == 'pending_verification':
                    stats['total_pending'] += 1
                    stats['pending_amount'] += amount
                elif status == 'verified':
                    stats['total_verified'] += 1
                    stats['verified_amount'] += amount
                elif status == 'rejected':
                    stats['total_rejected'] += 1
        
        return stats
        
    except Exception as e:
        print(f"Error getting payment stats: {e}")
        return {
            'total_pending': 0,
            'total_verified': 0,
            'total_rejected': 0,
            'pending_amount': 0,
            'verified_amount': 0
        }

# [file content end]