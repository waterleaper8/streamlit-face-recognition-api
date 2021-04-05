import streamlit as st
import requests
import json
import io
import os
from PIL import Image, ImageDraw, ImageFont

st.title('顔認識アプリ')

subscription_key = st.text_area('APIキー')
if subscription_key:

# with open('secret.json') as f:
#     secret_json = json.load(f)

# subscription_key = secret_json['SUBSCRIPTION_KEY']
# assert subscription_key

    face_api_url = 'https://facekmkm.cognitiveservices.azure.com/face/v1.0/detect'

    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    params = {
        'returnFaceId': 'true',
        'returnFaceAttributes': 'blur,exposure,noise,age,gender,facialhair,glasses,hair,makeup,accessories,occlusion,headpose,emotion,smile'
    }

    uploaded_file = st.file_uploader("Choose an image", type=['jpg','jpeg','png'])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)

        # with open('sample_02.jpeg', 'rb') as f:
        #     binary_img = f.read()
        with io.BytesIO() as output:
            img.save(output, format="JPEG")
            binary_img = output.getvalue() # バイナリ取得


        res = requests.post(face_api_url, params=params, headers=headers, data=binary_img)

        results = res.json()

        fnt = ImageFont.truetype("Helvetica.ttc", 24)

        for result in results:
            rect = result['faceRectangle']
            age = result['faceAttributes']['age']
            gender = result['faceAttributes']['gender']

            draw = ImageDraw.Draw(img)
            draw.rectangle([(rect['left'], rect['top']), (rect['left']+rect['width'], rect['top']+rect['height'])], fill=None, outline='red', width=5)
            draw.text((rect['left'], rect['top']-20), f'{gender} {age}', font=fnt, fill='white')

        st.image(img, caption='Uploaded Image.', use_column_width=True)

    

