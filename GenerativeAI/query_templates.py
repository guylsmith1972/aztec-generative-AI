import json
import utility


# REQUEST: Create a JSON object that describes a/an weaving bench (a wooden machine used for weaving textiles) in detail.
#  It should contain information about who would use the weaving bench, who would make it, the main parts and materials it's made from,
#  and any other items that might be used in conjuction with it.
#  Consider these elements in the context of 15th-century Europe, but refrain from mentioning 15th-century Europe specifically.


def get_object_request_query(ai_provider, object_name, object_description, example_object):
    def query(name, description):
        corrected_name = name.split('(')[0].strip()
        expanded_description = '' if description is None else f' ({description.rstrip(".")})'
        return f"REQUEST: Create a JSON object that describes a/an {corrected_name}{expanded_description} as it existed in 15th-century Europe. " \
            f"It should contain information about who would use the {corrected_name}, who would make it, the materials it's made from, " \
            "and any other items that might be used in conjuction with it or produced with it. " \
            "Consider these elements in the context of 15th-century Europe, but refrain from mentioning 15th-century Europe specifically.\n"
    

    prompt = f'{query(example_object["name"].lower(), example_object["description"].lower())}\n' \
        f'{ai_provider.get_response_prompt()}:\n' \
        f'{json.dumps(example_object, indent=2)}\n\n' \
        f'{query(object_name, object_description)}\n'

    result = ai_provider.query(prompt)
    return None if result is None else utility.extract_json(result)
