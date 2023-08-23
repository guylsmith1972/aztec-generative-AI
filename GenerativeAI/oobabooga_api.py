import requests

# For local streaming, the websockets are hosted without ssl - http://
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'


class OobaboogaAPI:
    @staticmethod
    def get_response_prompt():
        return '### Response:'

    @staticmethod
    def query(prompt, display_progress=False):
        if display_progress:
            print('\n\n')
            print('-' * 80)
            print(f'Running oobabooga prompt: {prompt}\n')
        request = {
            'prompt': f'{prompt}\n### Response:',
            'max_new_tokens': 2048,
            'auto_max_new_tokens': False,

            # Generation params. If 'preset' is set to different than 'None', the values
            # in presets/preset-name.yaml are used instead of the individual numbers.
            'preset': 'None',
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 20,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.15,
            'repetition_penalty_range': 0,
            'min_length': 1,
            'no_repeat_ngram_size': 0,
            'encoder_repetition_penalty': 1,

            # 'num_beams': 1,
            # 'penalty_alpha': 0,
            # 'length_penalty': 1,
            # 'early_stopping': False,
            # 'mirostat_mode': 0,
            # 'mirostat_tau': 5,
            # 'mirostat_eta': 0.1,
            # 'guidance_scale': 1,
            # 'negative_prompt': '',

            'seed': -1,
            'add_bos_token': False,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stopping_strings': []
        }

        response = requests.post(URI, json=request)

        if response.status_code == 200:
            result = response.json()['results'][0]['text']
            parts = result.split(':')
            if len(parts) > 1:
                if parts[0].lower().strip() in ['answer', 'machine', 'user', 'mechanical turk', 'a', 'dear user', 'me']:
                    result = ':'.join(parts[1:])
            if display_progress:
                print('=' * 80)
                print(result)
            return result
        else:
            print(f'ERROR: response.status_code is {response.status_code}')
