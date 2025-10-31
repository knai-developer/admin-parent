# [file name]: jazz_cash.py
# [file content begin]
#type:ignore
import streamlit as st
import requests
import json
import hashlib
import hmac
import uuid
from datetime import datetime

class JazzCashPayment:
    def __init__(self):
        self.config_file = "jazzcash_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load JazzCash configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            # Default configuration - Admin will update these
            self.config = {
                "merchant_id": "YOUR_MERCHANT_ID",
                "password": "YOUR_PASSWORD", 
                "integrity_salt": "YOUR_SALT",
                "return_url": "https://yourschool.com/payment/return",
                "currency": "PKR",
                "language": "EN",
                "version": "1.1"
            }
    
    def generate_secure_hash(self, pp_amount, pp_bill_reference, pp_description):
        """Generate secure hash for JazzCash"""
        data_string = f"{self.config['integrity_salt']}&{pp_amount}&{self.config['bank_code']}&{pp_bill_reference}&{self.config['currency']}&{pp_description}&{self.config['language']}&{self.config['merchant_id']}&{self.config['password']}&{self.config['return_url']}&{self.config['version']}"
        
        return hashlib.sha256(data_string.encode()).hexdigest().upper()
    
    def initiate_payment(self, amount, student_id, student_name, description):
        """Initiate JazzCash payment"""
        try:
            # Generate unique transaction ID
            pp_txn_ref_no = str(uuid.uuid4())[:20]
            pp_amount = str(int(amount * 100))  # Amount in paisas
            pp_bill_reference = student_id
            pp_description = description
            
            # Generate secure hash
            pp_secure_hash = self.generate_secure_hash(pp_amount, pp_bill_reference, pp_description)
            
            payment_data = {
                'pp_Version': self.config['version'],
                'pp_TxnType': 'MPAY',
                'pp_Language': self.config['language'],
                'pp_MerchantID': self.config['merchant_id'],
                'pp_SubMerchantID': '',
                'pp_Password': self.config['password'],
                'pp_BankID': '',
                'pp_ProductID': '',
                'pp_TxnRefNo': pp_txn_ref_no,
                'pp_Amount': pp_amount,
                'pp_TxnCurrency': self.config['currency'],
                'pp_TxnDateTime': datetime.now().strftime('%Y%m%d%H%M%S'),
                'pp_BillReference': pp_bill_reference,
                'pp_Description': pp_description,
                'pp_TxnExpiryDateTime': '',
                'pp_ReturnURL': self.config['return_url'],
                'pp_SecureHash': pp_secure_hash,
                'ppmpf_1': '1',
                'ppmpf_2': '2',
                'ppmpf_3': '3',
                'ppmpf_4': '4',
                'ppmpf_5': '5'
            }
            
            return {
                'success': True,
                'payment_url': 'https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoTransaction',
                'payment_data': payment_data,
                'transaction_id': pp_txn_ref_no
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, transaction_data):
        """Verify JazzCash payment response"""
        try:
            # Verify secure hash
            expected_hash = self.generate_secure_hash(
                transaction_data['pp_Amount'],
                transaction_data['pp_BillReference'],
                transaction_data['pp_Description']
            )
            
            if transaction_data['pp_SecureHash'] == expected_hash:
                return {
                    'success': True,
                    'verified': True,
                    'transaction_id': transaction_data['pp_TxnRefNo'],
                    'amount': float(transaction_data['pp_Amount']) / 100,
                    'status': transaction_data['pp_ResponseCode'] == '000'
                }
            else:
                return {'success': False, 'error': 'Hash verification failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def show_payment_interface(self, student_id, student_name, amount, description):
        """Show JazzCash payment interface"""
        st.subheader("📱 JazzCash Payment")
        
        # Display payment details
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Student:** {student_name}")
            st.write(f"**Student ID:** {student_id}")
            st.write(f"**Amount:** Rs. {amount:,}")
        
        with col2:
            st.write(f"**Description:** {description}")
            st.write(f"**Payment Method:** JazzCash")
            st.write(f"**Date:** {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        
        st.divider()
        
        # Payment instructions
        st.info("""
        **JazzCash Payment Instructions:**
        1. Open JazzCash app on your phone
        2. Go to 'Send Money' section
        3. Enter the JazzCash number provided by school
        4. Send exact amount: **Rs. {:,}**
        5. Use **Student ID: {}** as reference
        6. Keep transaction receipt for verification
        """.format(amount, student_id))
        
        # Manual payment confirmation
        st.subheader("Payment Confirmation")
        transaction_id = st.text_input("JazzCash Transaction ID*", 
                                     placeholder="e.g., TXN123456789")
        
        if st.button("✅ Confirm JazzCash Payment", type="primary"):
            if transaction_id:
                # Save payment record
                from real_payment_system import RealPaymentSystem
                payment_system = RealPaymentSystem()
                
                payment_record = {
                    'student_id': student_id,
                    'student_name': student_name,
                    'amount': amount,
                    'payment_method': 'JazzCash',
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

def jazzcash_payment_page():
    """JazzCash payment page"""
    payment = JazzCashPayment()
    
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
    jazzcash_payment_page()
# [file content end]