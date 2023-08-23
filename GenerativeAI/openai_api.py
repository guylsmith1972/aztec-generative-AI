import openai
import os


class OpenAIAPI:
    @staticmethod
    def get_response_prompt():
        return 'Response:'

    @staticmethod
    def query(prompt, display_progress=False):
        # Load the API key from an environment variable or secret management service
        openai_api_key = os.getenv('OPENAI_KEY')

        # Set the API key
        openai.api_key = openai_api_key

        if display_progress:
            print(f'Submitting to OpenAI: {prompt}')

        # create a chat completion
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f'{prompt}\n{OpenAIAPI.get_response_prompt()}\n'}])

        # return the chat completion
        response = chat_completion.choices[0].message.content
    
        if display_progress:
            print(f'OpenAI responded with: {response}')
    
        return response
