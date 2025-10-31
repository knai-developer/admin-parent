# type:ignore
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import webbrowser
from urllib.parse import quote
import base64
from database import load_school_config

def display_menu_bar():
    """Display menu bar with school name and logo"""
    school_config = load_school_config()
    school_name = school_config.get("school_name", "School Name")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        try:
            with open("school-pic.png", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            st.markdown(
                f'<img src="data:image/png;base64,{img_base64}" alt="School Logo" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">',
                unsafe_allow_html=True
            )
        except:
            st.markdown("🏫")
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px;">
            <h3 style="margin: 0; color: #2c3e50;">{school_name}</h3>
            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">Fee Payment Slip</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("")
    
    st.markdown("---")

def generate_fee_slip(slip_data):
    """Generate a fee slip as PNG image with only the fees being paid"""
    
    school_config = load_school_config()
    school_name = school_config.get("school_name", "Your School Name")
    
    # Create image
    width, height = 600, 900
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Load fonts (using default fonts)
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        header_font = ImageFont.truetype("arial.ttf", 20)
        normal_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default fonts
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    draw.rectangle([0, 0, width, 80], fill='#2c3e50')
    draw.text((width//2, 30), school_name.upper(), fill='white', font=title_font, anchor="mm")
    draw.text((width//2, 60), "FEE PAYMENT SLIP", fill='white', font=header_font, anchor="mm")
    
    y_position = 100
    
    # Student information
    draw.text((50, y_position), f"Student Name: {slip_data['student_name']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Phone: {slip_data.get('student_phone', 'N/A')}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Class: {slip_data['class_category']} {slip_data['class_section']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Payment Date: {slip_data['payment_date']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((50, y_position), f"Academic Year: {slip_data['academic_year']}", fill='black', font=normal_font)
    
    y_position += 50
    
    # Fee details header
    draw.rectangle([50, y_position, width-50, y_position+40], fill='#3498db', outline='#3498db')
    draw.text((width//2, y_position+20), "FEE DETAILS", fill='white', font=header_font, anchor="mm")
    
    y_position += 60
    
    fees_to_show = []
    total_amount = 0
    
    # Monthly fees - only show if paying monthly and amount is greater than 0
    if slip_data.get('pay_monthly', False) and slip_data['monthly_fee'] > 0 and slip_data['months']:
        for month in slip_data['months']:
            if month not in ['ANNUAL', 'ADMISSION']:
                fees_to_show.append((f"Monthly Fee - {month}", slip_data['monthly_fee']))
                total_amount += slip_data['monthly_fee']
    
    # Annual charges - only show if paying annual and amount is greater than 0
    if slip_data.get('pay_annual', False) and slip_data['annual_charges'] > 0:
        fees_to_show.append(("Annual Charges", slip_data['annual_charges']))
        total_amount += slip_data['annual_charges']
    
    # Admission fee - only show if paying admission and amount is greater than 0
    if slip_data.get('pay_admission', False) and slip_data['admission_fee'] > 0:
        fees_to_show.append(("Admission Fee", slip_data['admission_fee']))
        total_amount += slip_data['admission_fee']
    
    # Display all fees that are being paid
    if fees_to_show:
        for fee_name, amount in fees_to_show:
            draw.text((80, y_position), fee_name, fill='black', font=normal_font)
            draw.text((width-120, y_position), f"Rs. {amount:,}", fill='black', font=normal_font)
            y_position += 25
    else:
        draw.text((width//2, y_position), "No fees selected", fill='red', font=normal_font, anchor="mm")
        y_position += 25
    
    y_position += 20
    
    # Total line
    draw.line([50, y_position, width-50, y_position], fill='black', width=2)
    y_position += 10
    
    draw.text((80, y_position), "TOTAL AMOUNT", fill='black', font=header_font)
    draw.text((width-120, y_position), f"Rs. {total_amount:,}", fill='black', font=header_font)
    
    y_position += 50
    
    # Payment information
    draw.rectangle([50, y_position, width-50, y_position+120], fill='#f8f9fa', outline='#ddd')
    
    y_position += 20
    draw.text((width//2, y_position), "PAYMENT INFORMATION", fill='#2c3e50', font=header_font, anchor="mm")
    y_position += 40
    
    draw.text((80, y_position), f"Payment Method: {slip_data['payment_method']}", fill='black', font=normal_font)
    y_position += 30
    draw.text((80, y_position), f"Amount Received: Rs. {total_amount:,}", fill='black', font=normal_font)
    y_position += 30
    draw.text((80, y_position), f"Received By: {slip_data['signature']}", fill='black', font=normal_font)
    
    y_position += 60
    
    # Footer
    draw.text((width//2, y_position), "Thank you for your payment!", fill='#7f8c8d', font=small_font, anchor="mm")
    y_position += 25
    draw.text((width//2, y_position), "Generated by School Fees Management System", fill='#7f8c8d', font=small_font, anchor="mm")
    
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fee_slip_{slip_data['student_name'].replace(' ', '_')}_{timestamp}.png"
    filepath = os.path.join("slips", filename)
    
    # Create slips directory if it doesn't exist
    os.makedirs("slips", exist_ok=True)
    
    image.save(filepath)
    return filepath

def share_slip_via_whatsapp(image_path, student_name, class_category):
    """Share slip via WhatsApp with proper implementation"""
    try:
        # Create WhatsApp share message
        message = f"Fee Payment Slip for {student_name} - {class_category}"
        
        # Encode the message for URL
        encoded_message = quote(message)
        
        # For web version - open WhatsApp Web with message
        whatsapp_url = f"https://web.whatsapp.com/send?text={encoded_message}"
        
        # For mobile devices - try different approaches
        mobile_urls = [
            f"whatsapp://send?text={encoded_message}",
            f"https://api.whatsapp.com/send?text={encoded_message}"
        ]
        
        # Try to open WhatsApp
        success = False
        for url in mobile_urls:
            try:
                webbrowser.open(url)
                success = True
                break
            except:
                continue
        
        if not success:
            # Fallback to WhatsApp Web
            webbrowser.open(whatsapp_url)
        
        # Show instructions for image sharing
        st.success("📱 WhatsApp opened! Please manually attach the slip image:")
        st.info(f"""
        **To share the slip image on WhatsApp:**
        1. **Download the slip** using the 'Download Slip as Image' button
        2. **Open WhatsApp** (should open automatically)
        3. **Attach the image**: Click the attachment icon ➕ → Gallery/Documents → Select the downloaded slip
        4. **Send** the message
        
        **File Location:** The slip is saved as: `{os.path.basename(image_path)}`
        """)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to open WhatsApp: {str(e)}")
        st.info("""
        **Manual WhatsApp Sharing:**
        1. Download the slip image using the button below
        2. Open WhatsApp manually
        3. Select the contact/group
        4. Attach the downloaded slip image
        5. Send with your message
        """)
        return False

def get_image_base64(image_path):
    """Convert image to base64 for display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def create_whatsapp_direct_share(image_path, student_name, class_category):
    """Create a direct WhatsApp share link (limited functionality due to browser restrictions)"""
    # Note: Direct image sharing via URL is not supported by WhatsApp Web API
    # This is a workaround that opens WhatsApp with a message
    message = f"Fee Payment Slip for {student_name} - {class_category}\nPlease find the attached fee slip."
    encoded_message = quote(message)
    
    whatsapp_url = f"https://web.whatsapp.com/send?text={encoded_message}"
    return whatsapp_url
