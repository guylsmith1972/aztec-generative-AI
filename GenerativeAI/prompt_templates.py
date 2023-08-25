import copy
import utility


loaded_templates = {}


def get(template_name, replacements):
    if template_name not in loaded_templates:
        with open(f'prompt_templates/{template_name}.txt', 'r') as infile:
            loaded_templates[template_name] = infile.read()
   
    body = copy.copy(loaded_templates[template_name])
    for target, replacement in replacements.items():
        body = body.replace(target, '' if replacement is None else replacement)
        
    return body


def execute(ai_provider, template_name, replacements):
    prompt = get(template_name, replacements)
    result = ai_provider.query(prompt, display_progress=False)

    if result is None:
        return None

    return utility.extract_json(result.lower())
    
    
