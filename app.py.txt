import streamlit as st
import easyocr
import cv2
import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image

st.set_page_config(page_title="בודק טולרנסים חכם", layout="wide")
st.title("📏 בודק מידות וטולרנסים (ללא טבלת כותרת)")

uploaded_file = st.file_uploader("העלה שרטוט PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner('מנתח שרטוט ומסנן טבלאות...'):
        # 1. המרה לתמונה
        images = convert_from_bytes(uploaded_file.read())
        img_np = np.array(images[0])
        h, w, _ = img_np.shape
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # 2. הגדרת אזור טבלת כותרת (למשל: 25% תחתון ימני)
        # אפשר לשנות את האחוזים כאן לפי סוג השרטוטים שלך
        forbidden_zone_x = w * 0.70  # מ-70% מהרוחב ומעלה
        forbidden_zone_y = h * 0.70  # מ-70% מהגובה ומעלה

        # 3. OCR
        reader = easyocr.Reader(['en'])
        results = reader.readtext(img_np)
        
        missing_count = 0
        for i, (bbox, text, prob) in enumerate(results):
            # מיקום הטקסט
            (tl, tr, br, bl) = bbox
            curr_x, curr_y = int(tl[0]), int(tl[1])
            
            # סינון: אם הטקסט בתוך טבלת הכותרת - דלג
            if curr_x > forbidden_zone_x and curr_y > forbidden_zone_y:
                continue

            # בדיקה אם מדובר במידה (מספר)
            clean_text = text.replace(" ", "")
            if any(char.isdigit() for char in clean_text):
                
                # בדיקת טולרנס (בטקסט עצמו או בסביבתו)
                has_tol = '±' in clean_text or '+-' in clean_text
                if not has_tol:
                    for j in range(max(0, i-2), min(len(results), i+3)):
                        if '±' in results[j][1] or '+-' in results[j][1]:
                            has_tol = True
                            break
                
                if not has_tol:
                    # ציור עיגול אדום
                    cv2.circle(img_cv, (curr_x + 10, curr_y + 10), 30, (0, 0, 255), 3)
                    missing_count += 1

        # הצגה
        st.subheader(f"זיהינו {missing_count} מידות ללא טולרנס מחוץ לטבלת הכותרת")
        st.image(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB), use_column_width=True)
