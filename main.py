import os
import time
import telebot
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

path = '' #your path
filesBefore = set()
TG_API = "" #your telegram bot API
DRIVE_API = "" #path to your GDrive secret json file
SCOPES = ["https://www.googleapis.com/auth/drive"]
bot = telebot.TeleBot(TG_API, parse_mode = None)
def send_msg(message):
    bot.send_message(#your telegram id
        , message)


creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            DRIVE_API, SCOPES
        )
        creds = flow.run_local_server(port = 0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

def search_file():
    service = build("drive", "v3", credentials = creds)
    files = []
    page_token = None
    while True:
        response = (
            service.files().list(
                q="parents in '{}'".format(#your GDrive folder id),
                spaces = "drive",
                fields = "nextPageToken, files(id, name)",
                pageToken = page_token
            )
            .execute()
        )
        for file in response.get("files", []):
            print('Found file: ' + file.get("name") + ' ' +file.get("id"))
        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break
    return files


disk_files = search_file()


def upload_basic(filename, name):
  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": name, "parents": [#your GDrive folder id""]}
    media = MediaFileUpload(filename, mimetype="image/jpeg")
    # pylint: disable=maybe-no-member
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    print(f'File ID: {file.get("id")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.get("id")


while(True):
    filesBefore = set()
    files = set(os.listdir(path))
    temp = files.copy()
    for i in disk_files:
        for j in temp:
            if(i['name'] == j):
                files.remove(j)
    deletedFiles = filesBefore - files
    newFiles = files - filesBefore
    filesBefore = files
    print(newFiles)
    if(len(newFiles) != 0):
         for i in newFiles:
             send_msg("found new file: " + i)
    for i in newFiles:
        send_msg("started uploading file: " + path + '\\' + i + " id: " + upload_basic(path + '\\' + i, i))
    time.sleep(10)
