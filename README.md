# Movie/Show Tracker

Simplistic interface for tracking movies/shows using Google Sheets.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

In order to run the script properly you will have to:
- Set the API Key using your OMDB API Key
- Get credentials using Google API Console.
- Put the acquired credentials in the project file and rename it to "credentials.json"

## Usage

1. Clone this repository to your machine or download the files

2. [Get an OMDB API Key](https://www.omdbapi.com/apikey.aspx?__EVENTTARGET=freeAcct&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKLTIwNDY4MTIzNQ9kFgYCAQ9kFgICBw8WAh4HVmlzaWJsZWhkAgIPFgIfAGhkAgMPFgIfAGhkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYDBQtwYXRyZW9uQWNjdAUIZnJlZUFjY3QFCGZyZWVBY2N0oCxKYG7xaZwy2ktIrVmWGdWzxj%2FDhHQaAqqFYTiRTDE%3D&__VIEWSTATEGENERATOR=5E550F58&__EVENTVALIDATION=%2FwEdAAU%2BO86JjTqdg0yhuGR2tBukmSzhXfnlWWVdWIamVouVTzfZJuQDpLVS6HZFWq5fYpioiDjxFjSdCQfbG0SWduXFd8BcWGH1ot0k0SO7CfuulHLL4j%2B3qCcW3ReXhfb4KKsSs3zlQ%2B48KY6Qzm7wzZbR&at=freeAcct&Email=). Put this key in [main](main.py) or create a .env file with the line:
```py
APIKEY = "Your_Key"
```

3. [Create and download credentials using Google API Console with gspread](https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id). Put the downloaded file in this project folder.

4. Run main
```
python main.py
```

# Contributing
Contributions are open and welcome to all. If you run into problems or have ideas you would like to test out, don't hesitate to open an issue or submit pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.