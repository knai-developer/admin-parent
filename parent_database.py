import json
import os
import csv
from datetime import datetime
from pathlib import Path

# Shared database paths (same as admin app)
STUDENT_DETAILS_PATH = "data/student_details.json"
STUDENT_FEES_PATH = "data/student_fees.json"
FEES_DATA_PATH = "fees_data.csv"  # Changed path
PAYMENT_HISTORY_PATH = "data/parent_payments.json"

def ensure_databases_exist():
    """Ensure all required databases exist"""
    Path("data").mkdir(exist_ok=True)
    
    if not os.path.exists(PAYMENT_HISTORY_PATH):
        with open(PAYMENT_HISTORY_PATH, 'w') as f:
            json.dump({}, f)

def get_student_details(student_id):
    """Get student details from admin database"""
    if not os.path.exists(STUDENT_DETAILS_PATH):
        return None
    
    with open(STUDENT_DETAILS_PATH, 'r') as f:
        students = json.load(f)
    
    return students.get(student_id, None)

def get_student_fees(student_id):
    """Get student fee details"""
    if not os.path.exists(STUDENT_FEES_PATH):
        return None
    
    with open(STUDENT_FEES_PATH, 'r') as f:
        fees = json.load(f)
    
    return fees.get(student_id, None)

def get_student_fee_summary(student_id):
    """Get comprehensive fee summary for student"""
    ensure_databases_exist()
    
    student = get_student_details(student_id)
    fees = get_student_fees(student_id)
    
    if not student or not fees:
        return None
    
    # Calculate totals
    monthly_fee = fees.get("monthly_fee", 0)
    admission_fee = fees.get("admission_fee", 0)
    annual_fee = fees.get("annual_fee", 0)
    
    # Get received amount from fees_data.csv
    received = 0
    if os.path.exists(FEES_DATA_PATH):
        with open(FEES_DATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ID') == student_id:  # Changed from 'Student ID' to 'ID'
                    try:
                        received += float(row.get('Received Amount', 0))
                    except:
                        pass
    
    total_due = (monthly_fee * 12) + admission_fee + annual_fee
    balance = total_due - received
    
    return {
        "student_id": student_id,
        "student_name": student.get("name", "N/A"),
        "class": student.get("class", "N/A"),
        "monthly_fee": monthly_fee,
        "admission_fee": admission_fee,
        "annual_fee": annual_fee,
        "total_yearly_due": total_due,
        "total_received": received,
        "balance_due": max(0, balance),
        "percentage_paid": round((received / total_due * 100) if total_due > 0 else 0, 2)
    }

def get_paid_months(student_id):
    """Get list of paid months with details"""
    paid_months = []
    
    if os.path.exists(FEES_DATA_PATH):
        with open(FEES_DATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ID') == student_id and float(row.get('Monthly Fee', 0)) > 0:
                    paid_months.append({
                        'month': row.get('Month', ''),
                        'amount': float(row.get('Monthly Fee', 0)),
                        'date': row.get('Date', ''),
                        'method': row.get('Payment Method', '')
                    })
    
    return paid_months

def get_unpaid_months(student_id):
    """Get list of unpaid months"""
    all_months = [
        "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
        "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
    ]
    
    paid_months_data = get_paid_months(student_id)
    paid_months = [pm['month'] for pm in paid_months_data]
    
    unpaid_months = [month for month in all_months if month not in paid_months]
    return unpaid_months

def get_payment_history(student_id):
    """Get payment history for student"""
    ensure_databases_exist()
    
    history = []
    
    if os.path.exists(FEES_DATA_PATH):
        with open(FEES_DATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ID') == student_id:
                    try:
                        amount = float(row.get('Received Amount', 0))
                        if amount > 0:  # Only show actual payments
                            history.append({
                                "date": row.get('Date', 'N/A'),
                                "amount": amount,
                                "payment_method": row.get('Payment Method', 'Cash'),
                                "reference": row.get('Reference No', 'N/A'),
                                "remarks": row.get('Remarks', '')
                            })
                    except:
                        continue
    
    return sorted(history, key=lambda x: x['date'], reverse=True)

def record_payment_request(student_id, parent_email, amount, payment_type, payment_method, selected_months=None):
    """Record a payment request from parent"""
    ensure_databases_exist()
    
    try:
        with open(PAYMENT_HISTORY_PATH, 'r') as f:
            payments = json.load(f)
    except:
        payments = {}
    
    request_id = f"PR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if student_id not in payments:
        payments[student_id] = []
    
    payment_data = {
        "request_id": request_id,
        "parent_email": parent_email,
        "amount": amount,
        "payment_type": payment_type,
        "payment_method": payment_method,
        "status": "pending",
        "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "selected_months": selected_months if selected_months else []
    }
    
    payments[student_id].append(payment_data)
    
    with open(PAYMENT_HISTORY_PATH, 'w') as f:
        json.dump(payments, f, indent=2)
    
    return request_id

def get_payment_requests(student_id):
    """Get all payment requests for a student"""
    ensure_databases_exist()
    
    try:
        with open(PAYMENT_HISTORY_PATH, 'r') as f:
            payments = json.load(f)
    except:
        payments = {}
    
    return payments.get(student_id, [])

def export_payment_history_csv(student_id):
    """Export payment history as CSV"""
    history = get_payment_history(student_id)
    
    csv_data = "Date,Amount,Payment Method,Reference,Remarks\n"
    for payment in history:
        csv_data += f"{payment['date']},{payment['amount']},{payment['payment_method']},{payment['reference']},{payment['remarks']}\n"
    
    return csv_data