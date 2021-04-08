import streamlit as st
import requests
import json
import io
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import base64

st.title('顔認識アプリ')

if os.path.exists('secret.json'):
    with open('secret.json') as f:
        secret_json = json.load(f)
    subscription_key = secret_json['SUBSCRIPTION_KEY']
    assert subscription_key
else:
    subscription_key = st.text_area('APIキー')

face_api_url = 'https://facekmkm.cognitiveservices.azure.com/face/v1.0/detect'

headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': subscription_key
}
params = {
    'returnFaceId': 'true',
    'returnFaceAttributes': 'blur,exposure,noise,age,gender,facialhair,glasses,hair,makeup,accessories,occlusion,headpose,emotion,smile'
}

def pil2cv(image):
    # ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

uploaded_file = st.file_uploader("Choose an image", type=['jpg','jpeg'])
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    with io.BytesIO() as output:
        img.save(output, format="JPEG")
        binary_img = output.getvalue() # バイナリ取得
    
    

    frame = pil2cv(img)

    res = requests.post(face_api_url,
        params=params,
        headers=headers,
        data=binary_img)
    results = res.json()

    for result in results:
        rect = result['faceRectangle']
        age = result['faceAttributes']['age']
        gender = result['faceAttributes']['gender']
        # if gender == 'male':
        #     gender = '男性'
        # else:
        #     gender = '女性'
        label = gender + ' ' + str(age)
        label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)

        start_x = rect['left']
        start_y = rect['top']
        end_x = rect['left']+rect['width']
        end_y = rect['top']+rect['height']

        
        # draw = ImageDraw.Draw(img)
        # draw.rectangle([(start_x, start_y), (end_x, end_y)], fill=None, outline='red', width=5)
        # draw.text((rect['left'], rect['top']-20), f'{gender} {age}', font=fnt, fill='white')
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
        cv2.rectangle(frame, (start_x, start_y - label_size[1]),
            (start_x + label_size[0], start_y + base_line),
            (255, 255, 255), cv2.FILLED)
        cv2.putText(frame, label,
            (start_x, start_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 0, 0))
        img = cv2pil(frame)

    st.image(img, caption='Uploaded Image.', use_column_width=True)

    

