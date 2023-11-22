import gspread
import os, time, random, string, getpass

sID_file_path = os.path.join(os.getcwd(), 'spreadsheet_ID.txt')

def save_worksheetID(ID):
    with open(sID_file_path, 'w') as file:
        file.write(ID)

def get_worksheetID():
    if os.path.exists(sID_file_path):
        with open(sID_file_path) as file:
            return file.readline().strip('\n')
        
def authorize():
    credentials_path = os.path.join(os.getcwd(), 'credentials.json')
    authorized_user = os.path.join(os.getcwd(), 'authorized_user.json')

    return gspread.oauth(
        credentials_filename=credentials_path,
        authorized_user_filename=authorized_user
        )

def unique_sheetname():
    return f"{getpass.getuser()[:1]}_SHEET_{time.strftime('%Y%m%d%H%M%S')}_{''.join(random.choice(string.ascii_letters + string.digits))}"