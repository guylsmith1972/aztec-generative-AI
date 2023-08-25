import json
import jsonschema


loaded_schemata = {}


def get_schema(schema_name):
    if schema_name in loaded_schemata:
        return loaded_schemata[schema_name]
    
    with open(f'schemata/{schema_name}.json', 'r') as infile:
        schema = json.load(infile)
        loaded_schemata[schema_name] = schema
        return schema
    

def validate(schema_name, object_to_validate):
    try:
        jsonschema.validate(instance=object_to_validate, schema=get_schema(schema_name))
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation error: {e.message}")
        print(json.dumps(object_to_validate, indent=4))
        return False