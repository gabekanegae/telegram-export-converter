# Telegram Export and Converter Tool
A Python script to convert Telegram `.html` chat export files to easier to process `.csv`.

Made and tested with Python 3.8.0

**As of June 5th 2020, Telegram Desktop [v2.1.10](https://desktop.telegram.org/changelog#v-2-1-10-05-06-20) now allows individual chats to be exported as JSON as well.**

## Usage
- Export any Telegram chat by going to `Options > Export` chat history in the Telegram Desktop client
- Unselect all boxes, as photos and other media aren't supported
- Be sure to have `Format:` set to `HTML`
- Place the script inside the generated folder with all the `message.html` files
- Run `python3 telegram-export-converter.py`

## Known Caveats
- No support for exporting actual photos and other media
- No check before overwriting files
