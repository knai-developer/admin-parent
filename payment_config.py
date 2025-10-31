# [file name]: payment_config.py
# [file content begin]
#type:ignore
# (Admin Banking Configuration)
import streamlit as st
import json
import os
from datetime import datetime

class PaymentConfig:
    def __init__(self):
        self.config_file = "payment_config.json"
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize payment configuration file"""
        default_config = {
            "bank_details": {
                "bank_name": "",
                "account_title": "", 
                "account_number": "",
                "iban": "",
                "branch": "",
                "branch_code": ""
            },
            "jazzcash": {
                "account_number": "",
                "account_name": "",
                "payment_link": ""
            },
            "easypaisa": {
                "account_number": "", 
                "account_name": "",
                "payment_link": ""
            },
            "stripe": {
                "publishable_key": "",
                "secret_key": "",
                "webhook_secret": ""
            },
            "payment_instructions": {
                "bank_transfer_instructions": "",
                "jazzcash_instructions": "",
                "easypaisa_instructions": ""
            },
            "updated_at": ""
        }
        
        if not os.path.exists(self.config_file):
            self.save_config(default_config)
    
    def load_config(self):
        """Load payment configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return self._initialize_config()
    
    def save_config(self, config_data):
        """Save payment configuration"""
        config_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    
    def show_config_page(self):
        """Show payment configuration page for admin"""
        st.header("🏦 Payment Gateway Configuration")
        
        config = self.load_config()
        
        # Bank Details
        st.subheader("1. 🏦 Bank Account Details")
        col1, col2 = st.columns(2)
        
        with col1:
            config['bank_details']['bank_name'] = st.text_input(
                "Bank Name", 
                value=config['bank_details']['bank_name'],
                placeholder="e.g., HBL, UBL, MCB"
            )
            config['bank_details']['account_title'] = st.text_input(
                "Account Title",
                value=config['bank_details']['account_title'],
                placeholder="School Official Name"
            )
            config['bank_details']['account_number'] = st.text_input(
                "Account Number", 
                value=config['bank_details']['account_number'],
                placeholder="0123456789012"
            )
        
        with col2:
            config['bank_details']['iban'] = st.text_input(
                "IBAN Number",
                value=config['bank_details']['iban'], 
                placeholder="PK00HABB0000123456789012"
            )
            config['bank_details']['branch'] = st.text_input(
                "Branch Name",
                value=config['bank_details']['branch'],
                placeholder="Main Branch, Karachi"
            )
            config['bank_details']['branch_code'] = st.text_input(
                "Branch Code",
                value=config['bank_details']['branch_code'],
                placeholder="1234"
            )
        
        # JazzCash Configuration
        st.subheader("2. 📱 JazzCash Settings")
        col_j1, col_j2 = st.columns(2)
        
        with col_j1:
            config['jazzcash']['account_number'] = st.text_input(
                "JazzCash Number",
                value=config['jazzcash']['account_number'],
                placeholder="0300-1234567"
            )
            config['jazzcash']['account_name'] = st.text_input(
                "JazzCash Account Name", 
                value=config['jazzcash']['account_name'],
                placeholder="School Name"
            )
        
        with col_j2:
            config['jazzcash']['payment_link'] = st.text_input(
                "JazzCash Payment Link (Optional)",
                value=config['jazzcash']['payment_link'],
                placeholder="https://jazzcash.com.pk/your-school"
            )
        
        # EasyPaisa Configuration  
        st.subheader("3. 📲 EasyPaisa Settings")
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            config['easypaisa']['account_number'] = st.text_input(
                "EasyPaisa Number",
                value=config['easypaisa']['account_number'], 
                placeholder="0312-7654321"
            )
            config['easypaisa']['account_name'] = st.text_input(
                "EasyPaisa Account Name",
                value=config['easypaisa']['account_name'],
                placeholder="School Name"
            )
        
        with col_e2:
            config['easypaisa']['payment_link'] = st.text_input(
                "EasyPaisa Payment Link (Optional)",
                value=config['easypaisa']['payment_link'],
                placeholder="https://easypaisa.com.pk/your-school"
            )
        
        # Payment Instructions
        st.subheader("4. 📝 Payment Instructions")
        config['payment_instructions']['bank_transfer_instructions'] = st.text_area(
            "Bank Transfer Instructions",
            value=config['payment_instructions']['bank_transfer_instructions'] or """
1. Login to your bank app/website
2. Add beneficiary with above details  
3. Transfer exact amount
4. Use Student ID as reference
5. Keep transaction receipt""",
            height=100
        )
        
        config['payment_instructions']['jazzcash_instructions'] = st.text_area(
            "JazzCash Instructions", 
            value=config['payment_instructions']['jazzcash_instructions'] or """
1. Open JazzCash app
2. Go to 'Send Money'
3. Enter account number above
4. Send exact amount
5. Use Student ID as reference""",
            height=100
        )
        
        config['payment_instructions']['easypaisa_instructions'] = st.text_area(
            "EasyPaisa Instructions",
            value=config['payment_instructions']['easypaisa_instructions'] or """
1. Open EasyPaisa app  
2. Tap 'Send to Account'
3. Enter account number above
4. Send exact amount
5. Use Student ID as reference""",
            height=100
        )
        
        # Save Configuration
        if st.button("💾 Save Payment Configuration", type="primary"):
            if self.save_config(config):
                st.success("✅ Payment configuration saved successfully!")
                st.rerun()

def payment_config_page():
    """Payment configuration page"""
    config_manager = PaymentConfig()
    config_manager.show_config_page()
# [file content end]