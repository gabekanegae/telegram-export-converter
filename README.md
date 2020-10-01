# Telegram Export and Converter Tool
[![python](https://img.shields.io/badge/Python-3.8.0-blue.svg)](https://docs.python.org/release/3.8.0/whatsnew/changelog.html#changelog)
[![telegram](https://img.shields.io/badge/Telegram-2.1.10-blue.svg)](https://desktop.telegram.org/changelog#v-2-1-10-05-06-20)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/KanegaeGabriel/telegram-export-converter/blob/master/README.md)

A Python script to convert Telegram `.html` chat export files to easier to process `.csv`.

**As of June 5th 2020, Telegram Desktop [v2.1.10](https://desktop.telegram.org/changelog#v-2-1-10-05-06-20) now allows individual chats to be exported as JSON as well.**

## Usage
- In the Telegram Desktop client, open the chat you want to export
- In the upper right, go to `Options > Export chat history`
- Unselect all boxes, as photos and other media aren't supported
- Be sure to have `Format:` set to `HTML`
- Place the script inside the generated folder with all the `message.html` files
- Run `python3 telegram-export-converter.py`

## Known Caveats
- No support for exporting actual photos and other media
- No check before overwriting files
