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
        self.type = "msg"
        self.content = None

    def toTuple(self):
        if self.sender: self.sender = self.sender.strip()
        if self.fwd: self.fwd = self.fwd.strip()
        if self.content: self.content = self.content.strip()

        return (self.messageID, self.timestamp, self.sender, self.fwd, self.reply, self.type, self.content)

################################################################################

print("Starting...")
listdirFull = os.listdir()

# Scans current directory for message<n>.html Telegram chat export files
messageFiles = []
counter = 1
for file in listdirFull:
    if file.startswith("messages") and file.endswith(".html"):
        messageFiles.append("messages" + (str(counter) if counter > 1 else "") + ".html")
        counter += 1

if not messageFiles:
    print("No message.html files found. Are you sure the script is in the right directory? Exiting...")
    exit()

print("Loading all {} message files...".format(len(messageFiles)))

# Loads all files content into memory
lines = []
for file in messageFiles:
    with open(file, encoding="UTF-8") as f:
        lines += [line.replace("\n", "").strip() for line in f if line.strip()]

with open("raw.txt", "w+", encoding="UTF-8") as f:
    for line in lines:
        f.write(line)
        f.write("\n")

# Sets output filename as the chat's name
chatName = lines[15]
outputFile = "Telegram-" + chatName.replace(" ", "_") + ".csv"

################################################################################

messageIDNewPattern = re.compile('<div class="message default clearfix" id="([^"]+)')
messageIDJoinedPattern = re.compile('<div class="message default clearfix joined" id="([^"]+)')
timestampPattern = re.compile('<div class="pull_right date details" title="([^"]+)')

fwdPattern = re.compile('<div class="userpic userpic\d+" style="width: 42px; height: 42px">')
sameFWDMediaPattern = re.compile('<div class="media_wrap clearfix">')
sameFWDTextPattern = re.compile('<div class="text">')

photoPattern = re.compile('<div class="media clearfix pull_left media_photo">')
videoPattern = re.compile('<div class="media clearfix pull_left media_video">')
voicePattern = re.compile('<div class="media clearfix pull_left media_voice_message">')
audioPattern = re.compile('<div class="media clearfix pull_left media_audio_file">')
filePattern = re.compile('<div class="media clearfix pull_left media_file">')
locationPattern = re.compile('<a class="media clearfix pull_left block_link media_location" href="[^"]+"')
pollPattern = re.compile('<div class="media_poll">')
replyPattern = re.compile('In reply to <a href="#go_to_([^"]+)"')

fwdSenderPattern = re.compile('([^<]+)<span class="details"> ')
linkHTMLPattern = re.compile('</?a[^<]*>')

htmlTags = ["em", "strong", "code", "pre", "s"]

print("Processing...")
messages = []

cur = 0
total = 0
lastSender = None
lastFWDSender = None
while cur < len(lines):
    new = True
    messageID = re.findall(messageIDNewPattern, lines[cur])
    if not messageID:
        new = False
        messageID = re.findall(messageIDJoinedPattern, lines[cur])

    if messageID:
        m = Message()
        m.line = cur
        m.messageID = messageID[0].replace("message", "")

        if new:
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

        isFWD = re.findall(fwdPattern, m.content)
        isSameFWDText = re.findall(sameFWDTextPattern, m.content)
        isSameFWDMedia = re.findall(sameFWDMediaPattern, m.content)
        isPhoto = re.findall(photoPattern, m.content)
        isVideo = re.findall(videoPattern, m.content)
        isVoice = re.findall(voicePattern, m.content)
        isAudio = re.findall(audioPattern, m.content)
        isFile = re.findall(filePattern, m.content)
        isLocation = re.findall(locationPattern, m.content)
        isPoll = re.findall(pollPattern, m.content)
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

            m.type = "media"

            cur += 6
            m.content = "["+lines[cur]+"]"
        elif isPhoto or isVideo or isVoice or isAudio or isFile:
            m.type = "media"

            cur += 5
            m.content = "["+lines[cur]+"]"
        elif isLocation:
            m.type = "media"

            cur += 5
            m.content = "["+lines[cur] + " - " + lines[cur+3] + "]"
        elif isPoll:
            m.type = "media"

            m.content = "["+lines[cur+5] + " - " + lines[cur+2] + "]"
        elif isReply:
            m.reply = isReply[0].replace("message", "")

            cur += 3
            m.content = lines[cur]

        if isFWD or isReply:
            isPhoto = re.findall(photoPattern, m.content)
            isVideo = re.findall(videoPattern, m.content)
            isVoice = re.findall(voicePattern, m.content)
            isAudio = re.findall(audioPattern, m.content)
            isFile = re.findall(filePattern, m.content)
            isLocation = re.findall(locationPattern, m.content)
            isPoll = re.findall(pollPattern, m.content)

            if isPhoto or isVideo or isVoice or isAudio or isFile:
                m.type = "media"

                cur += 5
                m.content = "["+lines[cur]+"]"
            elif isLocation:
                m.type = "media"

                cur += 5
                m.content = "["+lines[cur] + " - " + lines[cur+3] + "]"
            elif isPoll:
                m.type = "media"

                m.content = "["+lines[cur+5] + " - " + lines[cur+2] + "]"

        if "&" in m.content:
            for original, replaced in entities.html5.items():
                m.content = m.content.replace("&"+original+";", replaced)

        if "<br>" in m.content:
            m.content = m.content.replace("<br>", "\\n")

        for original in htmlTags:
            m.content = m.content.replace("<"+original+">", "")
            m.content = m.content.replace("</"+original+">", "")

        if "<a" in m.content:
            m.content = re.sub(linkHTMLPattern, "", m.content)

        messages.append(m)
    cur += 1

with open(outputFile, "w+", encoding="UTF-8", newline="") as f:
    csv.writer(f).writerows([m.toTuple() for m in messages])

print("All done!")