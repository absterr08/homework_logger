from gmail_reader import GmailReader
from sheet_writer import SheetWriter
import re
import pdb



def validateDate(date):
    matchDashes = re.search('[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}', date)
    matchSlashes = re.search('[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}', date)
    if matchDashes or matchSlashes or date == "":
        return True
    return False

def main():
    lineSeparator = "****************************************************************************"
    day = input("Enter day (WxDx):\n")
    print(lineSeparator)
    date = input("Enter date to search after (optional; defaults to yesterday) (yyyy/mm/dd):\n")
    while not validateDate(date):
        print(lineSeparator)
        date = input("Please enter a valid date (yyyy/mm/dd): ")
    print(lineSeparator)
    print("Finding the good students who did their work...")
    reader = GmailReader(day, date)
    reader.populateMessageSenders()
    emails = reader.submitterEmails

    writer = SheetWriter(day, emails)
    writer.setup()
    cells = writer.range
    print('The following students will have their homework marked as complete in the following cells:')
    print(lineSeparator)
    i = 0
    while i < len(writer.range):
        print(f'{writer.students_complete[i]} : {writer.range[i]}')
        i += 1

    confirm = input("Do you want to proceed? (y/n)\n")
    writer.markCells() if writer.input_handler(confirm) else writer.good_bye()

if __name__ == '__main__':
    main()
