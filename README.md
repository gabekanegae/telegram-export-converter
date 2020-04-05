# Telegram Export and Converter Tool
A Python script to convert Telegram .html chat export files to easier to process .csv.

Made and tested with Python 3.8.0

## Usage
- Export any Telegram chat by going to Options > Export chat history in the Telegram Desktop client
- Unselect all boxes, as photos and other media aren't supported
- Place the script inside the folder with all the message.html files
- Run `python3 telegram-export-converter.py`

## Known Caveats
- No support for exporting actual photos and other media
- No check before overwriting files