import json
import os
import requests

MODEL_NAME = 'TheBloke/samantha-falcon-7B-GPTQ'
API_URL = 'https://api-inference.huggingface.co/models/' + MODEL_NAME
API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')
headers = {'Authorization': f'Bearer {API_TOKEN}'}


def generate_text(query):
    payload = {
        'inputs': query + '\n',
        'parameters': {
            'return_full_text': False,
            'max_new_tokens': 250
        },
        'options': {
            'wait_for_model': True
        }
    }
    data = json.dumps(payload)
    response = requests.request('POST', API_URL, headers=headers, data=data)
    return json.loads(response.content.decode('utf-8'))

