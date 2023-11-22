import unittest
import MS_T
import gspread
import os, json
from dotenv import load_dotenv

load_dotenv()

TEST_API_KEY = os.getenv('TEST_API_KEY')
TEST_SHEET_ID = os.getenv('TEST_SHEET_ID')
TEST_CREDENTIALS = json.loads(os.getenv('TEST_CREDENTIALS'))

client = gspread.service_account_from_dict(TEST_CREDENTIALS)
ss = MS_T.spreadsheet.Spreadsheet(client=client, spreadsheet=client.open_by_key(TEST_SHEET_ID), API_KEY=TEST_API_KEY)

test_param = {
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

class test_worksheet(unittest.TestCase):
    def test_sqGet(self):
        self.assertTrue(MS_T.utils.query({
            'i': test_param['imdbID'], 
            'apikey': TEST_API_KEY
            }))

    def test_add(self):
        sheet = ss.get_worksheet_by_title('Planned')

        p = sheet.add(param=test_param)

        self.assertEquals(p, test_param)

    def test_get_cache(self):
        sheet = ss.get_worksheet_by_title('Planned')

        sheet.add(param=test_param)

        self.assertTrue(sheet.values)

    def test_save(self):
        ss.save()

if __name__ == '__main__':
    unittest.main()