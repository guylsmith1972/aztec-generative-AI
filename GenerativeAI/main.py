from economy import Economy
from oobabooga_api import OobaboogaAPI
from openai_api import OpenAIAPI
import researcher


required_objects = {
    "axe": None,
    "chisel": None,
    "helmet": None,
    "loom": None,
    "pickaxe": None,
    "anvil": None,
    "sword": None
}


def discover_objects(economy, iteration):
    print('=' * 80 + ' ' + str(iteration))
    count = 0
    for _ in researcher.discover_objects(OobaboogaAPI, economy, required_objects, do_yield=True):
        count += 1
        if count == 1:
            economy.save()
            count = 0
    economy.save()


def main():
    economy = Economy('economy.json')

    # selected_objects = economy.get_random_objects(10)
    # pruned = {}
    # for name, details in selected_objects.items():
    #     related_objects = [x['name'] for x in details['related objects']]
    #     pruned[name] = ', '.join(related_objects)

    # print(pruned)

    for i in range(1, 100):
        discover_objects(economy, i)


if __name__ == '__main__':
    main()
