import craftable_object
import json


def discover_objects(ai_provider, economy, required_objects, do_yield=False):
    pending = economy.get_undefined_objects(required_objects)
    
    with open('example_object.json', 'r') as infile:
        example_object = json.load(infile)
    
    for candidate_name in pending:
        print(f'Submitting query for {candidate_name} -- {pending[candidate_name]}')
        try:
            if craftable_object.is_object_acceptable(ai_provider, candidate_name, pending[candidate_name]):
                print(f'{candidate_name} deemed acceptable')
                new_object = craftable_object.get_object_request_query(ai_provider, candidate_name, pending[candidate_name], example_object)
                if economy.add_object(new_object):
                    print(f'Added {candidate_name}')
                    
                else:
                    print(f'Error adding {candidate_name}')
                if do_yield:
                    yield new_object
            else:
                print(f'{candidate_name} rejected')
                economy.ban_object_name(candidate_name)
        except RuntimeWarning as rw:
            print(rw)
