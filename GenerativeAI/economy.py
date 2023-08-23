import copy
import json
import random
import schema


class Economy:
    def __init__(self, filename):
        self.economy = {'objects': {}}
        self.filename = filename
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as file:
                self.economy = json.load(file)
        except Exception as e:
            print(f'Caught exception: {e}')

    def save(self):
        print("Saving")
        with open(self.filename, 'w') as file:
            json.dump(self.economy, file, ensure_ascii=False, indent=2, sort_keys=True)

    def add_object(self, obj):
        if schema.validate('object_definition', obj):
            self.economy['objects'][obj['name'].lower()] = obj
            return True
        return False

    def get_object(self, name):
        key = name.lower()
        return self.economy['objects'][key] if 'objects' in self.economy and key in self.economy['objects'] else None
            
    def get_undefined_objects(self, required_objects):
        object_names_found = set()
        accessories_found = copy.copy(required_objects)

        for object_name, object_details in self.economy['objects'].items():
            object_names_found.add(object_name.lower())
            for accessory in object_details['related objects']:
                accessory_name = accessory['name'].lower()
                # if '(' not in object_name and ')' not in object_name:
                #     accessories_found[f'{accessory_name} ({object_name})'] = accessory['description'].lower()
                accessories_found[accessory_name] = None

        pending = {}
        for name, description in accessories_found.items():
            if name not in object_names_found and name not in pending:
                print(f'Queuing {name} ({description})')
                pending[name] = description 
     
        return pending

    def get_random_objects(self, num_samples):
        items = self.economy['objects']
        keys = random.sample(list(items.keys()), min(len(items), num_samples))
        return {key: items[key] for key in keys}

        