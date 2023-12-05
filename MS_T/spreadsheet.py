from .auth import (
    authorize,
    get_worksheetID,
    unique_sheetname,
    save_worksheetID
)
from .worksheet import Worksheet
import csv, os

EXPORT_TITLE = 'Movie/Show Tracker Exports'
MAX_ENTRIES_PER_ROW = 15
MAX_SHEET_ROWS = 50000
cell_titlerow_format = {
    'backgroundColor': {
        'red': 249/255,
        'green': 203/255,
        'blue': 156/255
    },
    'horizontalAlignment': 'CENTER',
    'textFormat': {
        'bold': True
    }
}

class Spreadsheet:
    def __init__(self, client=None, spreadsheet=None, API_KEY=None) -> None:
        ''' Contains gspread spreadsheet class for msdb methods

        More info: https://docs.gspread.org/en/latest/api/models/spreadsheet.html
        '''

        self.client = client or authorize()
        self.sheetID = get_worksheetID()
        self.g = spreadsheet or None
        self.API_KEY = API_KEY
        
        if not self.g:
            if self.sheetID:
                self.g = self.client.open_by_key(self.sheetID)
            else:
                self.g = self.new_spreadsheet()

                save_worksheetID(self.g.id)         

        self.worksheets = [Worksheet(self, self.g.worksheet(title=i.title), API_KEY=self.API_KEY) for i in self.g.worksheets()]
        self.load()

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            if hasattr(self.g, __name):
                return getattr(self.g, __name)

    @property
    def row_titles(self):
        return [
            'Title',
            'Date',
            'imdbID',
            'Link',
            'Type',
            'Season',
            'Episode',
            'eimdbID',
            'Genre',
        ]

    @property
    def all_values(self):
        return {i.title: i.cache for i in self.worksheets}
        
    def new_spreadsheet(self):
        title = f'Movie/Show Tracker - {unique_sheetname()}'

        created_spreadsheet = self.client.create(title=title)

        def format_wk(worksheet):
            worksheet.format('A1:Z1', cell_titlerow_format)
            worksheet.freeze(rows=1)

        def new_wk(title):
            worksheet = created_spreadsheet.add_worksheet(title=title, cols=15, rows=MAX_SHEET_ROWS)
            format_wk(worksheet)

        s1 = created_spreadsheet.sheet1
        s1.add_rows(MAX_SHEET_ROWS-s1.row_count)
        s1.update_title('Planned')
        format_wk(s1)

        new_wk('Available')
        new_wk('Watched')
        new_wk('Canceled')

        return created_spreadsheet

    def worksheet(self, title):
        for i in self.worksheets:
            if i.title == title:
                return i
    
    def get_worksheet_by_title(self, title=None, ignore=[]):
        selected = None
        sheet_names = [i.title for i in self.worksheets if i.title not in ignore]

        while not selected:
            selected = title or input(f"Worksheets: {sheet_names}\nSelect Worksheet (c to cancel): ")

            if selected.lower() == 'c':
                return

            # Get worksheet by title or index
            if not isinstance(selected, str) or selected.capitalize() not in sheet_names:
                selected = None
                print("\nError: Unable to find worksheet\n")

            title = None

        return self.worksheet(selected.capitalize())

    def get_dupes(self, **k):
        ''' 
        Checks all worksheets for duplicate entry input and returns results

        Example (if found):
        >>> dupe = spreadsheet.get_dupes({title='Barbie'})
        >>> print(dupe)
        >>> [{
            'Title': 'Barbie',
            'Date': 'N/A',
            'imdbID': 'tt1517268',
            'Link': 'https://www.imdb.com/title/tt1517268/',
            'Type': 'movie',
            'Season': 'N/A',
            'Episode': 'N/A'
            'eimdbID': 'N/A'
            'Genre': 'Adventure, Comedy, Fantasy'
        }, etc.]

        :param k[msID/eID]: imdbID
        :param k[title]: title
        :param k[ignore]: sheet_title or [sheet_titles]
        
        :return: Entry or entries where found
        :rtype: dict
        '''

        param = k.get('param')

        if not param:
            raise IndexError(f"Error: Missing param")

        title = param.get('Title')
        ID = param['eimdbID'] if param.get('eimdbID') and param['eimdbID'] != 'N/A' else param.get('imdbID')

        if not title or not ID:
            raise IndexError(
                f"Error: Missing args - Title: {title}, eimdbID: {param.get('eimdbID')}, imdbID: {param.get('imdbID')}")

        results = []
        for i in self.worksheets:
            k['sheet'] = i.title
            data = i.find(**k)

            if data:
                if not k.get('noprint'):
                    print(f'"{data["Title"]}" in worksheet "{i.title}"\nData: {data}')
                results.append(data)

        if results:
            return results
        
    def count_data(self):
        m = input("Count all worksheets? Y/N: ")
        a = 0

        if m.lower() == 'y':
            for i in self.c:
                a += len(i)
        else:
            wk = self.get_worksheet_by_title()

            if wk:
                a += len(i.cache)

        return a

    def clear_all_data(self):
        if input("Are you sure? Y/N: ").lower() == 'y':
            for i in self.worksheets:
                i.cache = []

        return True

    def load(self):
        ''' Extracts google sheet data to local cache '''

        print('Loading data...')

        failed = {}

        for sheet in self.worksheets:
            values = sheet.get_all_values()

            if len(values) <= 1:
                if not values or values[0] != self.row_titles:
                    sheet.update_to_row_titles()

                continue

            row_titles = [i for i in values[0] if i != '']
            failed[sheet.title] = []

            for row in values:                
                if row == row_titles:
                    continue

                row_data = {row_titles[i]: v for i, v in enumerate(row) if v != '' and i < len(row_titles)}

                if not sheet.cache_append(param=row_data):
                    failed[sheet.title].append(row_data['Title'])

            sheet.update_to_row_titles()

            if failed[sheet.title]:
                print(f'Failed to load data to "{sheet.title}" worksheet:\n{failed[sheet.title]}')

        results = not [i for sheet in failed.values() for i in sheet]
        
        if results:
            print('Data loaded!')

    def save(self):
        ''' Updates google spreadsheet values with local data '''
        
        for sheet in self.worksheets:
            vlen = len(sheet.col_values(1))

            if vlen > 1:
                sheet.batch_clear([f'A{2}:Z{vlen+1}'])

            if len(sheet.cache) > 0:
                entries = []

                for v in sheet.cache:
                    sorted_entry = [v[i] for i in self.row_titles if v.get(i)]
                    entries.append(sorted_entry)

                sheet.batch_update([{'range': f'A2:Z{len(sheet.cache)+1}', 'values': entries}])

        return True

    def import_(self, wk):
        if not wk:
            return

        file_path = input('Input file path: ')

        if not os.path.exists(file_path):
            print("Error: Failed to find path")
            return
        
        imported, failed = [], []

        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            total = len([entry for row in csv_reader for entry in row if entry != ''])
            accum = 1

            # Reset file pointer to first line
            file.seek(0)

            for row in csv_reader:
                for entry in row:
                    if entry == '':
                        continue

                    print(
                        f"\nImporting: {entry}\n{accum} out of {total} {'- Failed ' + str(len(failed)) if len(failed) >= 1 else ''}")

                    r = wk.add(title=entry)

                    if not r:
                        failed.append(entry)
                    else:
                        imported.append(r)

                    accum += 1

        print(f"\nImported {len(imported)} out of {total} " +
              f"{'- Failed: ' + str(len(failed)) if failed else ''} {failed if failed else ''}")
        
        return not failed

    def export_(self):
        if not os.path.exists(EXPORT_TITLE):
            os.makedirs(EXPORT_TITLE)

        for sheet, list in self.worksheets():
            if len(list) < 1:
                continue

            with open(f'{EXPORT_TITLE}/{sheet}.csv', 'w') as file:
                csv_writer = csv.writer(file)

                for i in range(0, len(list), MAX_ENTRIES_PER_ROW):
                    row = list[i:i+MAX_ENTRIES_PER_ROW]
                    csv_writer.writerow(row)

        return True