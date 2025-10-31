# fee change line no 144,159
#type:ignore
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from hashlib import md5
import streamlit as st

def initialize_files():
    """Initialize all required files"""
    initialize_csv()
    initialize_user_db()
    initialize_student_fees()
    initialize_default_fees()
    initialize_school_config()
    initialize_student_details()

def initialize_user_db():
    """Initialize the user database if it doesn't exist"""
    if not os.path.exists("users.json"):
        with open("users.json", 'w') as f:
            json.dump({}, f)

def initialize_student_fees():
    """Initialize the student fees JSON file if it doesn't exist"""
    if not os.path.exists("student_fees.json"):
        with open("student_fees.json", 'w') as f:
            json.dump({}, f)

def initialize_default_fees():
    """Initialize the default fees JSON file if it doesn't exist"""
    if not os.path.exists("default_fees.json"):
        with open("default_fees.json", 'w') as f:
            json.dump({
                "monthly_fee": 3000,
                "annual_charges": 3500,
                "admission_fee": 10000,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f)

def initialize_school_config():
    """Initialize the school configuration file if it doesn't exist"""
    if not os.path.exists("school_config.json"):
        with open("school_config.json", 'w') as f:
            json.dump({
                "school_name": "Your School Name",
                "school_logo": None,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f)

def initialize_csv():
    """Initialize the CSV file with proper columns if it doesn't exist"""
    if not os.path.exists("fees_data.csv"):
        columns = [
            "ID", "Student Name", "Father Name", "Student Phone", "Class Category", "Class Section", 
            "Address", "Age", "Month", 
            "Monthly Fee", "Annual Charges", "Admission Fee", 
            "Received Amount", "Payment Method", "Date", "Signature", 
            "Entry Timestamp", "Academic Year"
        ]
        pd.DataFrame(columns=columns).to_csv("fees_data.csv", index=False)

def initialize_student_details():
    """Initialize the student details JSON file if it doesn't exist"""
    if not os.path.exists("student_details.json"):
        with open("student_details.json", 'w') as f:
            json.dump({}, f)

def generate_student_id(student_name, class_category):
    """Generate a unique 8-character ID based on student name and class"""
    unique_str = f"{student_name}_{class_category}".encode('utf-8')
    return md5(unique_str).hexdigest()[:8].upper()

def save_to_csv(data):
    """Save data to CSV with proper validation"""
    try:
        if os.path.exists("fees_data.csv"):
            df = pd.read_csv("fees_data.csv")
        else:
            df = pd.DataFrame(columns=data[0].keys())
        
        new_df = pd.DataFrame(data)
        df = pd.concat([df, new_df], ignore_index=True)
        
        df.to_csv("fees_data.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def load_data():
    """Load data from CSV with robust error handling"""
    if not os.path.exists("fees_data.csv"):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv("fees_data.csv")
        
        expected_columns = [
            "ID", "Student Name", "Class Category", "Class Section", "Month", 
            "Monthly Fee", "Annual Charges", "Admission Fee", 
            "Received Amount", "Payment Method", "Date", "Signature", 
            "Entry Timestamp", "Academic Year"
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = np.nan
        
        try:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')
        except:
            pass
        
        try:
            df['Entry Timestamp'] = pd.to_datetime(df['Entry Timestamp']).dt.strftime('%d-%m-%Y %H:%M')
        except:
            pass
        
        return df.dropna(how='all')
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def update_data(updated_df):
    """Update the CSV file with the modified DataFrame"""
    try:
        updated_df.to_csv("fees_data.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")
        return False

def load_student_fees():
    """Load student-specific fees from JSON file"""
    try:
        if os.path.exists("student_fees.json"):
            with open("student_fees.json", 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading student fees: {str(e)}")
        return {}

def save_student_fees(fees_data):
    """Save student-specific fees to JSON file"""
    try:
        with open("student_fees.json", 'w') as f:
            json.dump(fees_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving student fees: {str(e)}")
        return False

def load_default_fees():
    """Load default fees from JSON file"""
    try:
        if os.path.exists("default_fees.json"):
            with open("default_fees.json", 'r') as f:
                return json.load(f)
        return {
            "monthly_fee": 3000,
            "annual_charges": 3500,
            "admission_fee": 10000
        }
    except Exception as e:
        st.error(f"Error loading default fees: {str(e)}")
        return {
            "monthly_fee": 3000,
            "annual_charges": 3500,
            "admission_fee": 10000
        }

def save_default_fees(fees_data):
    """Save default fees to JSON file"""
    try:
        fees_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("default_fees.json", 'w') as f:
            json.dump(fees_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving default fees: {str(e)}")
        return False

def get_student_fee_amount(student_id, fee_type):
    """Get specific fee amount for a student - dynamic fees system"""
    fees_data = load_student_fees()
    
    if student_id in fees_data:
        fee_mapping = {
            "monthly": "monthly_fee",
            "annual": "annual_charges", 
            "admission": "admission_fee"
        }
        
        if fee_type in fee_mapping:
            fee_key = fee_mapping[fee_type]
            return fees_data[student_id].get(fee_key, 0)
    
    default_fees_data = load_default_fees()
    fee_mapping = {
        "monthly": "monthly_fee",
        "annual": "annual_charges", 
        "admission": "admission_fee"
    }
    
    if fee_type in fee_mapping:
        fee_key = fee_mapping[fee_type]
        return default_fees_data.get(fee_key, 0)
    
    return 0

def get_student_fee_details(student_id):
    """Get all fee details for a student"""
    fees_data = load_student_fees()
    
    if student_id in fees_data:
        return fees_data[student_id]
    
    default_fees_data = load_default_fees()
    return {
        "monthly_fee": default_fees_data.get("monthly_fee", 3000),
        "annual_charges": default_fees_data.get("annual_charges", 3500),
        "admission_fee": default_fees_data.get("admission_fee", 10000),
        "student_name": "Not Set",
        "class_category": "Not Set"
    }

def check_fee_setting_exists(student_name, class_category):
    """Check if fee setting already exists for a student"""
    student_id = generate_student_id(student_name, class_category)
    fees_data = load_student_fees()
    return student_id in fees_data

def get_all_students_with_fees():
    """Get all students who have custom fee settings"""
    fees_data = load_student_fees()
    return fees_data

def load_school_config():
    """Load school configuration from JSON file"""
    try:
        if os.path.exists("school_config.json"):
            with open("school_config.json", 'r') as f:
                return json.load(f)
        return {
            "school_name": "Your School Name",
            "school_logo": None
        }
    except Exception as e:
        st.error(f"Error loading school config: {str(e)}")
        return {
            "school_name": "Your School Name",
            "school_logo": None
        }

def save_school_config(config_data):
    """Save school configuration to JSON file"""
    try:
        config_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("school_config.json", 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving school config: {str(e)}")
        return False

def save_student_details(student_details_data):
    """Save student details to JSON file"""
    try:
        with open("student_details.json", 'w') as f:
            json.dump(student_details_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving student details: {str(e)}")
        return False

def load_student_details():
    """Load student details from JSON file"""
    try:
        if os.path.exists("student_details.json"):
            with open("student_details.json", 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading student details: {str(e)}")
        return {}

def get_student_detail(student_id):
    """Get specific student details"""
    details = load_student_details()
    return details.get(student_id, {})

def add_student_detail(student_id, student_name, father_name, class_category, address, phone, age):
    """Add or update student details"""
    details = load_student_details()
    details[student_id] = {
        "student_name": student_name,
        "father_name": father_name,
        "class_category": class_category,
        "address": address,
        "phone": phone,
        "age": age,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return save_student_details(details)
