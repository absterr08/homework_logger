from gmail_reader import GmailReader
from SheetWriter import SheetWriter
import re
import pdb


def main():
    day = raw_input("Enter day (WxDx):\n")
    print("*****************")
    date = raw_input("Enter date to search after (optional; defaults to yesterday) (yyyy/mm/dd):\n")
    print("*****************")
    while not valiDate(date):
        date = raw_input("Please enter a valid date (yyyy/mm/dd): ")
        print("*****************")
    # limit = raw_input("Search all messages? (y/n):\n")
    # limit = False if limit == "y" else True
    gmailReader = GmailReader(day, date)
    gmailReader.populateMessageSenders()
    emails = gmailReader.submitterEmails
    # for email in emails:
    #     print(email)
    # pdb.set_trace()
    sheetWriter = SheetWriter(day, emails)
    sheetWriter.setup()
    cells = sheetWriter.range
    sheetWriter.markCells(cells)

def valiDate(date):
    matchDashes = re.search('[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}', date)
    matchSlashes = re.search('[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}', date)
    if matchDashes or matchSlashes or date == "":
        return True
    return False

if __name__ == '__main__':
    main()
