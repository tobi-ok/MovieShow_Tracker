import re, requests

imdbID_pattern = re.compile(r'^tt\d+$', re.IGNORECASE)

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
        'Episodes': [{'Title': 'Glorious Purpose', 'Released': '2021-06-09', 'Episode': '1', 'imdbRating': '8.6', 'imdbID': 'tt10161330'}, {'Title': 'The Variant', 'Released': '2021-06-16', 'Episode': '2', 'imdbRating': '8.7', 'imdbID': 'tt10161334'}, {'Title': 'Lamentis', 'Released': '2021-06-23', 'Episode': '3', 'imdbRating': '7.7', 'imdbID': 'tt10161336'}, {'Title': 'The Nexus Event', 'Released': '2021-06-30', 'Episode': '4', 'imdbRating': '9.0', 'imdbID': 'tt10161340'}, {'Title': 'Journey Into Mystery', 'Released': '2021-07-07', 'Episode': '5', 'imdbRating': '8.9', 'imdbID': 'tt10161338'}, {'Title': 'For All Time. Always.', 'Released': '2021-07-14', 'Episode': '6', 'imdbRating': '8.6', 'imdbID': 'tt10161342'}], 'Response': 'True'
        }

    :rtype: dict    
    '''

    if not isinstance(params, dict):
        raise TypeError(f"Error: Invalid arguements\nparams: {params}")

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
    return search_by_title(title)