from __future__ import print_function
import httplib2
import os
import pdb
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class SheetWriter:
    from wxdx_table import WEEK_DAYS
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    CLIENT_SECRET_FILE = 'docs_client_secret.json'
    APPLICATION_NAME = 'a/A Homework Logger'

    # tester IDs plus a valid API_KEY if necessary
    # SHEET_ID = '1MQfI2PPMkBExKMIJoiMb0F_2ENkMtwviD5dDgvVQx7M'

    # SHEET_ID = '1-b_qTGM-QpBv7AyXF4PHLDEMFNI3g8TL72ZsRFeBj2Q'
    API_KEY = 'AIzaSyCkDVeCy_Y2Zaa_3B7nfME8xB0xXNLw8Dw'

    #actual a/A sheet:
    SHEET_ID = '1PyYBW6edPNbnVE-EyfmMvPhA9up35aVFA48gw8eVUdM'

    MARK = [['X']]


    # On initialization, provide a Week and Day as a string, ex: 'W3D4'
    # also provide the list of students who've completed their HW
    def __init__(self, WXDX, students):
        self.day = WXDX
        self.students_complete = students
        # assigns an API_KEY if one is defined above, else leaves empty.
        self.API_KEY = self.API_KEY or ''
        # self.API_KEY = ''
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        self.service = discovery.build('sheets', 'v4', http=self.http,
                                  discoveryServiceUrl=self.discoveryUrl)

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            # pdb.set_trace()
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'homework_logger-google-docs-api.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def markCell(self, cell):
        body = {
        'values': self.MARK
        }

        result = self.service.spreadsheets().values().update(
        spreadsheetId=self.SHEET_ID, range=cell, key=self.API_KEY,
        valueInputOption="USER_ENTERED",
        body=body).execute()

    def markCells(self):
        count = 0
        for cell in self.range:
            self.markCell(cell)
            print(f'{cell} marked')
            count += 1

        print(f'{count} cell(s) marked')


    # generates a dictionary of students pointing to their corresponding row numbers from the sheet
    def assign_keys(self, names):
        students = {}
        idx = 3
        for name in names:
            students[name] = str(idx)
            idx += 1
            self.student_keys = students

    # Collects the students from the spreadsheet then converts them to a dictionary
    def student_keys(self):
        result = self.service.spreadsheets().values().get(
        spreadsheetId=self.SHEET_ID, range='C3:C', majorDimension='COLUMNS'
        ).execute()
        self.assign_keys(result['values'][0])

    # Defines the range of cells to be edited with 'markCells'
    def range_setter(self):
        cells = []
        col = self.WEEK_DAYS[self.day]
        for student in self.students_complete:
            cells.append(col + self.student_keys[student])
        self.range = cells

    def setup(self):
        self.student_keys()
        self.range_setter()

    def input_handler(self, input):
        handler = {
            'y': True,
            'n': False
        }

        return handler[input]

    def good_bye(self):
        print('Operation cancelled.  Goodbye!')
        SystemExit()
