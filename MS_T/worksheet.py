from .utils import (
    query,
    sqGet,
    msdb_user_confirm,
    imdbID_pattern,
    get_season_episode
)
from datetime import (date, datetime)

immutable_titles = [
    'imdbID',
    'Season',
    'Episode',
    'eimdbID'
]

class Worksheet:
    def __init__(self, spreadsheet, gspread_class, API_KEY=None) -> None:
        ''' Gspread 'worksheet' class extension

        More info: https://docs.gspread.org/en/latest/api/models/worksheet.html
        '''

        self.spreadsheet = spreadsheet
        self.g = gspread_class
        self.cache = []
        self.API_KEY = API_KEY

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            if hasattr(self.g, __name):
                return getattr(self.g, __name)
    
    @property
    def next_empty_row(self) -> int:
        row = 1

        col_values = self.col_values(1)

        for r in col_values:
            if r == '':
                return row
            row += 1

        # No empty rows found, return next row
        return row
    
    @property
    def values(self):
        return self.cache
    
    def update_to_row_titles(self):
        self.g.batch_clear(['A1:Z1'])
        self.g.update('A1:Z1', [self.spreadsheet.row_titles])      

    def find(self, **k):
        ''' Returns entry where found

        Example:
        >>> data = spreadsheet.worksheet.find(imdbID='tt0959621')
        >>> {
            'Title': "'Breaking Bad': S1E1 - Pilot",
            'Date': 'N/A',
            'imdbID': 'tt0903747',
            'Link': 'https://www.imdb.com/title/tt0959621/',
            'Type': 'movie',
            'Season': '1',
            'Episode': '1',
            'eimdbID': 'tt0959621',
            'Genre': 'Crime, Drama, Thriller'
        }

        :param k['param']: data 
        :param k['imdbID']: imdbID,
        :param k['eimdbID']: eimdbID

        :returns: entry data
        :rtype: dict
        '''    
        
        param = k.get('param')
        ID = None
        
        if param:
            ID = param['eimdbID'] if param.get('eimdbID') and param['eimdbID'] != 'N/A' else param.get('imdbID')

        if not ID:         
            ms = sqGet(API_KEY=self.API_KEY)

            if not ms: 
                return
                                    
            if ms['Type'] == 'series':
                se = get_season_episode(season_cap=ms.get('totalSeasons'))

                if not se:
                    return
                
                seInfo = query({
                    'i': ms['imdbID'],
                    'Season': se.get('s') if isinstance(se, dict) else None,
                    'Episode': se.get('e') if isinstance(se, dict) else None,
                    'apikey': self.API_KEY
                })

                if not seInfo:
                    return
                
                if isinstance(se, bool):
                    if not seInfo.get('totalSeasons') or seInfo['totalSeasons'] == 'N/A':
                        print("Error: Unable to get season data")
                        return
                    
                    seInfo['Episodes'] = []

                    for i in range(1, int(seInfo['totalSeasons'])+1):
                        season = query({
                            'i': ms['imdbID'],
                            'Season': i,
                            'apikey': self.API_KEY
                        })

                        if not season:
                            print(f"Failed to get data from season {i} of {ms['Title']}")
                            continue

                        for i in season['Episodes']:
                            seInfo['Episodes'].append(i)

                elif se.get('e'):
                    return self.find(param={
                        'imdbID': ms['imdbID'],
                        'eimdbID': seInfo['imdbID']
                    }, ignore=k.get('ignore'))

                if seInfo.get('Episodes'):
                    values = []

                    for i in seInfo['Episodes']:
                        values.append(
                            self.find(
                                    param={'imdbID': ms['imdbID'], 'eimdbID': i['imdbID']}, 
                                    ignore=k.get('ignore')
                                ) or None
                        )

                    return values
            else:
                if ms.get('seriesID'):
                    print('\nNOTE - Searching by episode imdbID unadvised (inconsistant/inaccurate omdb results)\n')

                    ms['eimdbID'] = ms['imdbID']
                    ms['imdbID'] = ms['seriesID']                  

                return self.find(param=ms, ignore=k.get('ignore'))
        elif (not k.get('ignore') or self.title not in k['ignore']) and len(self.cache) > 0:
            for i, v in enumerate(self.cache):
                if v['eimdbID'] == ID or v['imdbID'] == ID:
                    return i if k.get('index') else v
    
    def manual_find(self, **k):
        def get_row_input():
            while True:
                print("Select data type to search by")
                print('\n'.join([f'{i+1}. {v}' for i, v in enumerate(self.spreadsheet.row_titles)]))
                v = input("Selection (c to cancel): ")

                if v.lower() == 'c':
                    return

                try:
                    v = int(v)

                    if v < 1 or v > len(self.spreadsheet.row_titles):
                        print('Error: Invalid input')
                        continue
                    
                    return self.spreadsheet.row_titles[v-1]
                except:
                    for i in self.spreadsheet.row_titles:
                        if i.lower() == v.lower():
                            return i

                    print('Error: Invalid input')
                
        selected_type = k.get('selected_type', get_row_input())

        if not selected_type:
            return
                
        data_to_find = k.get('data_to_find', input('Input data to find: '))

        for data in self.cache:
            if data[selected_type] == data_to_find:
                return data
    
    def cache_append(self, **k):
        param = k.get('param')

        if not param:
            raise IndexError("Error: Missing param")
        
        new_param = {}
        
        # Update param with/without missing or extra data
        for t in self.spreadsheet.row_titles:
            new_param[t] = param.get(t) or 'N/A'
        
        if self.spreadsheet.get_dupes(param=new_param, ignore=k.get('ignore')):
            return       
        
        self.cache.append(new_param)
        return self.cache[-1]

    def add(self, **k) -> list|dict:
        ''' Adds or returns data of user entered movie/series 
        
        :param k['title']: Movie/Show title
        :param k['param']: MST Entry

        :returns: New entry data
        :rtype: dict
        '''

        ms = k.get('param') or sqGet(title=k.get('title'), API_KEY=self.API_KEY)

        if not ms:
            return
        
        param = {
                'Date': date.today().strftime("%A, %B %d, %Y"),
                'imdbID': ms['imdbID'],
                'Type': ms['Type'],
            }
                        
        if ms['Type'] == 'movie':
            param.update({
                'Title': ms['Title'],
                'Date': date.today().strftime("%A, %B %d, %Y"),
                'imdbID': ms['imdbID'],
                'Link': f"https://www.imdb.com/title/{ms['imdbID']}/",
                'Type': ms['Type'],
            })

            return self.cache_append(param=param)
        elif ms['Type'] == 'series':
            se = {'s': ms['Season'], 'e': ms.get('Episode')} if ms.get('Season') else get_season_episode(season_cap=ms.get('totalSeasons'))

            if not se:
                return
            
            seInfo = query({
                'i': ms['imdbID'],
                'Season': se.get('s') if isinstance(se, dict) else None,
                'Episode': se.get('e') if isinstance(se, dict) else None,
                'apikey': self.API_KEY
            })

            if not seInfo:
                return
                        
            def add_all_episodes(season, episodes):
                results = []

                for i in (episodes):
                    new_param = param.copy()
                    new_param.update({
                        'Title': f"'{ms['Title']}': S{season}E{i['Episode']} - {i['Title']}",
                        'Link': f"https://www.imdb.com/title/{i['imdbID']}/",
                        'Season': season,
                        'Episode': i['Episode'],
                        'eimdbID': i['imdbID']
                    })

                    r = self.cache_append(param=new_param)

                    if r:
                        results.append(r)

                if results:
                    return results
            
            if isinstance(se, bool):
                # Add all seasons
                if not seInfo.get('totalSeasons') or seInfo['totalSeasons'] == 'N/A':
                    print("Error: Unable to get season data")
                    return

                results = []

                for n in range(1, int(seInfo['totalSeasons'])+1):
                    episodes = []

                    season_data = query({
                        'i': ms['imdbID'],
                        'Season': n,
                        'apikey': self.API_KEY
                    })

                    if not season_data:
                        print(f"Failed to get data from season {n} of {ms['Title']}")
                        continue

                    for i in season_data['Episodes']:
                        episodes.append(i)

                    r = add_all_episodes(season=n, episodes=episodes)

                    if r:
                        results.append(r)

                return results            
            elif seInfo.get('Episodes'):
                # Add all episodes  
                return add_all_episodes(season=se['s'], episodes=seInfo['Episodes'])
            else:
                # Add single episode
                param.update({
                    'Title': f"'{ms['Title']}': S{se['s']}E{se['e']} - {seInfo['Title']}",
                    'Link': f"https://www.imdb.com/title/{seInfo['imdbID']}/",
                    'Season': se['s'],
                    'Episode': se['e'],
                    'eimdbID': seInfo['imdbID']
                })

                return self.cache_append(param=param)
        elif ms['Type'] == 'episode':
            seInfo = ms.copy()
            
            print('\nNOTE - Adding episode by imdbID unadvised (inconsistent/inaccurate omdb results)\n')

            if not seInfo.get('seriesID') or seInfo['seriesID'] == 'N/A':
                print('Error: Unable to get season data')
                return

            ms = query({
                'i': seInfo.get('seriesID'),
                'apikey': self.API_KEY
            })

            if not ms:
                return

            param.update({
                'Title': f"'{ms['Title']}': S{seInfo['Season']}E{seInfo['Episode']} - {seInfo['Title']}",
                'Link': f"https://www.imdb.com/title/{seInfo['imdbID']}/",
                'Type': 'series',
                'Season': seInfo['Season'],
                'Episode': seInfo['Episode'],
                'eimdbID': seInfo['imdbID']
            })

            return self.cache_append(param=param)
            
    def manual_add(self):
        entry = {}
        skip_options = {'s', 'skip', 'n/a'}
        immutable_titles_ = immutable_titles.copy()
        immutable_titles_.pop('eimdbID', None)
        
        def get_input(row_title):
            is_series = entry.get('Type') and entry['Type'] == 'series' and row_title == 'eimdbID'
            v = input(f'Enter "{row_title}" (c to cancel): ' if row_title in immutable_titles or is_series else f'Input "{row_title}" (s - skip, c to cancel): ')

            if v.lower() == 'c':
                return v.lower()
            
            if v == '' or v.lower() in skip_options:
                if row_title in immutable_titles or is_series:
                    print('Error: Cannot skip')
                    return get_input(row_title)
                else:
                    return 'N/A'
                
            if row_title == 'imdbID' or is_series:
                if not imdbID_pattern.match(v):
                    print(f'Error: Must input valid {row_title}\nFormat: tt + any # (ex. tt11743610)')
                    return get_input(row_title)
            elif row_title == 'eimdbID':
                if entry['imdbID'] == v:
                    print('Error: Episode ID must differ from series ID')
                    return get_input(row_title)             
            elif row_title == 'Type':
                v = v.lower()
            elif row_title == 'Season' or row_title == 'Episode':
                try:
                    v = int(v)
                except ValueError:
                    print("Error: Invalid input")
                    return get_input(row_title)
                
            return v
        
        for i in self.spreadsheet.row_titles:
            v = get_input(i)

            if v == 'c':
                return True

            if v:
                entry[i] = v

        if entry['Date'].lower() == 'today':
            entry['Date'] = date.today

        ms = None       

        if msdb_user_confirm('Search for entry? Y/N: '):
            ms = self.find(param=entry)
            
        return self.cache_append(param=ms or entry)
    
    def cache_remove(self, **k):
        param = k.get('param')

        if not param:
            raise IndexError("Error: Missing param")
        
        if not param.get('eimdbID') and not param.get('imdbID'):
            raise IndexError(f'Error: Unable to get ID\n{param}')
        
        i = self.find(param=param, index=True)

        if isinstance(i, int):
            return self.cache.pop(i)

    def remove(self, **k):
        ''' Remove entry from cache '''

        if not self.cache:
            print("No entries to remove!")
            return

        data = k.get(data) or self.find()

        if not data:
            print("Unable to find entry!")
            return
                
        if isinstance(data, list):
            if msdb_user_confirm(f"This will delete all episodes in the season\nAre you sure? Y/N: "):
                data_copy = list(data)

                for v in data:
                    if self.cache_remove(param=v):
                        data_copy.pop(0)

                return not data_copy
        else:
            if msdb_user_confirm(f"Removing: {data['Title']}\nAre you sure? Y/N: "):
                return self.cache_remove(param=data)

    def update(self, **k):
        data = k.get('param') or self.find()

        if not data:
            return
        
        def get_date():
            def validate(n):
                try:
                    return int(n)
                except ValueError:
                    print("Error: Invalid input")

            while True:
                c = input("Select date to modify (c to cancel)\nDay (d), Month (m), Year (y), All (a): ").lower()
                new_date = {}

                if c == 'd' or c == 'day':
                    i = validate(input('Input date - DD: '))

                    if i:
                        new_date['Day'] = i
                elif c == 'm' or c == 'month':
                    i = validate(input('Input month - MM: '))

                    if i:
                        new_date['Month'] = i
                elif c == 'y' or c == 'year':
                    i = validate(input('Input year - YYYY: '))

                    if i:
                        new_date['Year'] = i
                elif c == 'a' or c == 'all':
                    i = input('Input date - YYYY-MM-DD: ')

                    try:
                        # Parse the user's input into a datetime object
                        new_date = datetime.strptime(i, "%Y-%m-%d").strftime("%A, %B %d, %Y")
                    except ValueError:
                        print("Error: Invalid date format. Please use YYYY-MM-DD format.")
                elif c == 'c':
                    return
                else:
                    print("Error: Invalid input")

                if isinstance(new_date, dict):
                    try:
                        y, m, d = date.today().year, date.today().month, date.today().day
                        new_date = f"{new_date.get('Year', y)}-{new_date.get('Month', m)}-{new_date.get('Day', d)}"
                        new_date = datetime.strptime(new_date, "%Y-%m-%d").strftime("%A, %B %d, %Y")
                    except ValueError:
                        print("Error: Invalid date format. Please use YYYY-MM-DD format.")
                
                if not new_date:
                    continue
                
                return new_date
        
        def change_date(old_data, date=None):
            print(f"\nData to change: Date")    

            new_date = date or get_date()      

            if new_date:
                print(f"Changing date of: {old_data['Title']}\nTo: {new_date}")

                param = old_data.copy()
                param['Date'] = new_date

                if self.cache_remove(param=old_data):
                    return self.cache_append(param=param)        

        print('Choose data to edit')
        print('\n'.join([f'{v}' for v in self.spreadsheet.row_titles if v not in immutable_titles]))
        choice = input('Select option (c to cancel): ').lower()
        
        if choice == 'date':
            if isinstance(data, list):
                if msdb_user_confirm('This will affect all episodes in the season\nAre you sure? Y/N: '):
                    data_copy = list(data)
                    new_date = get_date()

                    for v in data:
                        if change_date(v, new_date):
                            data_copy.pop(0)
                        
                    return not data_copy
            else:
                return change_date(data)
        elif isinstance(data, dict):
            if choice == 'type':
                while True:
                    input_type = input('Enter type of entry (movie or series, c to cancel): ').lower()

                    if input_type == 'c':
                        return True

                    if input_type != 'movie' and input_type != 'series':
                        print("Error: Invalid input")

                    param = data.copy()
                    param['Type'] = input_type

                    if self.cache_remove(param=data):
                        return self.cache_append(param=param)
            else:
                new_input = input('Enter new data (c to cancel): ')

                if new_input.lower() == 'c':
                    return True

                param = data.copy()
                param[choice.capitalize()] = new_input

                if self.cache_remove(param=data):
                    return self.cache_append(param=param)

    def move(self, **k):
        data = k.get('param') or self.find()

        if not data:
            return
        
        print('\nEnter worksheet to move to')
        newwk = self.spreadsheet.get_worksheet_by_title(ignore=[self.title])

        if not newwk:
            return
        
        if isinstance(data, list):
            data_copy = list(data)

            for v in data:
                if self.cache_remove(param=v) and newwk.cache_append(param=v, ignore=[self.title]):
                    data_copy.pop(0)
                
            return not data_copy
        else:
            if self.cache_remove(param=data):
                return newwk.cache_append(param=data, ignore=[self.title])