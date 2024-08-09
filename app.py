from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import base64
import io

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, file_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, file_content[0], prompt])
    return response.text

def input_file_setup(uploaded_file):
    if uploaded_file is not None:
        # Check if the uploaded file is an image or a PDF
        if uploaded_file.type == "application/pdf":
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            first_page = images[0]
        else:  # Assuming it's an image (jpg, jpeg, png)
            first_page = Image.open(uploaded_file)
        
        # Convert the image to RGB mode if it has an alpha channel (RGBA)
        if first_page.mode == "RGBA":
            first_page = first_page.convert("RGB")

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue() 

        file_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  
            }
        ]
        return file_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App
st.set_page_config(page_title="Invoice Data Extractor")
st.header("Invoice Data Extractor")
uploaded_file = st.file_uploader("Upload your invoice in PDF or image form.", type=["pdf","jpg","jpeg","png"])

submit1 = st.button("Extract Customer Details")
submit2 = st.button("Extract Products")
submit3 = st.button("Extract Total Amount")

input_prompt1 = """
Extract customer details from the invoice image provided. Include the customer's name, address, and contact information if available.
"""

input_prompt2 = """
Extract a list of products from the invoice image provided. Include the product name, quantity, and price for each item.
"""

input_prompt3 = """
Extract the total amount from the invoice image provided. Provide the total amount as stated on the invoice.
"""

if submit1:
    if uploaded_file is not None:
        file_content = input_file_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, file_content, "")
        st.subheader("Customer Details:")
        st.write(response)
    else:
        st.write("Please upload the invoice")
elif submit2:
    if uploaded_file is not None:
        file_content = input_file_setup(uploaded_file)
        response = get_gemini_response(input_prompt2, file_content, "")
        st.subheader("Products List:")
        st.write(response)
    else:
        st.write("Please upload the invoice")
elif submit3:
    if uploaded_file is not None:
        file_content = input_file_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, file_content, "")
        st.subheader("Total Amount:")
        st.write(response)
    else:
        st.write("Please upload the invoice")
