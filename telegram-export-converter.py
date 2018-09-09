########################################################
#            Telegram Chat History Converter           #
#                        Sep 2018                      #
#                                                      #
#   Converts all message.html Telegram files to .txt   #
#        and .csv files for easier processing.         #
#                                                      #
# Code by: Gabriel Kanegae Souza                       #
########################################################

from os import listdir
from re import sub
from sys import argv

# HTML div headers for each element
TIMESTAMP = '<div class="pull_right date details" title="'
SENDER = '<div class="from_name">\n'
FWD_MSG = '<div class="forwarded body">\n'
FWD_SENDER = '<span class="details">'
MESSAGE = '<div class="text">\n'
MEDIA = '<div class="title bold">\n'
REPLY = '<div class="reply_to details">\n'

# Identifiers for the element types
MEDIA_TAG = "<media>\n"
MESSAGE_TAG = "<msg>\n"
NOFWD_TAG = "<nfwd>\n"

# Separator for the .csv file
CSV_SEP = ";"

print("Starting...")

# Receives output filename as argument
outputFile = ""
if len(argv) > 1:
    outputFile = argv[1].split(".")[0]
    print("Will save file as '{}.txt' and '{}.csv'...".format(outputFile, outputFile))

print("Looking for message files...")

# Scans current directory for message<n>.html Telegram chat export files
messageFiles = []
counter = 1
listdirFull = listdir()
for file in listdirFull:
    if file.startswith("messages") and file.endswith(".html"):
        messageFiles.append("messages" + (str(counter) if counter > 1 else "") + ".html")
        counter += 1

if len(messageFiles) == 0:
    print("No message.html files found. Are you sure the script is in the right directory? Exiting...")
    exit()

print("Loading all {} message files...".format(len(messageFiles)))

# Loads all files content into memory
linesRaw = []
for file in messageFiles:
    with open(file) as f:
        for line in f:
            if len(line) > 0 and line != "\n":
                linesRaw.append(line.replace("\n", "").strip() + "\n")

# Sets default filename as the chat's name, if not provided as argument
if outputFile == "":
    outputFile = "Telegram-" + linesRaw[15][:-1].replace(" ", "_")

print("Processing...")
linesProcessed = []

# Buffers to store sender's name (when they send many messages, it's only shown once)
lastNameShown, lastFWDShown = "", ""

# Processes each element and filters them
for i in range(len(linesRaw)):
    # Sender's name
    if linesRaw[i] == SENDER:
        # If it's a forward, show forwarder's name
        if linesRaw[i-1] == FWD_MSG and linesRaw[i-11] != SENDER and linesRaw[i-10] != SENDER:
            linesProcessed.append(lastNameShown)

        # Show sender's name
        linesProcessed.append(linesRaw[i+1])

        # Save it on buffers, as original sender or forwarder
        if FWD_SENDER not in linesRaw[i+1]:
            lastNameShown = linesRaw[i+1]
        else:
            lastFWDShown = linesRaw[i+1]

    # Message
    elif linesRaw[i] == MESSAGE:
        # If it's not a reply nor the first message sent nor media, show sender's name 
        if ((linesRaw[i-3] != SENDER and linesRaw[i-3] != REPLY) or (linesRaw[i-3] == REPLY and linesRaw[i-6] != SENDER)) and (linesRaw[i-12] != MEDIA):
            linesProcessed.append(lastNameShown)

        # If it's a forward, show original sender's name
        if linesRaw[i-1] == FWD_MSG:
            linesProcessed.append(lastFWDShown)

        # If it's not a media description
        if linesRaw[i-12] != MEDIA:
            # If it's not a forward
            if linesRaw[i-1] != FWD_MSG and linesRaw[i-4] != FWD_MSG:
                linesProcessed.append(NOFWD_TAG)

            linesProcessed.append(MESSAGE_TAG)

        # Show message
        linesProcessed.append(linesRaw[i+1])

    # Message timestamp
    elif linesRaw[i].startswith(TIMESTAMP):
        # Get timestamp substring from inside the tags
        linesProcessed.append(linesRaw[i][linesRaw[i].index(TIMESTAMP) + len(TIMESTAMP):-3] + "\n")

    # Media (audio, images, videos, gifs...)
    elif linesRaw[i] == MEDIA:
        # If it's not the first message sent, show sender's name
        if linesRaw[i-8] != SENDER and linesRaw[i-11] != SENDER:
            linesProcessed.append(lastNameShown)

        # If it's not a forward
        if linesRaw[i-9] != FWD_MSG:
            linesProcessed.append(NOFWD_TAG)

        linesProcessed.append(MEDIA_TAG)

        # If it has a description, show it in the same line
        if linesRaw[i+12] == MESSAGE:
            linesProcessed.append("[" + linesRaw[i+1][:-1] + "] ")
        else:
            linesProcessed.append("[" + linesRaw[i+1][:-1] + "]\n")

htmlEntities = {"&lt;": "<", "&gt;": ">", "&amp;": "&",
                "&quot;": "\"", "&apos;": "'", "&cent;": "¢",
                "&pound;": "£", "&yen;": "¥", "&euro;": "€",
                "&copy;": "©", "&reg;": "®"}

# Final cleanup, to remove leftover HTML tags
linesCleaned = []
for i in range(len(linesProcessed)):
    # Remove HTML newlines
    linesProcessed[i] = linesProcessed[i].replace("<br>", " ")

    # Remove <a> tags, keeping the links
    linesProcessed[i] = sub(r"<a href=\".+\">", "", linesProcessed[i]).replace("</a>", " ")

    # Replace all HTML entities
    for (k, v) in htmlEntities.items():
        linesProcessed[i] = linesProcessed[i].replace(k, v)

    # Format forwarded messages
    if FWD_SENDER in linesProcessed[i]:
        linesProcessed[i] = linesProcessed[i].replace(FWD_SENDER, " | FWD @").replace("  | FWD @", " | FWD @").replace("</span>", "")
        linesProcessed[i] = sub(r" +via @.+\| FWD", " | FWD", linesProcessed[i])

    # Remove "via @" occurences
    if FWD_SENDER in linesProcessed[i]:
        linesProcessed[i] = sub(r" +via @.+\| FWD", " | FWD", linesProcessed[i])
    linesProcessed[i] = sub(r"via @.+", "", linesProcessed[i])
    
    linesCleaned.append(linesProcessed[i])

# Writes to .txt
print("Writing to file '{}.txt'...".format(outputFile))
with open(outputFile + ".txt", "w") as f:
    for line in linesCleaned:
        f.write(line)

# Reads .txt contents back
linesRead = []
with open(outputFile + ".txt") as f:
    for line in f:
        linesRead.append(line)

# Writes to .csv
print("Writing to file '{}.csv'...".format(outputFile))
with open(outputFile + ".csv", "w", encoding="UTF-16") as f:
    for i in range(len(linesRead)):
        linesRead[i] = linesRead[i].replace("\n", "")
        linesRead[i] = linesRead[i].replace("\"", "'")

    for i in range(len(linesRead)):
        if i % 5 == 0:
            f.write("\"" + linesRead[i] + "\"" + CSV_SEP)
            f.write("\"" + linesRead[i+1] + "\"" + CSV_SEP)
            f.write("\"" + linesRead[i+2] + "\"" + CSV_SEP)
            f.write("\"" + linesRead[i+3] + "\"" + CSV_SEP)
            f.write("\"" + linesRead[i+4] + "\"" + "\n")

print("All done!")