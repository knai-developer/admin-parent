# type:ignore
import os
import streamlit as st
from datetime import datetime
import pandas as pd
from database import generate_student_id, save_to_csv, load_data, load_student_fees, get_student_fee_amount, load_school_config, get_student_detail
from utils import format_currency, get_academic_year, check_annual_admission_paid, get_unpaid_months
from slip_generator import generate_fee_slip, share_slip_via_whatsapp, display_menu_bar


def fees_entry_page():
    """Fees entry page"""
    from slip_generator import display_menu_bar
    display_menu_bar()
    
    st.header("➕ Enter Fee Details")
     
    CLASS_CATEGORIES = [
        "Nursery", "KGI", "KGII", 
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5",
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10 (Matric)"
    ]
    
    PAYMENT_METHODS = ["Cash", "Bank Transfer", "Cheque", "Online Payment", "Other"]
    
    # Initialize session state variables if they don't exist
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'available_months' not in st.session_state:
        st.session_state.available_months = []
    if 'current_student_id' not in st.session_state:
        st.session_state.current_student_id = None
    if 'last_saved_records' not in st.session_state:
        st.session_state.last_saved_records = None
    if 'last_student_name' not in st.session_state:
        st.session_state.last_student_name = ""
    if 'last_father_name' not in st.session_state:
        st.session_state.last_father_name = ""
    if 'last_class_category' not in st.session_state:
        st.session_state.last_class_category = None
    if 'last_class_section' not in st.session_state:
        st.session_state.last_class_section = ""
    if 'current_fee_type' not in st.session_state:
        st.session_state.current_fee_type = "Monthly Fee"
    if 'current_total_amount' not in st.session_state:
        st.session_state.current_total_amount = 0
    if 'previous_fee_type' not in st.session_state:
        st.session_state.previous_fee_type = "Monthly Fee"
    if 'previous_month_selection' not in st.session_state:
        st.session_state.previous_month_selection = "Select a month"
    if 'last_generated_slip' not in st.session_state:
        st.session_state.last_generated_slip = None
    if 'show_share_options' not in st.session_state:
        st.session_state.show_share_options = False
    if 'fee_breakdown' not in st.session_state:
        st.session_state.fee_breakdown = {
            "monthly_fee": 0,
            "annual_charges": 0,
            "admission_fee": 0,
            "selected_months": [],
            "payment_method": "",
            "payment_date": ""
        }
    
    # Show WhatsApp share options if slip was generated
    if st.session_state.show_share_options and st.session_state.last_generated_slip:
        show_whatsapp_share_options()
        return
    
    # Create the form
    with st.form(key=f"fee_form_{st.session_state.form_key}", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            student_name = st.text_input(
                "Student Name*", 
                placeholder="Full name", 
                value=st.session_state.last_student_name,
                key=f"student_name_{st.session_state.form_key}"
            )
        with col2:
            father_name = st.text_input(
                "Father Name*",
                placeholder="Father's full name",
                value=st.session_state.last_father_name,
                key=f"father_name_{st.session_state.form_key}"
            )
        with col3:
            class_category = st.selectbox(
                "Class Category*", 
                CLASS_CATEGORIES, 
                index=CLASS_CATEGORIES.index(st.session_state.last_class_category) if st.session_state.last_class_category in CLASS_CATEGORIES else 0,
                key=f"class_category_{st.session_state.form_key}"
            )
        
        class_section = st.text_input(
            "Class Section", 
            placeholder="A, B, etc. (if applicable)", 
            value=st.session_state.last_class_section,
            key=f"class_section_{st.session_state.form_key}"
        )
        
        # Add a button to update student data
        update_btn = st.form_submit_button("🔍 Check Student Records")
        
        if update_btn:
            update_student_data(student_name, class_category)
            st.rerun()
        
        student_id = st.session_state.current_student_id
        
        # Show student records if student_id is available
        if student_id:
            display_student_records(student_id)
        
        payment_date = st.date_input("Payment Date", value=datetime.now(), 
                                   key=f"payment_date_{st.session_state.form_key}")
        academic_year = get_academic_year(payment_date)
        
        # Multiple fee selection
        st.subheader("💰 Select Fee Types to Pay")
        
        col_fee1, col_fee2, col_fee3 = st.columns(3)
        with col_fee1:
            pay_monthly = st.checkbox("Monthly Fee", value=True, key=f"pay_monthly_{st.session_state.form_key}")
        with col_fee2:
            pay_annual = st.checkbox("Annual Charges", key=f"pay_annual_{st.session_state.form_key}")
        with col_fee3:
            pay_admission = st.checkbox("Admission Fee", key=f"pay_admission_{st.session_state.form_key}")
        
        # Initialize fee variables
        monthly_fee = 0
        annual_charges = 0
        admission_fee = 0
        selected_months = []
        
        # Load student fees data
        fees_data = load_student_fees()
        
        # Handle selected fee types
        if pay_monthly:
            monthly_fee, selected_months = handle_monthly_fee(
                student_id, fees_data, academic_year
            )
        
        if pay_annual:
            annual_result = handle_annual_charges(student_id, academic_year, fees_data)
            if annual_result:
                annual_charges, _ = annual_result
            else:
                pay_annual = False
        
        if pay_admission:
            admission_result = handle_admission_fee(student_id, academic_year, fees_data)
            if admission_result:
                admission_fee, _ = admission_result
            else:
                pay_admission = False
        
        # Calculate total amount dynamically
        total_amount = calculate_total_amount(pay_monthly, pay_annual, pay_admission, 
                                            monthly_fee, annual_charges, admission_fee, selected_months)
        
        # Update session state with current total amount
        st.session_state.current_total_amount = total_amount
        
        col3, col4 = st.columns(2)
        with col3:
            st.text_input(
                "Total Amount",
                value=format_currency(total_amount),
                disabled=True,
                key=f"total_amount_{st.session_state.form_key}"
            )
            
            payment_method = st.selectbox(
                "Payment Method*",
                PAYMENT_METHODS,
                key=f"payment_method_{st.session_state.form_key}"
            )
        with col4:
            # Show received amount as display only (user cannot change)
            st.text_input(
                "Received Amount*",
                value=format_currency(total_amount),
                disabled=True,
                key=f"received_amount_display_{st.session_state.form_key}"
            )
            
            # Hidden field for actual received amount (will use total_amount)
            received_amount = total_amount
            
            signature = st.text_input(
                "Received By (Signature)*",
                placeholder="Your name",
                key=f"signature_{st.session_state.form_key}"
            )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Save Fee Record")
        with col_btn2:
            refresh = st.form_submit_button("🔄 Refresh Form")
        
        if refresh:
            refresh_form()
            st.rerun()
        
        if submitted:
            # Check payment status before submission
            annual_paid, admission_paid = check_annual_admission_paid(student_id, academic_year)
            
            success = handle_form_submission(
                student_name, father_name, class_category, class_section, student_id,
                signature, pay_monthly, pay_annual, pay_admission,
                selected_months, monthly_fee, annual_charges, admission_fee, 
                received_amount, payment_method, payment_date, academic_year,
                annual_paid, admission_paid
            )

def show_whatsapp_share_options():
    """Show WhatsApp share options for the generated slip (outside form)"""
    st.markdown("---")
    st.subheader("📤 Share Fee Slip via WhatsApp")
    
    student_name = st.session_state.last_student_name
    class_category = st.session_state.last_class_category
    
    st.markdown("### WhatsApp Share Options")
    
    col_image, col_message = st.columns([1, 1])
    
    with col_image:
        st.markdown("#### 📄 Fee Slip Image")
        if st.session_state.last_generated_slip:
            from PIL import Image
            slip_image = Image.open(st.session_state.last_generated_slip)
            st.image(slip_image, use_container_width=True)
            
            # Download button for slip image
            with open(st.session_state.last_generated_slip, "rb") as file:
                st.download_button(
                    label="⬇️ Download Slip Image",
                    data=file,
                    file_name=f"fee_slip_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            # Share button with instructions
            if st.button("📤 Share", use_container_width=True, key="share_slip_button"):
                st.info("""
                **📝 WhatsApp Sharing Instructions:**

                1. Download the slip image using the button above
                2. Open WhatsApp → Select contact/group
                3. Send the slip image along with the fee details message below
                """)
    
    with col_message:
        st.markdown("#### Method 1: Copy Message with Fee Details")
        
        fee_breakdown = st.session_state.fee_breakdown
        
        total_amount = 0
        if fee_breakdown.get("monthly_fee", 0) > 0 and fee_breakdown.get("selected_months"):
            total_amount += fee_breakdown["monthly_fee"] * len(fee_breakdown["selected_months"])
        if fee_breakdown.get("annual_charges", 0) > 0:
            total_amount += fee_breakdown["annual_charges"]
        if fee_breakdown.get("admission_fee", 0) > 0:
            total_amount += fee_breakdown["admission_fee"]
        
        # Generate detailed fee message with breakdown
        fee_message = generate_fee_details_message(
            student_name, 
            class_category, 
            total_amount, 
            fee_breakdown
        )
        
        st.text_area(
            "📋 Select and Copy this message to WhatsApp:", 
            value=fee_message, 
            height=250, 
            key="share_message", 
            disabled=True
        )
        
        st.info("""
        **How to copy:**
        1. Click in the text box above
        2. Press Ctrl+A (or Cmd+A on Mac) to select all
        3. Press Ctrl+C (or Cmd+C on Mac) to copy
        4. Open WhatsApp and paste the message
        """)
    
    # Additional instructions
    st.markdown("---")
    st.markdown("""
    **📝 WhatsApp Sharing Instructions:**

    1. Download the slip image
    2. Copy the fee details message
    3. Open WhatsApp → Select contact/group
    4. Send the slip image and paste the message
    """)
    
    # Back to form button
    if st.button("⬅️ Back to Fee Entry", use_container_width=True, key="back_to_form"):
        st.session_state.show_share_options = False
        st.rerun()

def generate_fee_details_message(student_name, class_category, total_amount, fee_breakdown):
    """Generate WhatsApp message with complete fee breakdown - plain text format"""
    from datetime import datetime
    from database import load_school_config
    
    school_config = load_school_config()
    school_name = school_config.get("school_name", "British School of Karachi")
    
    message = f"""💰 FEE PAYMENT SLIP

STUDENT INFORMATION:
Name: {student_name}
Class: {class_category}

FEE BREAKDOWN:"""
    
    # Add monthly fees if applicable
    if fee_breakdown.get("monthly_fee", 0) > 0 and fee_breakdown.get("selected_months"):
        months_str = ", ".join(fee_breakdown["selected_months"])
        monthly_total = fee_breakdown["monthly_fee"] * len(fee_breakdown["selected_months"])
        message += f"\nMonthly Fee ({months_str}): Rs. {int(monthly_total):,}"
    
    # Add annual charges if applicable
    if fee_breakdown.get("annual_charges", 0) > 0:
        message += f"\nAnnual Charges: Rs. {int(fee_breakdown['annual_charges']):,}"
    
    # Add admission fee if applicable
    if fee_breakdown.get("admission_fee", 0) > 0:
        message += f"\nAdmission Fee: Rs. {int(fee_breakdown['admission_fee']):,}"
    
    message += f"""

PAYMENT DETAILS:
Total Amount: Rs. {int(total_amount):,}
Payment Method: {fee_breakdown.get('payment_method', 'Not specified')}
Date: {fee_breakdown.get('payment_date', datetime.now().strftime('%d-%m-%Y'))}

STATUS: ✅ Payment Received

Thank you for your payment!

{school_name}
Fees Management System"""
    
    return message

def calculate_total_amount(pay_monthly, pay_annual, pay_admission, monthly_fee, annual_charges, admission_fee, selected_months):
    """Calculate total amount based on selected fee types"""
    total = 0
    if pay_monthly:
        total += monthly_fee * len(selected_months)
    if pay_annual:
        total += annual_charges
    if pay_admission:
        total += admission_fee
    return total

def update_fee_calculation(student_id, academic_year):
    """Update fee calculation when fee type changes"""
    # This function is kept for compatibility but logic moved to calculate_total_amount
    pass

def update_student_data(student_name, class_category):
    """Update session state with student data when name or class changes"""
    if student_name and class_category:
        student_id = generate_student_id(student_name, class_category)
        st.session_state.current_student_id = student_id
        st.session_state.available_months = get_unpaid_months(student_id)
        
        # Reset fee calculation when student changes
        st.session_state.current_total_amount = 0
        st.session_state.previous_fee_type = "Monthly Fee"
        st.session_state.previous_month_selection = "Select a month"
    else:
        st.session_state.current_student_id = None
        st.session_state.available_months = []
        st.session_state.current_total_amount = 0

def display_student_records(student_id):
    """Display student payment history"""
    st.subheader("📋 Student Payment History")
    
    df = load_data()
    student_records = df[df['ID'] == student_id]
    
    if not student_records.empty:
        display_df = student_records[[ 
            "Student Name", "Father Name", "Month", "Monthly Fee", "Annual Charges", 
            "Admission Fee", "Received Amount", "Payment Method", "Date", "Academic Year"
        ]].sort_values("Date", ascending=False)
        
        st.dataframe(
            display_df.style.format({
                "Monthly Fee": format_currency,
                "Annual Charges": format_currency,
                "Admission Fee": format_currency,
                "Received Amount": format_currency
            }),
            use_container_width=True
        )
        
        # Calculate totals
        total_monthly = student_records["Monthly Fee"].sum()
        total_annual = student_records["Annual Charges"].sum()
        total_admission = student_records["Admission Fee"].sum()
        total_received = student_records["Received Amount"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Monthly", format_currency(total_monthly))
        col2.metric("Total Annual", format_currency(total_annual))
        col3.metric("Total Admission", format_currency(total_admission))
        col4.metric("Total Received", format_currency(total_received))
        
        # Show payment status
        st.subheader("Payment Status")
        payment_date = st.session_state.get(f"payment_date_{st.session_state.form_key}", datetime.now())
        academic_year = get_academic_year(payment_date)
        
        annual_paid, admission_paid = check_annual_admission_paid(student_id, academic_year)
        unpaid_months = st.session_state.available_months
        
        col_paid, col_unpaid = st.columns(2)
        
        with col_paid:
            st.markdown("#### ✅ Paid Months")
            paid_months = student_records[student_records['Monthly Fee'] > 0]['Month'].unique()
            if len(paid_months) > 0:
                for month in sorted(paid_months):
                    amount = student_records[student_records['Month'] == month]['Monthly Fee'].iloc[0]
                    st.markdown(f"- {month}: {format_currency(amount)}")
            else:
                st.markdown("No months paid yet")
        
        with col_unpaid:
            st.markdown("#### ❌ Unpaid Months")
            if len(unpaid_months) > 0:
                for month in unpaid_months:
                    st.markdown(f"- {month}")
            else:
                st.markdown("All months paid")
        
        st.markdown("---")
        st.markdown(f"**Annual Fees Paid**: {'✅ Yes' if annual_paid else '❌ No'}")
        st.markdown(f"**Admission Fee Paid**: {'✅ Yes' if admission_paid else '❌ No'}")
        
        # Show current fee settings
        st.subheader("💰 Current Fee Settings")
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        annual_fee = get_student_fee_amount(student_id, "annual")
        admission_fee = get_student_fee_amount(student_id, "admission")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly Fee", format_currency(monthly_fee))
        col2.metric("Annual Charges", format_currency(annual_fee))
        col3.metric("Admission Fee", format_currency(admission_fee))
        
    else:
        st.info("No fee records found for this student.")
        unpaid_months = st.session_state.available_months
        
        st.markdown("#### ❌ Unpaid Months")
        if len(unpaid_months) > 0:
            for month in unpaid_months:
                st.markdown(f"- {month}")
        else:
            st.markdown("All months paid")
        
        # Show current fee settings for new students too
        st.subheader("💰 Current Fee Settings")
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        annual_fee = get_student_fee_amount(student_id, "annual")
        admission_fee = get_student_fee_amount(student_id, "admission")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly Fee", format_currency(monthly_fee))
        col2.metric("Annual Charges", format_currency(annual_fee))
        col3.metric("Admission Fee", format_currency(admission_fee))

def handle_monthly_fee(student_id, fees_data, academic_year):
    """Handle monthly fee input with dynamic fees"""
    monthly_fee = 0
    selected_months = []
    
    if not student_id:
        st.warning("Please enter Student Name and select Class Category.")
    elif not st.session_state.available_months:
        st.error("All months have been paid for this student!")
    else:
        # Get monthly fee from database (dynamic)
        monthly_fee = get_student_fee_amount(student_id, "monthly")
        
        st.text_input(
            "Monthly Fee Amount per Month*",
            value=format_currency(monthly_fee),
            disabled=True,
            key=f"monthly_fee_{st.session_state.form_key}"
        )
        
        # Show fee source information
        if student_id in fees_data:
            st.success(f"✅ Admin set monthly fee: {format_currency(monthly_fee)}")
        else:
            st.info(f"ℹ️ Using default monthly fee: {format_currency(monthly_fee)}")
        
        # Multiple month selection
        available_months = st.session_state.available_months
        selected_months = st.multiselect(
            "Select Month(s)*",
            available_months,
            key=f"month_select_{st.session_state.form_key}"
        )
        
        if selected_months:
            st.markdown(f"**Selected Months**: {', '.join(selected_months)}")
            st.markdown(f"**Amount to Pay**: {format_currency(monthly_fee * len(selected_months))}")
        else:
            st.markdown("**Selected Months**: None")
    
    return monthly_fee, selected_months

def handle_annual_charges(student_id, academic_year, fees_data):
    """Handle annual charges input with dynamic fees"""
    annual_charges = 0
    
    if student_id:
        annual_paid, _ = check_annual_admission_paid(student_id, academic_year)
        if annual_paid:
            st.error("Annual charges have already been paid for this academic year!")
            return None
        else:
            # Get annual charges from database (dynamic)
            annual_charges = get_student_fee_amount(student_id, "annual")
            
            st.text_input(
                "Annual Charges Amount*",
                value=format_currency(annual_charges),
                disabled=True,
                key=f"annual_charges_{st.session_state.form_key}"
            )
            
            # Show fee source information
            if student_id in fees_data:
                st.success(f"✅ Admin set annual charges: {format_currency(annual_charges)}")
            else:
                st.info(f"ℹ️ Using default annual charges: {format_currency(annual_charges)}")
            
            return annual_charges, ["ANNUAL"]
    else:
        st.warning("Please enter Student Name and select Class Category.")
        return None

def handle_admission_fee(student_id, academic_year, fees_data):
    """Handle admission fee input with dynamic fees"""
    admission_fee = 0
    
    if student_id:
        _, admission_paid = check_annual_admission_paid(student_id, academic_year)
        if admission_paid:
            st.error("Admission fee has already been paid for this academic year!")
            return None
        else:
            # Get admission fee from database (dynamic)
            admission_fee = get_student_fee_amount(student_id, "admission")
            
            st.text_input(
                "Admission Fee Amount*",
                value=format_currency(admission_fee),
                disabled=True,
                key=f"admission_fee_{st.session_state.form_key}"
            )
            
            # Show fee source information
            if student_id in fees_data:
                st.success(f"✅ Admin set admission fee: {format_currency(admission_fee)}")
            else:
                st.info(f"ℹ️ Using default admission fee: {format_currency(admission_fee)}")
            
            return admission_fee, ["ADMISSION"]
    else:
        st.warning("Please enter Student Name and select Class Category.")
        return None

def refresh_form():
    """Refresh the form"""
    st.session_state.form_key += 1
    st.session_state.last_student_name = ""
    st.session_state.last_father_name = ""
    st.session_state.last_class_category = None
    st.session_state.last_class_section = ""
    st.session_state.current_student_id = None
    st.session_state.available_months = []
    st.session_state.current_fee_type = "Monthly Fee"
    st.session_state.current_total_amount = 0
    st.session_state.previous_fee_type = "Monthly Fee"
    st.session_state.previous_month_selection = "Select a month"
    st.session_state.last_generated_slip = None
    st.session_state.show_share_options = False

def handle_form_submission(
    student_name, father_name, class_category, class_section, student_id,
    signature, pay_monthly, pay_annual, pay_admission,
    selected_months, monthly_fee, annual_charges, admission_fee, 
    received_amount, payment_method, payment_date, academic_year,
    annual_paid, admission_paid
):
    """Handle form submission with multiple fee types"""
    if not student_name or not father_name or not class_category or not signature:
        st.error("Please fill all required fields (*)")
        return False
    elif not student_id:
        st.error("Please enter Student Name and select Class Category.")
        return False
    elif pay_monthly and not selected_months:
        st.error("Please select at least one month for Monthly Fee payment.")
        return False
    elif pay_annual and annual_paid:
        st.error("Annual charges have already been paid for this academic year!")
        return False
    elif pay_admission and admission_paid:
        st.error("Admission fee has already been paid for this academic year!")
        return False
    elif not (pay_monthly or pay_annual or pay_admission):
        st.error("Please select at least one fee type to pay.")
        return False
    else:
        fee_records = []
        
        # Always use the calculated total amount as received amount
        calculated_received_amount = st.session_state.current_total_amount
        
        from database import get_student_detail
        student_detail = get_student_detail(student_id)
        address = student_detail.get("address", "")
        age = student_detail.get("age", "")
        student_phone = student_detail.get("phone", "")
        
        # Create records for each fee type
        if pay_monthly:
            for month in selected_months:
                fee_data = {
                    "ID": student_id,
                    "Student Name": student_name,
                    "Father Name": father_name,
                    "Student Phone": student_phone,
                    "Class Category": class_category,
                    "Class Section": class_section,
                    "Address": address,
                    "Age": age,
                    "Month": month,
                    "Monthly Fee": monthly_fee,
                    "Annual Charges": 0,
                    "Admission Fee": 0,
                    "Received Amount": monthly_fee,
                    "Payment Method": payment_method,
                    "Date": payment_date.strftime("%Y-%m-%d"),
                    "Signature": signature,
                    "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Academic Year": academic_year
                }
                fee_records.append(fee_data)
        
        if pay_annual:
            fee_data = {
                "ID": student_id,
                "Student Name": student_name,
                "Father Name": father_name,
                "Student Phone": student_phone,
                "Class Category": class_category,
                "Class Section": class_section,
                "Address": address,
                "Age": age,
                "Month": "ANNUAL",
                "Monthly Fee": 0,
                "Annual Charges": annual_charges,
                "Admission Fee": 0,
                "Received Amount": annual_charges,
                "Payment Method": payment_method,
                "Date": payment_date.strftime("%Y-%m-%d"),
                "Signature": signature,
                "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Academic Year": academic_year
            }
            fee_records.append(fee_data)
        
        if pay_admission:
            fee_data = {
                "ID": student_id,
                "Student Name": student_name,
                "Father Name": father_name,
                "Student Phone": student_phone,
                "Class Category": class_category,
                "Class Section": class_section,
                "Address": address,
                "Age": age,
                "Month": "ADMISSION",
                "Monthly Fee": 0,
                "Annual Charges": 0,
                "Admission Fee": admission_fee,
                "Received Amount": admission_fee,
                "Payment Method": payment_method,
                "Date": payment_date.strftime("%Y-%m-%d"),
                "Signature": signature,
                "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Academic Year": academic_year
            }
            fee_records.append(fee_data)
        
        if save_to_csv(fee_records):
            st.session_state.fee_breakdown = {
                "monthly_fee": monthly_fee if pay_monthly else 0,
                "annual_charges": annual_charges if pay_annual else 0,
                "admission_fee": admission_fee if pay_admission else 0,
                "selected_months": selected_months if pay_monthly else [],
                "payment_method": payment_method,
                "payment_date": payment_date.strftime("%d-%m-%Y")
            }
            
            # Generate combined slip data
            slip_data = {
                "student_name": student_name,
                "father_name": father_name,
                "class_category": class_category,
                "class_section": class_section,
                "payment_date": payment_date.strftime("%d-%m-%Y"),
                "academic_year": academic_year,
                "monthly_fee": monthly_fee if pay_monthly else 0,
                "annual_charges": annual_charges if pay_annual else 0,
                "admission_fee": admission_fee if pay_admission else 0,
                "received_amount": calculated_received_amount,
                "payment_method": payment_method,
                "signature": signature,
                "months": selected_months if pay_monthly else [],
                "pay_monthly": pay_monthly,
                "pay_annual": pay_annual,
                "pay_admission": pay_admission
            }
            
            # Generate slip image
            slip_image_path = generate_fee_slip(slip_data)
            st.session_state.last_generated_slip = slip_image_path
            st.session_state.show_share_options = True
            
            # Store the success message in session state to display after rerun
            st.session_state.success_message = "✅ Fee record(s) saved successfully!"
            st.session_state.show_balloons = True
            
            # Update session state
            st.session_state.last_student_name = student_name
            st.session_state.last_father_name = father_name
            st.session_state.last_class_category = class_category
            st.session_state.last_class_section = class_section or ""
            st.session_state.form_key += 1
            st.session_state.available_months = get_unpaid_months(student_id)
            st.session_state.last_saved_records = fee_records
            st.session_state.current_total_amount = 0
            st.session_state.previous_fee_type = "Monthly Fee"
            st.session_state.previous_month_selection = "Select a month"
            
            st.rerun()
            return True
        else:
            st.error("Failed to save fee records. Please try again.")
            return False
    
    return True
