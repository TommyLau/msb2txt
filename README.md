# msb2txt

A tool for extracting and converting text data from MSB files, with specific support for the "Famicom Detective Club" game from Nintendo Switch.

## About

This repository contains tools for working with MSB file formats from Nintendo systems. The primary tool `msb2txt.py` converts hexadecimal values to corresponding characters using the game's character set.

## Usage

Run the script with Python:

```
python msb2txt.py
```

Once running:
1. Enter hex values (e.g., '80D880E3') when prompted
2. The script will convert these values to corresponding characters from the game's font set
3. Type 'q' to quit

## Files

- `msb2txt.py`: Python script that converts hexadecimal values to characters using the font data
- `font.txt`: Character set data extracted from the original "Famicom Detective Club" game from Nintendo Switch. This file contains the complete character set used in the game, including Japanese characters, ASCII symbols, and various special characters.

## How It Works

The script maps hexadecimal values to characters by:
1. Reading the character set from `font.txt`
2. Converting hex input to an index (by subtracting 0x8000)
3. Using this index to find the corresponding character in the font data

## Note

This tool is for educational and research purposes. All game assets and character data belong to their respective owners (Nintendo).