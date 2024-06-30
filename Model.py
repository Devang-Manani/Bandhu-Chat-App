import google.generativeai as genai
import json
import requests
import os

class Model:
    def __init__(self,model_name):
        self._model = genai.GenerativeModel(model_name=model_name)
        self._chat = self._model.start_chat(history=[])
    
    def get_text_model_response(self,prompt):
        return self._chat.send_message(prompt)

    def get_vision_model_response(self,prompt,img=''):
        return self._model.generate_content([prompt,img])

    
def get_text_generator_models():
    with open('model_info/text_generator_models.json','r') as f:
        return json.load(f)

def get_image_base_text_generator_models():
    with open('model_info/image_base_text_generator_models.json','r') as f:
        return json.load(f)
    
def set_api_key(KEY):
    url = f"https://generativelanguage.googleapis.com/v1/models?key={KEY}"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        genai.configure(api_key=KEY)
        os.environ["GOOGLE_API_KEY"] = KEY
        return True
    else:
        return False
        