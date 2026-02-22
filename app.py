import streamlit as st
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image

st.set_page_config(page_title="בודק טולרנסים", layout="wide")
st.title("🔍 בודק טולרנסים מהיר")

# הגדרה לקריאת PDF בשרת
uploaded_file = st.file_uploader("העלה שרטוט PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner('מנתח את השרטוט...'):
        # 1. המרה לתמונה
        images = convert_from_bytes(uploaded_file.read())
        img_np = np.array(images[0])
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # 2. זיהוי טקסט (שימוש במנוע קל יותר)
        data = pytesseract.image_to_data(img_np, output_type=pytesseract.Output.DICT)
        
        missing_count = 0
        for i in range(len(data)):
            text = data[i].strip()
            
            # בדיקה אם זה מספר (מידה)
            if text.isdigit() or (text.replace('.','',1).isdigit()):
                # בדיקה אם יש סימן טולרנס בטקסט הסמוך
                context = " ".join(data[max(0, i-2):i+3])
                if '±' not in context and '+-' not in context:
                    # סימון בעיגול אדום
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    cv2.circle(img_cv, (x + w//2, y + h//2), 30, (0, 0, 255), 3)
                    missing_count += 1

        st.subheader(f"נמצאו {missing_count} מידות ללא טולרנס:")
        st.image(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB), use_column_width=True)
