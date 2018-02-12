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

    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Gmail API Python Quickstart'
    LABEL_ID = 'Label_1'

    def __init__(self, day, date=None):
        self.day = day
        self.dateQuery = self.setDateQuery(date)
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=self.http)
        self.messages = self.service.users().messages()
        self.submitterEmails = []

    def setDateQuery(self, date):
        if date == '':
            date = datetime.date.today() - datetime.timedelta(1)
        return "after:" + str(date)


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
                                       'gmail-python-quickstart.json')

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
        messages = self.messages.list(userId='me', labelIds=[self.LABEL_ID],
        q=self.dateQuery).execute()['messages']
        messageIds = []
        for message in messages:
            messageIds.append(message['id'])

        return messageIds

    def getMessageBody(self, messageId):
        message = self.messages.get(userId='me', id=messageId, format='raw').execute()
        return base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    def getMessageSubject(self, messageBody):
        return re.search('Subject: (.*?)\\r\\n', messageBody).group(1)

    def getMessageSenderEmail(self, messageBody):
        return re.search('From: (.*?) <.*?>\\r\\n', messageBody).group(1)

    def getMessageSenderName(self, messageBody):
        return re.search('From:.*?<(.*?)>\\r\\n', messageBody).group(1)

    def checkMessageSubject(self, messageBody):
        subject = self.getMessageSubject(messageBody)
        rgxMatch = re.search(self.day, subject)
        return True if rgxMatch else False

    def populateMessageSenders(self):
        messageIds = self.getMessageIds()
        for messageId in messageIds:
            messageBody = self.getMessageBody(messageId)
            senderEmail = self.getMessageSenderEmail(messageBody)
            if self.checkMessageSubject(messageBody):
                self.submitterEmails.append(senderEmail)




def main():
    day = raw_input("Enter day (WxDx):\n")
    print("*****************")
    date = raw_input("Enter date to search after (optional; defaults to yesterday) (yyyy/mm/dd):\n")
    print("*****************")
    # limit = raw_input("Search all messages? (y/n):\n")
    # limit = False if limit == "y" else True
    gmailReader = GmailReader(day, date)
    gmailReader.populateMessageSenders()
    for name in gmailReader.submitterEmails:
        print(name)

def valiDate(date):
    matchDashes = re.search('[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}')
    matchSlashes = re.search('[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}')
    if matchDashes or matchSlashes:
        return True
    return False



if __name__ == '__main__':
    main()