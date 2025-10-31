
# type:ignore
import streamlit as st
import json
import os
from datetime import datetime

class RealPaymentSystem:
    def __init__(self):
        self.payments_file = "parent_payments.json"
        self._initialize_payments_file()
    
    def _initialize_payments_file(self):
        """Initialize payments file if it doesn't exist"""
        if not os.path.exists(self.payments_file):
            with open(self.payments_file, 'w') as f:
                json.dump({}, f)
    
    def handle_parent_payment(self, student_id, student_name, amount, payment_method, transaction_id):
        """Handle payment from parent and record in admin system"""
        try:
            from database import save_to_csv, load_student_details
            
            # Load student details
            student_details = load_student_details()
            student_info = student_details.get(student_id, {})
            
            # Create payment record
            payment_record = {
                "ID": student_id,
                "Student Name": student_name,
                "Father Name": student_info.get('father_name', ''),
                "Student Phone": student_info.get('phone', ''),
                "Class Category": student_info.get('class_category', ''),
                "Class Section": student_info.get('class_section', ''),
                "Address": student_info.get('address', ''),
                "Age": student_info.get('age', ''),
                "Month": "PARENT_PAYMENT",
                "Monthly Fee": amount,
                "Annual Charges": 0,
                "Admission Fee": 0,
                "Received Amount": amount,
                "Payment Method": payment_method,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Signature": "Parent Portal",
                "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Academic Year": "2024-2025",
                "Transaction ID": transaction_id,
                "Payment Source": "Parent Portal"
            }
            
            # Save to main database
            if save_to_csv([payment_record]):
                # Also save to parent payments file for tracking
                self._save_parent_payment_record(student_id, student_name, amount, payment_method, transaction_id)
                return True
            return False
            
        except Exception as e:
            st.error(f"Payment recording error: {str(e)}")
            return False

    def _save_parent_payment_record(self, student_id, student_name, amount, payment_method, transaction_id):
        """Save parent payment record to separate file"""
        try:
            parent_payments_file = "parent_payments_history.json"
            
            if os.path.exists(parent_payments_file):
                with open(parent_payments_file, 'r') as f:
                    payments = json.load(f)
            else:
                payments = {}
            
            if student_id not in payments:
                payments[student_id] = []
            
            payment_data = {
                "student_id": student_id,
                "student_name": student_name,
                "amount": amount,
                "payment_method": payment_method,
                "transaction_id": transaction_id,
                "payment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "pending_verification"
            }
            
            payments[student_id].append(payment_data)
            
            with open(parent_payments_file, 'w') as f:
                json.dump(payments, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving parent payment: {str(e)}")
            return False

def real_payment_page():
    """Real payment system page"""
    payment_system = RealPaymentSystem()
    
    st.header("💳 Real Payment System")
    st.info("This is the payment system for processing parent payments.")

if __name__ == "__main__":
    real_payment_page()
# [file content end]