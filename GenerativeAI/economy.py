import copy
import craftable_object
import json
import random


class Economy:
    def __init__(self, filename):
        self.economy = {'objects': {}, 'banned': []}
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
        if craftable_object.validate(obj):
            self.economy['objects'][obj['name']] = obj
            return True
        return False

    def get_object(self, name):
        key = name
        return self.economy['objects'][key] if 'objects' in self.economy and key in self.economy['objects'] else None
    
    def ban_object_name(self, name):
        if name in self.economy['banned']:
            return
        self.economy['banned'].append(name)
     
    def is_banned(self, name):
        return name in self.economy['banned']
    
    def get_undefined_objects(self, required_objects):
        object_names_found = set()
        accessories_found = copy.copy(required_objects)

        for object_name, object_details in self.economy['objects'].items():
            object_names_found.add(object_name)
            for accessory_name, accessory_details in craftable_object.extract_object_references(object_details).items():
                if self.is_banned(accessory_name):
                    continue
                parts = accessory_name.split(' of a ')
                if len(parts) > 2:
                    continue
                
                accessories_found[accessory_name] = accessory_details

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

        