import os
import re
import requests

imdbID_pattern = re.compile(r'^tt\d+$', re.IGNORECASE)
season_episode_modecmds =\
'''
    Mode options:
    a* - All series' seasons
    e* - All season 1 episodes (if any)
    (m, #) - Specific season or episode
    c - Cancel
    (s, skip) - Default S1E1
'''
season_episode_cmds =\
'''
    Input options:
    # - Season or episode
    r - Redo
    c - Cancel
    (s, skip) - Default 1
'''

def re_dirname(filepath, n):
    path = os.path.dirname(filepath)
    n -= 1

    if n >= 1:
        return re_dirname(path, n)
    
    return path

def get_season_episode(season_cap=None):
        season_cap = int(season_cap) if season_cap and season_cap != 'N/A' else None

        def get_(specified_input=None, name=None):
            se_input = specified_input or input(f'Enter {name}: ').lower()

            if se_input == '?':
                print(season_episode_cmds)
                return get_(name=name)
            elif se_input == 'r':
                return se_input
            elif se_input == 's':
                return 1
            elif se_input == 'c':
                return None
            
            try:
                return int(se_input)
            except ValueError:
                print('Error: Invalid input')
                return get_(name=name)
            
        print('Enter ? for cmds')

        # Main
        while True:
            input_mode = input(f'Select mode: ').lower()

            def manual_input(entered_input=None):
                s = get_(specified_input=entered_input, name='Season')
                if not s: return
                elif s == 'r': return manual_input()

                if season_cap and s > season_cap:
                    print(f'\nNOTE - Input season "{s}" is higher than total seasons "{season_cap}"\nDefault: Latest season - "{season_cap}"\n')
                    s = season_cap          

                e = get_(name='Episode')
                if not e: return
                elif e == 'r': return manual_input()                   
            
                return {'s': s, 'e': e}

            if input_mode == '?':
                print(season_episode_modecmds)
                continue
            elif input_mode == 'a*':
                return True
            elif input_mode == 'e*':
                return {'s': 1}
            elif input_mode == 'm':
                return manual_input()
            elif input_mode == 's' or input_mode == 'skip':
                return {'s': 1, 'e': 1}
            elif input_mode == 'c':
                return
            
            #
            try:
                return manual_input(int(input_mode))
            except ValueError:
                print("Error: Invalid Input")

def msdb_user_confirm(text):
    while True:
        c = input(text).lower()

        if c == 'y':
            return True
        elif c == 'c' or c == 'n':
            return 
        else:
            print("Error: Invalid input")

def query(params:dict=None) -> dict:
    ''' Search omdb for movie/series entry with specified params

    :param apikey: apikey

    ONE REQUIRED
    :param s, t: title
    :param i: imdbID or eimdbID

    OPTIONAL
    :param Season: #
    :param Episode: #
    
    Example:
    >>> results = query(params={
            's', 't', or 'i': str,
            'Season': #,
            'Episode' #,
            'apikey': apikey
        })
    
    Example 1: Loki (2021) 'Season': 1, 'Episode': 1
    >>> {
        'Title': 'Glorious Purpose', 
        'Year': '2021', 
        'Rated': 'TV-14', 
        'Released': '09 Jun 2021', 
        'Season': '1', 
        'Episode': '1', 
        'Runtime': '51 min', 
        'Genre': 'Action, Adventure, Fantasy', 
        'Director': 'Kate Herron', 
        'Writer': 'Michael Waldron, Bisha K. Ali, Elissa Karasik', 
        'Actors': 'Tom Hiddleston, Owen Wilson, Gugu Mbatha-Raw', 
        'Plot': 'Loki, the God of Mischief, finds himself out of time and in an unusual place and forced - against his godly disposition - to cooperate with others.', 
        'Language': 'English', 
        'Country': 'United States', 
        'Awards': 'N/A', 
        'Poster': 'https://m.media-amazon.com/images/M/MV5BOTk0ZGFjYmItNjQzNC00OTBiLWI4ZDktY2I4YzQ2NDRhZmZlXkEyXkFqcGdeQXVyODIyOTEyMzY@._V1_SX300.jpg', 
        'Ratings': [{'Source': 'Internet Movie Database', 'Value': '8.6/10'}], 
        'Metascore': 'N/A', 
        'imdbRating': '8.6', 
        'imdbVotes': '30692', 
        'imdbID': 'tt10161330', 
        'seriesID': 'tt9140554', 
        'Type': 'episode', 
        'Response': 'True'
        }

    Examples 2: 's': 'Loki'
    >>> {
        'Title': 'Loki', 
        'Year': '2021–', 
        'imdbID': 'tt9140554', 
        'Type': 'series', 
        'Poster': 'https://m.media-amazon.com/images/M/MV5BYTY0YTgwZjUtYzJiNy00ZDQ2LWFlZmItZThhMjExMjI5YWQ2XkEyXkFqcGdeQXVyMTM1NjM2ODg1._V1_SX300.jpg'
        }

    Example 3: 't': 'Loki' or 'i': 'tt9140554' 
    >>> {
        'Title': 'Loki', 
        'Year': '2021–', 
        'Rated': 'TV-14', 
        'Released': '09 Jun 2021', 
        'Runtime': 'N/A', 
        'Genre': 'Action, Adventure, Fantasy', 
        'Director': 'N/A', 
        'Writer': 'Michael Waldron', 
        'Actors': 'Tom Hiddleston, Owen Wilson, Gugu Mbatha-Raw', 
        'Plot': 'The mercurial villain Loki resumes his role as the God of Mischief in a new series that takes place after the events of “Avengers: Endgame.”', 
        'Language': 'English', 
        'Country': 'United States', 
        'Awards': 'Nominated for 6 Primetime Emmys. 12 wins & 53 nominations total', 
        'Poster': 'https://m.media-amazon.com/images/M/MV5BYTY0YTgwZjUtYzJiNy00ZDQ2LWFlZmItZThhMjExMjI5YWQ2XkEyXkFqcGdeQXVyMTM1NjM2ODg1._V1_SX300.jpg', 
        'Ratings': [{'Source': 'Internet Movie Database', 'Value': '8.2/10'}], 
        'Metascore': 'N/A', 
        'imdbRating': '8.2', 
        'imdbVotes': '356,825', 
        'imdbID': 'tt9140554', 
        'Type': 'series', 
        'totalSeasons': '2', 
        'Response': 'True'
        }

    Example 4: 'Season': 1
    >>> {
        'Title': 'Loki', 
        'Season': '1', 
        'totalSeasons': '2', 
        'Episodes': [{'Title': 'Glorious Purpose', 'Released': '2021-06-09', 'Episode': '1', 'imdbRating': '8.6', 'imdbID': 'tt10161330'}, {'Title': 'The Variant', 'Released': '2021-06-16', 'Episode': '2', 'imdbRating': '8.7', 'imdbID': 'tt10161334'}, {'Title': 'Lamentis', 'Released': '2021-06-23', 'Episode': '3', 'imdbRating': '7.7', 'imdbID': 'tt10161336'}, {'Title': 'The Nexus Event', 'Released': '2021-06-30', 'Episode': '4', 'imdbRating': '9.0', 'imdbID': 'tt10161340'}, {'Title': 'Journey Into Mystery', 'Released': '2021-07-07', 'Episode': '5', 'imdbRating': '8.9', 'imdbID': 'tt10161338'}, {'Title': 'For All Time. Always.', 'Released': '2021-07-14', 'Episode': '6', 'imdbRating': '8.6', 'imdbID': 'tt10161342'}],
        'Response': 'True'
        }

    :rtype: dict    
    '''
    
    if not isinstance(params, dict):
        raise TypeError(f"Invalid arguements\nparams: {params}")
    
    if not params.get('apikey'):
        raise IndexError('Missing apikey')

    base_url = "https://www.omdbapi.com/"
    results = requests.get(base_url, params)
    results_json = None
    
    if results.status_code == 200:
        results_json = results.json()
        
        if results_json['Response'] == 'True':
            return results_json
        
    print(f'Failed to query\nResults: {results}\nJson: {results_json}')

def search_by_title(title=None, API_KEY=None):
    title = title or input("Enter movie/series (c to cancel): ")

    print(f"Attempting broad search for: {title}...")
    
    data_results = query({
        "s": title,
        "apikey": API_KEY
    })

    if not data_results:
        return
    
    print('\nResults:\n', '\n'.join([f"{i+1}. {v}" for i, v in enumerate(data_results['Search'])])+'\n')

    try:
        picked = input('Choose title by number (c to cancel): ')

        if picked.lower() == 'c':
            return
        
        picked = int(picked)

        if picked < 1 or picked > len(data_results['Search']):
            print("Error: Unable to find title")
        else:
            return data_results['Search'][picked-1]
    except (ValueError, IndexError):
        print("Error: Invalid choice")

def sqGet(title=None, API_KEY=None):
    ''' Uses both search and query methods to find movie/show '''

    title = title or input('Enter movie/show: ')

    # Exact match
    print(f"Attempting exact match search for: {title}...")

    # if ID
    if imdbID_pattern.match(title):
        title = title.lower()
        type = 'i'
    else:
        type = 't'

    ms = query({
        type: title,
        'apikey': API_KEY
    })

    if ms and msdb_user_confirm(f"Found: {[ms['Title'], ms.get('Released') or ms['Year'], 'https://www.imdb.com/title/' + ms['imdbID']]}\nIs this correct? Y/N: "):
        return ms
        
    # Broad search
    return search_by_title(title, API_KEY=API_KEY)
