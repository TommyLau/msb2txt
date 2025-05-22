# Mages Engine Tools

A collection of tools for extracting and converting data from Mages engine games, with specific support for the Famicom Tantei Club (Detective Club) series.

## Tools

### 1. MSB Text Extractor (msb2txt.py)

A Python script that parses MSB files and extracts the text content using the game's character set. Supports both 16-bit and 32-bit character encoding formats.

#### Supported Games

- **FTV1**: Famicom Tantei Club: The Missing Heir (16-bit encoding)
- **FTV2**: Famicom Tantei Club: The Girl Who Stands Behind (16-bit encoding)
- **FTCM**: Famicom Tantei Club: Emio – The Smiling Man (32-bit encoding)

#### Usage

```bash
# Default mode (16-bit for FTV1/FTV2)
python msb2txt.py path/to/file.msb

# 32-bit mode for FTCM
python msb2txt.py --ftcm path/to/file.msb
```

Optional arguments:
```
-f, --font     Specify a custom font data file
               (defaults: font_ftv1_2.txt for FTV1/FTV2, font_gl.txt for FTCM)
-o, --output   Specify a custom output file (default: same name as input with .txt extension)
-n, --name     Specify a custom player name file (default: name.txt)
--ftcm         Use 32-bit mode for FTCM
```

Example:
```bash
python msb2txt.py --font custom_font.txt --output dialog.txt --name player.txt game/script/scene01.msb
```

### 2. MPK File Extractor (mpk_extractor.py)

A Python script to extract files from Mages Package (MPK) archives. The tool reads the entire MPK file into memory for faster extraction and creates a directory named after the MPK file to store extracted contents.

⚠️ **Note**: Currently only supports uncompressed files. Compressed files will be extracted as-is without decompression.

#### Usage

```bash
python mpk_extractor.py your_file.mpk
```

This will:
1. Create a directory named after your MPK file (e.g., `mes00` for `mes00.mpk`)
2. Extract all files maintaining their original paths
3. Show compression status for each file

Example output:
```
Reading MPK file: mes00.mpk
Loaded 1,234,567 bytes into memory
MPK Version: 2.0
Found 10 files
Files will be extracted to: mes00/
  file1.txt (uncompressed)
  file2.dat (compressed)
Extracting files...
Extraction complete!
```

## Files

- `msb2txt.py`: Python script that parses MSB files and extracts text using the font data
- `mpk_extractor.py`: Python script that extracts files from MPK archives
- `font_ftv1_2.txt`: Character set data extracted from "Famicom Detective Club: The Missing Heir" and "Famicom Detective Club: The Girl Who Stands Behind" from Nintendo Switch. This file contains the complete character set used in the games, including Japanese characters, ASCII symbols, and various special characters.
- `font_gl.txt`: Character set data extracted from "Famicom Detective Club: Emio – The Smiling Man" from Nintendo Switch. This file contains the complete character set used in the game, including Japanese characters, ASCII symbols, and various special characters.
- `name.txt`: Player name file containing the player's surname and given name, separated by a space. This is used to replace player name commands in the text.

## Player Names

The `name.txt` file should contain a single line with the player's surname and given name separated by a space. For example:

```
木村 天澤
```

During parsing, commands 0x20 and 0x21 will be replaced with the player's surname and given name respectively.

## How It Works

The MSB extractor works by:
1. Reading the MSB file header to identify file format and version
2. Parsing the entry table to find text locations
3. Reading character codes based on game version (16-bit or 32-bit)
4. Converting character codes to actual text using font mapping data
5. Handling special commands like player name substitution
6. Outputting the extracted text to a file

## Supported Commands

The script recognizes the following command codes in the MSB files:

- 0x00: LineBreak - Inserts a newline character
- 0x01: CharacterName - Indicates the speaking character's name
- 0x02: LineStart - Marks the start of a new line of text
- 0x03: LineEnd - Marks the end of a line of text
- 0x04: SetColor - Sets text color (format: <#RRGGBB>, where RR=Red, GG=Green, BB=Blue)
- 0x09: RubyBase - Base text for furigana/ruby annotations
- 0x0A: RubyTextStart - Start of ruby text
- 0x0B: RubyTextEnd - End of ruby text
- 0x18: InputText - Indicates text input by the player
- 0x20: PlayerSurname - Replaced with the player's surname from name.txt
- 0x21: PlayerGivenName - Replaced with the player's given name from name.txt
- 0xFF: StringEnd - Marks the end of a string

## Thanks to

This project was made possible thanks to the following open source projects and their documentation on the Mages engine file formats:

- [wetor/MagesTools](https://github.com/wetor/MagesTools/tree/master) - Go implementation of tools for the Mages engine
- [CommitteeOfZero/sc3tools](https://github.com/CommitteeOfZero/sc3tools/tree/main) - Tools for working with SC3 script files
- [CommitteeOfZero/SciAdv.Net](https://github.com/CommitteeOfZero/SciAdv.Net/tree/master) - .NET library for Science Adventure series games

## Note

This tool is for educational and research purposes. All game assets and character data belong to their respective owners (Nintendo).

## License

Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>

All rights reserved.