from time import sleep
import streamlit as st
from PIL import Image 
import io
import os
import google.generativeai as genai
from Model import Model,get_image_base_text_generator_models,get_text_generator_models,set_api_key

# -------------------------------------------------------Functions-----------------------------------------------------------
def get_stream_data(response):
    for res in response.text:
        yield res
        sleep(0.001)

def set_api_key_page():
    st.title("Configure Google API Key")
    api_key = st.text_input("Enter your google API key:", type="password")  # Mask input for security

    if st.button("Set API Key"):        
        is_key_set = set_api_key(api_key)
        if is_key_set:
            st.success(" API Key set successfully!",icon="✅")
            st.rerun()
        else:
            st.error(" Please enter valid API key.",icon="🛑")


def chat_page():
    with st.sidebar:
        c1,c2 = st.columns(2)
        with c1: st.logo('logo/logo side bar.png',icon_image='logo/logo.jpg')
        model_type = st.radio("Select model type:", ["🔠 Text Model", "🖼️ Vision Model"])

        container = st.container(border=True)
        if model_type == '🖼️ Vision Model':
            container.write("Vision model, which processe the image and text you provide as input and then generates relevant output based on image and text.")
            model_details = get_image_base_text_generator_models()
            is_image_uploader = True
        else:
            container.write("Text model, which processes the text you provide as input and then generates a relevant output based on that input.")
            model_details = get_text_generator_models()
            is_image_uploader = False

        selected_model = st.selectbox(
            "Select the model you want to talk:",
            [model['display_name'] for model in model_details]
        )

        for model in model_details:
            if model['display_name'] == selected_model:
                model_object = Model(model['name'])

                with st.expander("Model Details"):
                    st.markdown(f"**Model Name:** {model['display_name']}")
                    st.markdown(f"**Version:** {model['Version']}")
                    st.markdown(f"**Description:** {model['Description']}")
                    st.markdown(f"**Input Token Limit:** {model['Input Token Limit']}")
                    st.markdown(f"**Output Token Limit:** {model['Output Token Limit']}")
                    st.markdown(f"**Supported Generation Methods:** {', '.join(model['Supported Generation Methods'])}")
                    st.markdown(f"**Temperature:** {model['Temperature']}")
                    st.markdown(f"**Top P:** {model['Top P']}")
                    st.markdown(f"**Top K:** {model['Top K']}")

        if is_image_uploader:
            uploaded_file = st.file_uploader("Choose an image.")

            if uploaded_file is not None:
                uploaded_image = Image.open(uploaded_file)
                image_bytes = io.BytesIO()
                uploaded_image.save(image_bytes, format='PNG')
                image_bytes.seek(0)
                st.session_state['image_bytes'] = image_bytes
                st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)
            else:
                st.write('Please upload an image.')
                image_bytes = None

    if "message_history" not in st.session_state:
        st.session_state['message_history'] = []

    for message in st.session_state['message_history']:
        with st.chat_message(message['role']):
            if isinstance(message['content'], list) and len(message['content']) == 2:
                st.markdown(message['content'][0])
                image_bytes = io.BytesIO(message['content'][1])
                st.image(image_bytes, use_column_width=True)
            else:
                st.markdown(message['content'])

    if prompt := st.chat_input('How can I help you today?'):
        with st.chat_message('user'):
            st.markdown(prompt)
            if is_image_uploader and 'image_bytes' in st.session_state:
                st.image(st.session_state['image_bytes'].getvalue())

        if is_image_uploader and uploaded_file is not None and 'image_bytes' in st.session_state:
            st.session_state['message_history'].append({"role": "user", 'content': [prompt, st.session_state['image_bytes'].getvalue()]})
            response = model_object.get_vision_model_response(prompt, uploaded_image)
        else:
            st.session_state['message_history'].append({"role": "user", 'content': prompt})
            response = model_object.get_text_model_response(prompt)

        with st.chat_message(name='Bandhu', avatar='🤝'):
            st.write_stream(get_stream_data(response))
        st.session_state['message_history'].append({"role": "🤝", 'content': response.text})

# ------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ.keys():
        set_api_key_page()
    else:
        chat_page()