# msb2txt

A tool for extracting and converting text data from MSB files from Mages engine games, with specific support for the "Famicom Detective Club" game from Nintendo Switch.

## About

This repository contains tools for working with MSB file formats from Nintendo systems. The primary tool `msb2txt.py` parses MSB files and extracts the text content using the game's character set.

## Usage

Run the script with Python:

```
python msb2txt.py path/to/file.msb
```

Optional arguments:
```
-f, --font     Specify a custom font data file (default: font.txt)
-o, --output   Specify a custom output file (default: same name as input with .txt extension)
-n, --name     Specify a custom player name file (default: name.txt)
```

Example:
```
python msb2txt.py --font custom_font.txt --output dialog.txt --name player.txt game/script/scene01.msb
```

## Files

- `msb2txt.py`: Python script that parses MSB files and extracts text using the font data
- `font.txt`: Character set data extracted from the original "Famicom Detective Club" game from Nintendo Switch. This file contains the complete character set used in the game, including Japanese characters, ASCII symbols, and various special characters.
- `name.txt`: Player name file containing the player's surname and given name, separated by a space. This is used to replace player name commands in the text.

## Player Names

The `name.txt` file should contain a single line with the player's surname and given name separated by a space. For example:

```
木村 天澤
```

During parsing, commands 0x20 and 0x21 will be replaced with the player's surname and given name respectively.

## How It Works

The script extracts text from MSB files by:
1. Reading the MSB file header to find the text offset
2. Parsing the binary data from the text offset
3. Interpreting bytes according to Mages engine format:
   - Bytes ≥ 0x80 are treated as characters (16-bit big-endian values)
   - Bytes < 0x80 are treated as commands (like character names, ruby text, etc.)
4. Mapping character codes to actual characters using the font data (by subtracting 0x8000)
5. Replacing player name commands with names from the name.txt file
6. Outputting the extracted text to a file

## Supported Commands

The script recognizes the following command codes in the MSB files:

- 0x01: CharacterName - Indicates the speaking character's name
- 0x02: DialogueLine - Indicates a line of dialogue
- 0x09: RubyBase - Base text for furigana/ruby annotations
- 0x0A: RubyTextStart - Start of ruby text
- 0x0B: RubyTextEnd - End of ruby text
- 0x20: PlayerSurname - Replaced with the player's surname from name.txt
- 0x21: PlayerGivenName - Replaced with the player's given name from name.txt
- 0x03FF: End - End of text segment

## Note

This tool is for educational and research purposes. All game assets and character data belong to their respective owners (Nintendo).

## License

Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>

All rights reserved.