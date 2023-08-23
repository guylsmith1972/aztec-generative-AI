from doctest import Example
import json

import openai
import oobabooga_api
import openai_api
import query_templates
import re
import utility


# def generate_json_list(prompt = None, result = None):
#     if result is None and prompt is None:
#         raise RuntimeError('prompt and result are both None in generate_json_list -- one must be set')
#     if result is not None and prompt is not None:
#         raise RuntimeError('prompt and result are both set in generate_json_list -- only one is allowed to be set')
    
#     if result is None:
#         result = oobabooga_api.run(prompt)
#     if result is None:
#         raise RuntimeError(f'failed to retrieve result for {prompt}')
    
#     result = oobabooga_api.run(f'Convert the following listed items into a JSON array of strings. The array elements should consist of single strings only. Do not include indices.\n{result}\n')
#     as_list = None if result is None else utility.extract_json(result)
#     return as_list if isinstance(as_list, list) else None


# def deduplicate(original):
#     listed = ', '.join([f'"{x}"' for x in original])    
#     result = oobabooga_api.run(f'Create a shorter list from the following items by discarding one item that is similar to other items in the list. If no items are similar, return the same list: {listed}')
#     as_json =  generate_json_list(result=result)
#     return original if as_json is None else set(as_json)


# def get_sentiment(statement):
#     return oobabooga_api.run(f'Respond with "yes" if the following statement is in the affirmative, and respond with "No" otherwise. Do not respond with anything else. STATEMENT: {statement}')


# def check_if_duplicate(candidate, existing_items):
#     for item in existing_items:
#         if candidate.lower() == item.lower():
#             return True
#         result = oobabooga_api.run(f'Is "{candidate}" another way of saying "{item}"?')
#         if result.lower().startswith('yes'):
#             return True
#     return False


# def check_if_duplicate_fast(candidate, existing_items):
#     listed = '\n'.join([f'"{x}"' for x in existing_items])
#     result = oobabooga_api.run(f'Is "{candidate}" another way of saying any of the following:\n{listed}')
#     return result.lower().startswith('yes') 


# def simplify_wording(items):
#     listed = '\n'.join([f'"{x}"' for x in items])
#     # TODO: The following query isn't doing anything. Improve it so it works.
#     result = oobabooga_api.run(f'Please simplify the wording of the following statements, reducing detail if possible:\n{listed}')
#     return generate_json_list(result=result)


# def extract_items_with_prefix(prefix, source):
#     results = []
#     for item in source:
#         if item.startswith(prefix):
#             results.append(item[len(prefix):])
#     return results


# def pluralize_set(original):
#     listed = ', '.join([f'"{x}"' for x in original])
#     result = oobabooga_api.run(f'What are the plural forms of each of the following strings: {listed}\n')
#     as_json = generate_json_list(result=result)
#     return original if as_json is None else set([x.lower() for x in as_json])


# def research_tools(economy, where):
#     for entry in economy['tasks']:
#         parts = entry.split(':')
#         profession = parts[0]
#         task = parts[1]
#         result = generate_json_list(prompt=f'Create a list of specific tools needed for {profession} in {where} to perform the following task: {task}. Only provide the tool names. Do not describe the tools.')
#         if result is None:
#             return
#         for tool in result:
#             parts = re.split(r' and | or |/', tool)
#             for part in parts:
#                 economy['tools'].add(f'{profession}:{part}'.lower())

 
# def research_tasks(economy, where):
#     for profession in economy['professions']:
#         result = generate_json_list(prompt=f'List some important tasks {profession} in {where} would perform in their line of work.\n')
#         if result is None:
#             return
        
#         for i in result:
#             if not check_if_duplicate(i, extract_items_with_prefix(profession + ':', economy['tasks'])):
#                 economy['tasks'].add(f'{profession}:{i}'.lower())


# def research_professions(economy, where):
#     for entry in economy['tools']:
#         try:
#             parts = entry.split(':')
#             profession = parts[0]
#             tool = parts[1]
#             result = oobabooga_api.run(f'In {where}, what kind of professional would create the tool "{tool}" as used by {profession}?')
#             if result is None:
#                 return
#             result = oobabooga_api.run(f'List the professions that are mentioned in the following text as a JSON array of strings containing just the names of the professions\n'
#                                        f'TEXT: "{result.strip()}"\n\n')
#             result = utility.extract_json(result)
#             if result is None:
#                 return
#             if isinstance(result, list):
#                 for element in result:
#                     print(f'New profession: {element}')
#                     economy['professions'].add(element.lower())
#             else:
#                 print(f'Failed to get a list: {result}')
#         except Exception as e:
#             print(f'Exception caught handling {entry} -- {e}')

    
# def research_economy(economy, where):
#     research_tasks(economy, where)
#     yield None
#     research_tools(economy, where)
#     yield None
#     research_professions(economy, where)
#     economy['professions'] = pluralize_set(economy['professions'])
#     yield None


def discover_objects(ai_provider, economy, required_objects, do_yield=False):
    pending = economy.get_undefined_objects(required_objects)
    
    with open('example_object.json', 'r') as infile:
        example_object = json.load(infile)
    
    for candidate_name in pending:
        print(f'Submitting query for {candidate_name} -- {pending[candidate_name]}')
        new_object = query_templates.get_object_request_query(ai_provider, candidate_name, pending[candidate_name], example_object)
        if economy.add_object(new_object):
            print(f'Added {candidate_name}')
        else:
            print(f'Error adding {candidate_name}')

        if do_yield:
            yield new_object
