from html import unescape
from time import time
from sys import argv
import csv
import os
import re

class Message:
    def __init__(self):
        self.message_id = None
        self.timestamp = None
        self.sender = None
        self.fwd = None
        self.reply = None
        self.content = None

    def toTuple(self):
        if self.message_id: self.message_id = self.message_id.replace('message', '')
        if self.timestamp: self.timestamp = ' '.join(self.timestamp.split()[:2])
        if self.sender: self.sender = unescape(self.sender.strip())
        if self.fwd: self.fwd = unescape(self.fwd.strip())
        if self.reply: self.reply = self.reply.replace('message', '')
        if self.content: self.content = unescape(self.content.strip())

        return (self.message_id, self.timestamp, self.sender, self.fwd, self.reply, self.content)

t0 = time()

message_id_new_pattern = re.compile('<div class="message default clearfix" id="([^"]+)')
message_id_joined_pattern = re.compile('<div class="message default clearfix joined" id="([^"]+)')
timestamp_pattern = re.compile('<div class="pull_right date details" title="([^"]+)')

fwd_pattern = re.compile('<div class="userpic userpic\d+" style="width: 42px; height: 42px">')
fwd_reply_pattern = re.compile('<div class="reply_to details">')
fwd_sender_pattern = re.compile('([^<]+)<span class="date details')
same_fwd_media_pattern = re.compile('<div class="media_wrap clearfix">')
same_fwd_text_pattern = re.compile('<div class="text">')
reply_pattern = re.compile('In reply to <a href="(?:messages\d*.html)?#go_to_([^"]+)"')

photo_pattern = re.compile('<div class="media clearfix pull_left media_photo">')
video_pattern = re.compile('<div class="media clearfix pull_left media_video">')
voice_pattern = re.compile('<div class="media clearfix pull_left media_voice_message">')
audio_pattern = re.compile('<div class="media clearfix pull_left media_audio_file">')
file_pattern = re.compile('<div class="media clearfix pull_left media_file">')
contact_pattern = re.compile('<div class="media clearfix pull_left media_contact">')
contact_link_pattern = re.compile('<a class="media clearfix pull_left block_link media_contact" href="[^"]+"')
location_link_pattern = re.compile('<a class="media clearfix pull_left block_link media_location" href="[^"]+"')
call_pattern = re.compile('<div class="media clearfix pull_left media_call( success)?">')
poll_pattern = re.compile('<div class="media_poll">')
game_pattern = re.compile('<a class="media clearfix pull_left block_link media_game" href="[^"]+">')

html_link_pattern = re.compile('</?a[^<]*>')
html_span_pattern = re.compile('</?span[^<]*>')

html_tags = ['em', 'strong', 'code', 'pre', 's']

################################################################################

print("Starting...")

# Scans current directory for message<n>.html Telegram chat export files
message_files = []
n = 1
for file in os.listdir():
    if file.startswith('messages') and file.endswith('.html'):
        message_files.append('messages' + (str(n) if n > 1 else '') + '.html')
        n += 1

if not message_files:
    print('No message.html files found. Are you sure the script is in the right directory? Exiting...')
    exit()

print(f'Loading all {len(message_files)} message files...')

# Loads all files content into memory
lines = []
for file in message_files:
    with open(file, encoding='UTF-8') as f:
        lines += [line.replace('\n', '').strip() for line in f if line.strip()]

# Writes all concatenated message<n>.html files for debugging
# with open('rawHTML.txt', 'w+', encoding='UTF-8') as f:
#     f.write('\n'.join(lines) + '\n')

# Sets output filename as the chat's name
chat_name = lines[15]
output_file = 'Telegram-' + ''.join(c if c.isalnum() else '_' for c in chat_name) + '.csv'

################################################################################

print(f'Processing \'{chat_name}\'...')

messages = []
cur = 0
last_sender = None
last_fwd_sender = None

while cur < len(lines):
    # Skip lines that aren't the start of a message
    if not lines[cur].startswith('<div class='):
        cur += 1
        continue

    # Check if it's a new sender's message
    new = True
    message_id = re.findall(message_id_new_pattern, lines[cur])
    if not message_id:
        new = False
        message_id = re.findall(message_id_joined_pattern, lines[cur])

    # Skip lines that aren't the start of a message
    if not message_id:
        cur += 1
        continue

    m = Message()
    m.message_id = message_id[0]

    if new: # New sender
        # If it's from a Deleted Account, no initial is
        # shown as avatar, so there's a line less to skip
        if lines[cur+4] == '</div>':
            cur += 8
        else:
            cur += 9

        timestamp = re.findall(timestamp_pattern, lines[cur])
        m.timestamp = timestamp[0]

        cur += 4
        m.sender = lines[cur]
        last_sender = m.sender

        cur += 3
        m.content = lines[cur]
    else: # Same sender as the message before
        cur += 2
        timestamp = re.findall(timestamp_pattern, lines[cur])
        m.timestamp = timestamp[0]

        m.sender = last_sender

        cur += 4
        m.content = lines[cur]

    is_fwd = re.match(fwd_pattern, m.content)
    is_same_fwd_text = re.match(same_fwd_text_pattern, m.content)
    is_same_fwd_media = re.match(same_fwd_media_pattern, m.content)
    is_reply = re.findall(reply_pattern, m.content)
    is_fwd_reply_same_fwd_text = re.findall(fwd_reply_pattern, m.content)

    if is_fwd:
        # If it's from a Deleted Account, no initial is
        # shown as avatar, so there's a line less to skip
        if lines[cur+2] == '</div>':
            cur += 7
        else:
            cur += 8
        
        fwd_sender = re.findall(fwd_sender_pattern, lines[cur])
        m.fwd = fwd_sender[0]
        last_fwd_sender = m.fwd

        cur += 2
        is_fwd_reply = re.findall(fwd_reply_pattern, lines[cur])
        if is_fwd_reply:
            cur += 4
        else:
            cur += 1

        m.content = lines[cur]
    elif is_fwd_reply_same_fwd_text:
        m.fwd = last_fwd_sender

        cur += 4
        m.content = lines[cur]
    elif is_same_fwd_text:
        m.fwd = last_fwd_sender

        cur += 1
        m.content = lines[cur]
    elif is_same_fwd_media:
        m.fwd = last_fwd_sender

        cur += 6
        m.content = f'[{lines[cur]}]'
    elif is_reply:
        m.reply = is_reply[0]

        cur += 3
        m.content = lines[cur]

    if m.content.startswith('<'):
        is_photo = re.match(photo_pattern, m.content)
        is_video = re.match(video_pattern, m.content)
        is_voice = re.match(voice_pattern, m.content)
        is_audio = re.match(audio_pattern, m.content)
        is_file = re.match(file_pattern, m.content)
        is_contact = re.match(contact_pattern, m.content)
        is_contact_link = re.match(contact_link_pattern, m.content)
        is_location_link = re.match(location_link_pattern, m.content)
        is_call = re.match(call_pattern, m.content)
        is_poll = re.match(poll_pattern, m.content)
        is_game = re.match(game_pattern, m.content)

        # Write type of media as content
        if any([is_photo, is_video, is_voice, is_audio, is_file]):
            cur += 5
            m.content = f'[{lines[cur]}]'
        elif is_contact or is_contact_link:
            cur += 5
            m.content = f'[Contact - {lines[cur]} - {lines[cur+3]}]'
        elif is_location_link:
            cur += 5
            m.content = f'[{lines[cur]} - {lines[cur+3]}]'
        elif is_call:
            cur += 8
            m.content = f'[Call - {lines[cur]}]'
        elif is_poll:
            m.content = f'[{lines[cur+5]} - {lines[cur+2]}]'
        elif is_game:
            m.content = f'[Game - {lines[cur+5]} - {lines[cur+11]}]'

    # Replace HTML line breaks
    if '<br>' in m.content:
        m.content = m.content.replace('<br>', '\\n')

    # Remove HTML formatting tags
    if '<' in m.content and any(f'<{tag}>' in m.content for tag in html_tags):
        for tag in html_tags:
            m.content = m.content.replace(f'<{tag}>', '')
            m.content = m.content.replace(f'</{tag}>', '')

    # Remove HTML tags with args
    if '<a' in m.content:
        m.content = re.sub(html_link_pattern, '', m.content)
    if '<span' in m.content:
        m.content = re.sub(html_span_pattern, '', m.content)

    # Handle animated emojis, as they're not logged properly by Telegram (might change soon?)
    if m.content == '</div>':
        m.content = '[Animated emoji]'

    messages.append(m)
    cur += 1

# Write CSV
with open(output_file, 'w+', encoding='UTF-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(list(messages[0].__dict__.keys()))
    writer.writerows([m.toTuple() for m in messages])

print(f'Written to \'{output_file}\' in {(time()-t0):.2f}s.')