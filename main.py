import MS_T
import os
from dotenv import load_dotenv

API_KEY = 'YOUR_OMDB_API_KEY'
env_path = os.path.join(os.getcwd(), '.env')

if API_KEY == 'YOUR_OMDB_API_KEY' and os.path.exists(env_path):
    load_dotenv(env_path)
    API_KEY = os.getenv('APIKEY')

if API_KEY is None:
    raise ValueError('Unable to find APIKEY')

spreadsheet = MS_T.Spreadsheet(API_KEY=API_KEY)
MENU_OPTIONS = {
    ('help', '?'): {
        'desc': 'Show commands'
    },
    ('title'): {
        'desc': 'Get spreadsheet title',
        'func': lambda **k: print(spreadsheet.title)
    },
    ('url'): {
        'desc': 'Get spreadsheet url',
        'func': lambda **k: print(spreadsheet.url)
    },
    ('id'): {
        'desc': 'Get spreadsheet id',
        'func': lambda **k: print(spreadsheet.id)
    },
    ('ca', 'clear all'): {
        'desc': "Clears all data",
        'func': lambda **k: spreadsheet.clear_all_data()
    },
    ('i', 'import'): {
        'desc': 'Import file to update',
        'func': lambda **k: spreadsheet.import_(spreadsheet.get_worksheet_by_title())
    },
    ('e', 'export'): {
        'desc': 'Export data to file',
        'func': lambda **k: spreadsheet.export_()
    },
    ('count'): {
        'desc': 'Count total of entries in cache',
        'func': lambda **k: print(spreadsheet.count_data())
    },
    ('s', 'search'): {
        'desc': 'Search for movie/show',
        'func': lambda **k: print(MS_T.utils.sqGet(API_KEY=API_KEY))
    },
    ('f', 'find'): {
        'desc': 'Find entry',
        'func': lambda **k: print(k['execute_on_worksheet']('find'))
    },
    ('mf'): {
        'desc': 'Find entry without querying',
        'func': lambda **k: print(k['execute_on_worksheet']('manual_find'))
    },
    ('a', 'add'): {        
        'desc': 'Add entry',
        'func': lambda **k: k['execute_on_worksheet']('add')
    },
    ('ma'): {
        'desc': 'Manually add entry',
        'func': lambda **k: k['execute_on_worksheet']('manual_add')
    },
    ('r', 'remove'): {
        'desc': 'Remove entry',
        'func': lambda **k: k['execute_on_worksheet']('remove')
    },
    ('u', 'upd', 'update'): {
        'desc': 'Update entry',
        'func': lambda **k: k['execute_on_worksheet']('update')
    },
    ('m', 'move'): {
        'desc': 'Move entry',
        'func': lambda **k: k['execute_on_worksheet']('move')
    },
    ('load'): {
        'desc': 'Retrieve database data to cache',
        'func': lambda **k: spreadsheet.load()
    },
    ('save'): {
        'desc': 'Send cache to database',
        'func': lambda **k: spreadsheet.save()
    },
    ('av', 'all values'): {
        'desc': 'Get all values in the spreadsheet',
        'func': lambda **k: print(spreadsheet.all_values)
    },
    ('sv', 'sheet values'): {
        'desc': 'Get all values in a worksheet',
        'func': lambda **k: print(k['execute_on_worksheet']('values'))
    }
}

MS_T.auth.API_KEY = API_KEY

def display_commands():
    print('\nList of commands:\n' + '\n'.join([f'{i+1}. {v} - {MENU_OPTIONS[v]["desc"]}' for i, v in enumerate(MENU_OPTIONS)]) + '\n')

def execute(attr):
    if callable(attr):
        results = attr()

        if not results:
            print('Error: Unable to execute command')

        return results
    else:
        return attr

def execute_on_worksheet(__name):
    worksheet = spreadsheet.get_worksheet_by_title()
    if worksheet:
        attr = getattr(worksheet, __name)
        return execute(attr)
    
def main():
    while True:
        input_choice = input("\nMovie/Series Database\n\nEnter 'help' for all commands.\nEnter Command: ")

        if not any(input_choice in sublist for sublist in MENU_OPTIONS):
            print("\nError: Invalid input\n")
            continue

        if input_choice.lower() in [i for i in MENU_OPTIONS][0]:
            display_commands()
        else:
            option = None

            for i, v in MENU_OPTIONS.items():
                if isinstance(i, str):
                    if input_choice == i:
                        option = v
                        break
                else:
                    for x in i:
                        if input_choice == x:
                            option = v
                            break
                    
            if not option:
                print("Error: Failed to get command")
                continue

            print(f"\n~ {option['desc']} ~")

            if option.get('func') and option['func'](execute_on_worksheet=execute_on_worksheet):
                print("Success!")
    
if __name__ == '__main__':
    main()