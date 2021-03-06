from __future__ import print_function
import httplib2
import os
import pdb
import base64
import re
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class GmailReader:
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/gmail-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

    CLIENT_SECRET_FILE = 'gmail_client_secret.json'
    APPLICATION_NAME = 'a/A Homework Logger'
    LABEL_ID = 'Label_1'
    # self.service.users().labels().list(userId='me').execute()

    def __init__(self, day, date=None):
        self.day = day
        self.dateQuery = self.setDateQuery(date)
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=self.http)
        self.messages = self.service.users().messages()
        self.submitterEmails = []
        self.searching = False

    def setDateQuery(self, date):
        # if date == '':
        #     dayBeforeToday = datetime.date.today() - datetime.timedelta(5)
        #     return "subject:hwrk " + "subject:+" + self.day + " after:" + str(dayBeforeToday)
        # givenDate = datetime.datetime.strptime(date, "%Y-%m-%d")
        # dayBefore = (givenDate - datetime.timedelta(2)).date()
        # dayAfter = (givenDate + datetime.timedelta(2)).date()
        # return "hwrk " + self.day + " after:" + str(dayBefore) + " before:" + str(dayAfter)
        return "hwrk " + self.day + " after:2018-05-21"

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
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'homework_logger-gmail-api.json')

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

    def getMessageIds(self):
        messages = self.messages.list(userId='me',
        q=self.dateQuery,
        maxResults=1000,
        labelIds=self.LABEL_ID).execute()
        messageIds = []
        try:
            messages = messages['messages']
            for message in messages:
                messageIds.append(message['id'])
            return messageIds
        except:
            return messageIds

    def getMessageBody(self, messageId):
        message = self.messages.get(userId='me', id=messageId, format='raw').execute()
        return base64.urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8')

    def getMessageSubject(self, messageBody):
        match = re.search('Subject: (.*?)\\r\\n', messageBody).group(1)
        return match

    def getMessageSenderEmail(self, messageBody):
        try:
            # email = re.search('From: .*?<(.*?)>\\r\\n', messageBody).group(1)
            email = re.search('Original-Sender: (.*?)\\r\\n', messageBody).group(1)
            # pdb.set_trace()
            return email.lower()
        except:
            # pdb.set_trace()
            print('')

    def getMessageSenderName(self, messageBody):
        return re.search('From: (.*?) <.*?>\\r\\n', messageBody).group(1)

    def checkMessageSubject(self, messageBody):
        subject = self.getMessageSubject(messageBody)
        searchString = 'HWRK ' + self.day
        rgxMatch = re.search(searchString, subject)
        return True if rgxMatch else False

    def populateMessageSenders(self):
        messageIds = self.getMessageIds()
        for messageId in messageIds:
            message = self.messages.get(userId='me', id=messageId, format='full').execute()
            headers = message['payload']['headers']
            # print(headers[41])
            messageBody = self.getMessageBody(messageId)
            # if self.checkMessageSubject(messageBody):
            senderEmail = self.getMessageSenderEmail(messageBody)
            print(senderEmail)
            self.submitterEmails.append(senderEmail)
        # pdb.set_trace()
