import json
from unittest import result
import prompt_templates
import re
import schema
import utility


def extract_object_references(obj):
    # "tools needed"
    tools = obj.get("assembly", {}).get("tools needed", {})
    result = {k.strip(): v.strip() for k, v in tools.items()}
    
    # "pieces needed"
    pieces = obj.get("assembly", {}).get("pieces needed", {})
    print(pieces)
    result.update({f'{k.strip()} of a {obj["name"].strip()}': v["description"] for k, v in pieces.items() if v["type"] == "component"})
    
    # "related objects"
    related_objects = obj.get("related objects", {})
    result.update({k.strip(): v.strip() for k, v in related_objects.items()})
    
    # "variants"
    variants = obj.get("variants", {})
    result.update({k.strip(): v.strip() for k, v in variants.items()})
    
    return result


def validate(obj):
    return schema.validate('object_definition', obj)


def correct_name_and_description(name, description):
    corrected_name = name.split('(')[0].strip()
    expanded_description = '' if description is None else f' ({description.rstrip(".")})'
    return corrected_name.lower(), expanded_description.lower()


def is_object_a_piece(ai_provider, object_name, object_description, parent_object_name):
    def query(name, description, parent_name):
        corrected_name, expanded_description = correct_name_and_description(name, description)
        return f'REQUEST: Is a/an {corrected_name}{expanded_description} a physical object that is crafted as a piece to be joined to a/an {parent_name} during the assembly of the {parent_name}? Answer with "Yes." or "No."'

    prompt = f'{query("Face", "The flat top surface of the anvil where metal is struck.", "Anvil")}\n' \
        f'{ai_provider.get_response_prompt()}\n' \
        'No. It is not created separately and added to the anvil. It is just a name for the top side of the anvil.' \
        f'{query("Shell", "the hard, outer layer designed to disperse impact forces and protect the head from direct trauma", "Helmet")}\n' \
        f'{ai_provider.get_response_prompt()}\n' \
        'Yes. The shell is the main piece of the helmet.' \
        f'{query("String", "The cord or wire used to draw the bow and shoot the arrow.", "Anvil")}\n' \
        f'{ai_provider.get_response_prompt()}\n' \
        'No. A string is not a piece of an anvil.' \
        f'{query("String", "The cord or wire used to draw the bow and shoot the arrow.", "Longbow")}\n' \
        f'{ai_provider.get_response_prompt()}\n' \
        'Yes. A string is crafted separately and then joined to the longbow.'\
        f'{query("Arrow", "a slender, pointed projectile that is shot from a bow and typically made up of a shaft with feathered vanes at one end and a pointed head at the other", "Longbow")}\n' \
        f'{ai_provider.get_response_prompt()}\n' \
        'No. An arrow is used in conjuction with a longbow, but it is not a permanent part of the longbow itself.'\
        f'{query(object_name, object_description, parent_object_name)}\n'

    result = ai_provider.query(prompt)
    print(f'Result for {parent_object_name}:{object_name} is {result}')
    if result.startswith('Yes.') or result.startswith('Yes,'):
        return True
    if result.startswith('No.') or result.startswith('No,'):
        return False;
    raise RuntimeWarning(f'Bad response to query: {result}')


def are_objects_pieces(ai_provider, pieces, object_name):
    axe_input = {
	    "blade": "a sharpened piece of material (usually metal) designed for cutting or piercing",
	    "handle": "the part by which a tool or weapon is held and manipulated",
	    "hilt": "the protective guard at the base of a blade",
	    "pommel": "the weighted knob at the end of the handle of a weapon or tool"
    }
    axe_output = {
        "blade": "component",
        "handle": "component",
        "hilt": "name",
        "pommel": "modification"
    }
    
    def query(in_pieces, name, out_pieces):
        result = f'Input: Are the following objects manufactured components of a {name}, names for parts of a {name}, or modifications of a {name}?\n\n{json.dumps(in_pieces, indent=4)}'
        if out_pieces is not None:
            result += f'{ai_provider.get_response_prompt()}\n{json.dumps(out_pieces, indent=4)}\n\n'
        return result

    prompt = query(axe_input, 'axe', axe_output) + query(pieces, object_name, None)
    result = ai_provider.query(prompt)
    print(f'Result for {object_name}:{json.dumps(pieces, indent=4)} is {result}')
    return result


def is_object_acceptable(ai_provider, object_name, object_description):
    def query(name, description):
        corrected_name, expanded_description = correct_name_and_description(name, description)
        return f'REQUEST: Is a/an {corrected_name}{expanded_description} something that existed in medieval Europe? Answer with "Yes." or "No." and no other text.'

    prompt = f'{query("vacuum cleaner", "a device that uses suction to remove dirt and debris from floors, upholstery, and other surfaces")}\n'\
        f'{ai_provider.get_response_prompt()}\n' \
        'No.'\
        f'{query("chisel", "a tool with a curved blade and short handle for carving and shaping wood")}\n' \
        f'{ai_provider.get_response_prompt()}\n' \
        'Yes.'\
        f'{query(object_name, object_description)}\n'
    
    result = ai_provider.query(prompt)
    if result.startswith('Yes.') or result.startswith('Yes,'):
        return True
    if result.startswith('No.') or result.startswith('No,'):
        return False;
    raise RuntimeWarning(f'Bad response to query: {result}')


def verify_name(object_json, expected_name):
    if object_json['name'] != expected_name:
        parts = expected_name.split(' of a ')
        if len(parts) > 1:
            swapped_name = parts[1].strip() + ' ' + parts[0].strip()
            if object_json['name'] == swapped_name:
                return True
        print(f'Received unexpected name {object_json["name"]} when asking for a {expected_name}')
        return False
    return True


def get_validated_object(ai_provider, object_json, expected_name):
    if not validate(object_json):
        return None
    
    if not verify_name(object_json, expected_name):
        return None

    return object_json


def get_answer_from_map(ai_provider, template_name, replacements, allowed_answers):
    response = prompt_templates.execute_raw(ai_provider, template_name, replacements)
    first_word = re.split('[\s,.]', response.lower().strip())[0]
    if first_word not in allowed_answers:
        raise RuntimeWarning(f'{first_word} does not start with an allowed answer -- {response}')
    return allowed_answers[first_word]
    

def get_object_request_query(ai_provider, object_name, object_description, example_object):
    name_parts = object_name.split(' of a ')
    replacements = {
        "***RESPONSE-INDICATOR***": ai_provider.get_response_prompt(),
        "***OBJECT-NAME***": object_name,
        "***OBJECT-DESCRIPTION***": object_description,
        "***PART-NAME***": name_parts[0],
        "***PARENT-NAME***": name_parts[1] if len(name_parts) > 1 else None
        }
    
    result = prompt_templates.execute(ai_provider, 'generate_craftable_object', replacements)
    if result is None:
        return None
    
    if len(name_parts) > 1:
        construction_method = 'direct'
        pieces = prompt_templates.execute(ai_provider, 'confirm_construction_of_a', replacements)
    else:
        construction_method = get_answer_from_map(ai_provider, 'get_construction_method', replacements, {'assembled': 'assembled', 'direct': 'direct'})
    
        if construction_method == 'assembled':
            pieces = prompt_templates.execute(ai_provider, 'generate_object_parts', replacements)
        elif construction_method == 'direct':
            pieces = prompt_templates.execute(ai_provider, 'generate_object_materials', replacements)

    if pieces is None:
        return None    
    
    result['construction method'] = construction_method
    result['assembly'] = {"pieces needed": pieces}

    tools = prompt_templates.execute(ai_provider, 'generate_tools_needed', replacements)
    if tools is None:
        return None
    
    result['assembly']['tools needed'] = tools

    return get_validated_object(ai_provider, result, object_name)
