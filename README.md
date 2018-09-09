# telegram-export-converter
A Python script to convert Telegram .html chat export files to easier to process .txt and .csv.

Made and tested with Python 3.6.5

## Usage
- Export any Telegram chat by going to Options > Export chat history in the Telegram Desktop client
- Unselect all boxes, as photos and other media aren't supported
- Place the script inside the folder with all the message.html files
- Run `python3 telegram-export-converter.py [output file]`
    - If no output file is provided, default filename will be the chat's name

## Known Caveats
- No support for exporting actual photos and other media
- Throws out reply info and "via @" occurrences
- Replaces `"` with `'` to allow for easier .csv export
- No command line options for choosing .txt or .csv, always generates both
- No check before overwriting files