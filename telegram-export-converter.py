from sys import argv
import os
import re
import csv
from html import entities

class Message:
    def __init__(self):
        self.messageID = None
        self.timestamp = None
        self.sender = None
        self.fwd = None
        self.reply = None
        self.content = None

    def toTuple(self):
        if self.messageID: self.messageID = self.messageID.replace("message", "")
        if self.sender: self.sender = self.sender.strip()
        if self.fwd: self.fwd = self.fwd.strip()
        if self.reply: self.reply = self.reply.replace("message", "")
        if self.content: self.content = self.content.strip()

        return (self.messageID, self.timestamp, self.sender, self.fwd, self.reply, self.content)

messageIDNewPattern = re.compile('<div class="message default clearfix" id="([^"]+)')
messageIDJoinedPattern = re.compile('<div class="message default clearfix joined" id="([^"]+)')
timestampPattern = re.compile('<div class="pull_right date details" title="([^"]+)')

fwdPattern = re.compile('<div class="userpic userpic\d+" style="width: 42px; height: 42px">')
fwdSenderPattern = re.compile('([^<]+)<span class="details"> ')
sameFWDMediaPattern = re.compile('<div class="media_wrap clearfix">')
sameFWDTextPattern = re.compile('<div class="text">')
replyPattern = re.compile('In reply to <a href="#go_to_([^"]+)"')

photoPattern = re.compile('<div class="media clearfix pull_left media_photo">')
videoPattern = re.compile('<div class="media clearfix pull_left media_video">')
voicePattern = re.compile('<div class="media clearfix pull_left media_voice_message">')
audioPattern = re.compile('<div class="media clearfix pull_left media_audio_file">')
filePattern = re.compile('<div class="media clearfix pull_left media_file">')
locationPattern = re.compile('<a class="media clearfix pull_left block_link media_location" href="[^"]+"')
pollPattern = re.compile('<div class="media_poll">')

linkHTMLPattern = re.compile('</?a[^<]*>')

htmlTags = ["em", "strong", "code", "pre", "s"]

################################################################################

print("Starting...")

# Scans current directory for message<n>.html Telegram chat export files
messageFiles = []
n = 1
for file in os.listdir():
    if file.startswith("messages") and file.endswith(".html"):
        messageFiles.append("messages" + (str(n) if n > 1 else "") + ".html")
        n += 1

if not messageFiles:
    print("No message.html files found. Are you sure the script is in the right directory? Exiting...")
    exit()

print("Loading all {} message files...".format(len(messageFiles)))

# Loads all files content into memory
lines = []
for file in messageFiles:
    with open(file, encoding="UTF-8") as f:
        lines += [line.replace("\n", "").strip() for line in f if line.strip()]

# Writes all concatenated message<n>.html files for debugging
# with open("rawHTML.txt", "w+", encoding="UTF-8") as f:
#     f.write("\n".join(lines) + "\n")

# Sets output filename as the chat's name
chatName = lines[15]
outputFile = "Telegram-" + "".join(c if c.isalnum() else "_" for c in chatName) + ".csv"

################################################################################

print("Processing...")

messages = []
cur = 0
lastSender = None
lastFWDSender = None

while cur < len(lines):
    # Check if it's a new sender's message 
    new = True
    messageID = re.findall(messageIDNewPattern, lines[cur])
    if not messageID:
        new = False
        messageID = re.findall(messageIDJoinedPattern, lines[cur])

    if not messageID:
        cur += 1
        continue

    m = Message()
    m.messageID = messageID[0]

    if new: # New sender
        cur += 9
        timestamp = re.findall(timestampPattern, lines[cur])
        m.timestamp = timestamp[0]

        cur += 4
        m.sender = lines[cur]
        lastSender = m.sender

        cur += 3
        m.content = lines[cur]
    else: # Same sender as the message before
        cur += 2
        timestamp = re.findall(timestampPattern, lines[cur])
        m.timestamp = timestamp[0]

        m.sender = lastSender

        cur += 4
        m.content = lines[cur]

    isFWD = re.match(fwdPattern, m.content)
    isSameFWDText = re.match(sameFWDTextPattern, m.content)
    isSameFWDMedia = re.match(sameFWDMediaPattern, m.content)
    isReply = re.findall(replyPattern, m.content)

    if isFWD:
        cur += 8
        fwdSender = re.findall(fwdSenderPattern, lines[cur])
        m.fwd = fwdSender[0]
        lastFWDSender = m.fwd

        cur += 3
        m.content = lines[cur]
    elif isSameFWDText:
        m.fwd = lastFWDSender

        cur += 1
        m.content = lines[cur]
    elif isSameFWDMedia:
        m.fwd = lastFWDSender

        cur += 6
        m.content = "["+lines[cur]+"]"
    elif isReply:
        m.reply = isReply[0].replace("message", "")

        cur += 3
        m.content = lines[cur]

    isPhoto = re.match(photoPattern, m.content)
    isVideo = re.match(videoPattern, m.content)
    isVoice = re.match(voicePattern, m.content)
    isAudio = re.match(audioPattern, m.content)
    isFile = re.match(filePattern, m.content)
    isLocation = re.match(locationPattern, m.content)
    isPoll = re.match(pollPattern, m.content)

    # Write type of media as content
    if any([isPhoto, isVideo, isVoice, isAudio, isFile]):
        cur += 5
        m.content = "["+lines[cur]+"]"
    elif isLocation:
        cur += 5
        m.content = "["+lines[cur] + " - " + lines[cur+3] + "]"
    elif isPoll:
        m.content = "["+lines[cur+5] + " - " + lines[cur+2] + "]"

    # Replace HTML entities with characters
    if "&" in m.content:
        for original, replaced in entities.html5.items():
            m.content = m.content.replace("&"+original+";", replaced)

    # Replace HTML line breaks
    if "<br>" in m.content:
        m.content = m.content.replace("<br>", "\\n")

    # Remove HTML formatting tags
    if "<" in m.content:
        for original in htmlTags:
            m.content = m.content.replace("<"+original+">", "")
            m.content = m.content.replace("</"+original+">", "")

    # Remove <a> tags
    if "<a" in m.content:
        m.content = re.sub(linkHTMLPattern, "", m.content)

    messages.append(m)
    cur += 1

# Write CSV
with open(outputFile, "w+", encoding="UTF-8", newline="") as f:
    csv.writer(f).writerows([m.toTuple() for m in messages])

print("All done!")