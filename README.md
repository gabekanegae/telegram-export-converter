# Telegram Export and Converter Tool
A Python script to convert Telegram .html chat export files to easier to process .txt and .csv.

Made and tested with Python 3.6.5

## Usage
- Export any Telegram chat by going to Options > Export chat history in the Telegram Desktop client
- Unselect all boxes, as photos and other media aren't supported
- Place the script inside the folder with all the message.html files
    - Or alongside the folder, then run with the flag `-d (FOLDERNAME)`
- Run `python3 telegram-export-converter.py [FLAGS]`, with flags listed below:
    - `-h`: shows help page.
    - `-txt`, `-csv`: generates only the .txt or .csv file.
        - Default: generates both.
    - `-o (FILENAME)`: sets otuput filename.
        - Default: Telegram-CHATNAME
    - `-d (DIRECTORY)`: runs the script as if in that directory, but generating output files in the current directory.

## Known Caveats
- No support for exporting actual photos and other media
- Throws out reply info and "via @" occurrences
- Replaces `"` with `'` to allow for easier .csv export
- No check before overwriting files
