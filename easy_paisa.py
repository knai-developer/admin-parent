# [file name]: easy_paisa.py
# [file content begin]
#type:ignore
import streamlit as st
import requests
import json
import uuid
from datetime import datetime

class EasyPaisaPayment:
    def __init__(self):
        self.config_file = "easypaisa_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load EasyPaisa configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            # Default configuration - Admin will update these
            self.config = {
                "store_id": "YOUR_STORE_ID",
                "account_num": "YOUR_ACCOUNT_NUMBER",
                "hash_key": "YOUR_HASH_KEY",
                "return_url": "https://yourschool.com/payment/return",
                "currency": "PKR"
            }
    
    def initiate_payment(self, amount, student_id, student_name, description):
        """Initiate EasyPaisa payment"""
        try:
            # Generate unique transaction ID
            transaction_id = str(uuid.uuid4())[:20]
            
            payment_data = {
                'storeId': self.config['store_id'],
                'accountNum': self.config['account_num'],
                'transactionAmount': amount,
                'transactionType': 'InitialRequest',
                'orderId': transaction_id,
                'merchantEmail': 'school@example.com',
                'merchantName': 'School Fees Management',
                'transactionDateTime': datetime.now().strftime('%Y%m%d%H%M%S'),
                'productDetails': description,
                'bankIdentificationNumber': student_id,
                'signature': self._generate_signature(transaction_id, amount)
            }
            
            return {
                'success': True,
                'payment_url': 'https://easypay.easypaisa.com.pk/easypay/Index.jsf',
                'payment_data': payment_data,
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_signature(self, order_id, amount):
        """Generate signature for EasyPaisa"""
        import hashlib
        data_string = f"{self.config['store_id']}{order_id}{amount}{self.config['hash_key']}"
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def verify_payment(self, response_data):
        """Verify EasyPaisa payment response"""
        try:
            # Verify signature
            expected_signature = self._generate_signature(
                response_data['orderId'],
                response_data['transactionAmount']
            )
            
            if response_data['signature'] == expected_signature:
                return {
                    'success': True,
                    'verified': True,
                    'transaction_id': response_data['orderId'],
                    'amount': float(response_data['transactionAmount']),
                    'status': response_data['responseCode'] == '000'
                }
            else:
                return {'success': False, 'error': 'Signature verification failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def show_payment_interface(self, student_id, student_name, amount, description):
        """Show EasyPaisa payment interface"""
        st.subheader("📲 EasyPaisa Payment")
        
        # Display payment details
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Student:** {student_name}")
            st.write(f"**Student ID:** {student_id}")
            st.write(f"**Amount:** Rs. {amount:,}")
        
        with col2:
            st.write(f"**Description:** {description}")
            st.write(f"**Payment Method:** EasyPaisa")
            st.write(f"**Date:** {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        
        st.divider()
        
        # Payment instructions
        st.info("""
        **EasyPaisa Payment Instructions:**
        1. Open EasyPaisa app on your phone
        2. Go to 'Send to Account' section
        3. Enter the EasyPaisa number provided by school
        4. Send exact amount: **Rs. {:,}**
        5. Use **Student ID: {}** as reference
        6. Keep transaction receipt for verification
        """.format(amount, student_id))
        
        # Manual payment confirmation
        st.subheader("Payment Confirmation")
        transaction_id = st.text_input("EasyPaisa Transaction ID*", 
                                     placeholder="e.g., EPTXN123456789")
        
        if st.button("✅ Confirm EasyPaisa Payment", type="primary"):
            if transaction_id:
                # Save payment record
                from real_payment_system import RealPaymentSystem
                payment_system = RealPaymentSystem()
                
                payment_record = {
                    'student_id': student_id,
                    'student_name': student_name,
                    'amount': amount,
                    'payment_method': 'EasyPaisa',
                    'transaction_id': transaction_id,
                    'status': 'pending_verification'
                }
                
                if payment_system._save_payment_record(payment_record):
                    st.success("🎉 Payment submitted for verification!")
                    st.info("Payment will be verified by admin within 24 hours")
                else:
                    st.error("Failed to save payment record")
            else:
                st.error("Please enter transaction ID")

def easypaisa_payment_page():
    """EasyPaisa payment page"""
    payment = EasyPaisaPayment()
    
    # Get student and fee details from session
    if 'current_student' in st.session_state:
        student = st.session_state.current_student
        fee_details = st.session_state.current_fee_details
        
        payment.show_payment_interface(
            student['id'],
            student['name'],
            fee_details['total_amount'],
            f"School Fees - {student['class']}"
        )
    else:
        st.warning("Please select a student first")

if __name__ == "__main__":
    easypaisa_payment_page()
# [file content end]