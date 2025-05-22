# msb2txt

A tool for extracting and converting text data from MSB files from Mages engine games, with specific support for the "Famicom Detective Club" game from Nintendo Switch.

## Tools

### 1. MSB Text Extractor (msb2txt.py)

A Python script that parses MSB files and extracts the text content using the game's character set.

#### Usage

```bash
python msb2txt.py path/to/file.msb
```

Optional arguments:
```
-f, --font     Specify a custom font data file (default: font.txt)
-o, --output   Specify a custom output file (default: same name as input with .txt extension)
-n, --name     Specify a custom player name file (default: name.txt)
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

- 0x00: LineBreak - Inserts a newline character
- 0x01: CharacterName - Indicates the speaking character's name
- 0x02: LineStart - Marks the start of a new line of text
- 0x03: LineEnd - Marks the end of a line of text
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