import os
import random
import string
import time
import getpass
import gspread
from .utils import re_dirname

dirpath = re_dirname(os.path.dirname(__file__), 1)
sID_file_path = os.path.join(dirpath, 'spreadsheet_ID.txt')

def save_worksheetID(ID):
    with open(sID_file_path, 'w') as file:
        file.write(ID)

def get_worksheetID():
    if os.path.exists(sID_file_path):
        with open(sID_file_path) as file:
            return file.readline().strip('\n')
        
def authorize():
    credentials_path = os.path.join(dirpath, 'credentials.json')
    authorized_user = os.path.join(dirpath, 'authorized_user.json')

    return gspread.oauth(
        credentials_filename=credentials_path,
        authorized_user_filename=authorized_user
        )

def unique_sheetname():
    return f"{getpass.getuser()[:1]}_SHEET_{time.strftime('%Y%m%d%H%M%S')}_{''.join(random.choice(string.ascii_letters + string.digits))}"
