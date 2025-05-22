#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# MSB2TXT - Mages Engine MSB Text Extractor
# Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>
# All rights reserved.
#

import argparse
import struct
import os
import sys

def get_script_dir():
    """Get the directory where the script is located."""
    return os.path.dirname(os.path.abspath(__file__))

def find_file(filename, file_type="file"):
    """Find file in script directory first, then current directory.
    
    Args:
        filename: Name of the file to find
        file_type: Type of file for error message (e.g., "font", "name")
    
    Returns:
        str: Full path to the found file
        
    Raises:
        FileNotFoundError: If file is not found in either location
    """
    # Try script directory first
    script_dir = get_script_dir()
    script_path = os.path.join(script_dir, filename)
    if os.path.isfile(script_path):
        return script_path
    
    # Try current directory
    if os.path.isfile(filename):
        return filename
        
    raise FileNotFoundError(f"{file_type.capitalize()} file '{filename}' not found in script directory ({script_dir}) or current directory")

def find_font_file(font_name):
    """Find font file in script directory first, then current directory."""
    return find_file(font_name, "font")

def find_name_file(name_file):
    """Find name file in script directory first, then current directory."""
    return find_file(name_file, "name")

def print_banner():
    """Print a friendly banner with usage information."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║  MSB2TXT - Mages Engine MSB Text Extractor                    ║
    ║                                                               ║
    ║  Extract text from Mages Engine MSB files                     ║
    ║  Supports Famicom Detective Club and other Mages games        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

    Basic Usage:
      python msb2txt.py path/to/file.msb
    
    Options:
      -f, --font FILE    Specify a custom font data file
                        (defaults: font_ftv1_2.txt for FTV1/FTV2, font_gl.txt for FTCM)
      -o, --output FILE  Specify output file (default: same as input with .txt)
      -h, --help         Show this help message and exit
    
    Example:
      python msb2txt.py game.msb                      # Basic usage (16-bit mode)
      python msb2txt.py -o output.txt game.msb        # Specify output file
      python msb2txt.py -f custom_font.txt game.msb   # Use custom font data
      python msb2txt.py --ftcm game.msb               # Use 32-bit mode for FTCM
      
    Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>
    """
    print(banner)

def read_font_data(filename):
    """Read font data from file and process it by removing newlines and spaces."""
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove carriage returns, newlines, and spaces
    content = content.replace('\r', '').replace('\n', '')
    
    # Remove all spaces (regular and ideographic spaces)
    content = content.replace(' ', '')
    
    # Check for and remove BOM (U+FEFF) at the beginning of the file
    if content and content[0] == '\ufeff':
        content = content[1:]
    
    return content

def read_player_name(filename="name.txt"):
    """Read player name from file and split into surname and given name."""
    try:
        # Find the name file
        name_path = find_name_file(filename)
        with open(name_path, 'r', encoding='utf-8') as file:
            line = file.readline().strip()
            parts = line.split(" ", 1)
            surname = parts[0] if len(parts) > 0 else ""
            given_name = parts[1] if len(parts) > 1 else ""
            return surname, given_name
    except FileNotFoundError:
        print(f"Warning: {filename} not found, using empty names")
        return "", ""
    except Exception as e:
        print(f"Error reading player name: {e}")
        return "", ""

def hex_to_char(index, font_data):
    """Convert hex input to corresponding character in font data.
    
    Args:
        index: Index to convert
        font_data: Font character mapping data
    
    Returns:
        tuple: (character, success) where character is the converted character or error message,
               and success is a boolean indicating whether the conversion succeeded.
    """
    try:
        # Check if index is valid
        if 0 <= index < len(font_data):
            return (font_data[index], True)
        else:
            return (f"Error: Index {index} out of range (0-{len(font_data)-1})", False)
    except ValueError:
        return ("Error: Invalid hexadecimal input", False)

class MsbParser:
    """Parser for MSB files from Mages engine."""
    
    # Define command codes
    COMMAND_CODES = {
        0x00: "LineBreak",
        0x01: "CharacterName",
        0x02: "LineStart",
        0x03: "LineEnd",
        0x04: "SetColor",
        0x09: "RubyBase",
        0x0A: "RubyTextStart",
        0x0B: "RubyTextEnd",
        0x12: "SetMarginLeft",
        0x18: "InputText",
        0x20: "PlayerSurname",
        0x21: "PlayerGivenName",
        0xFF: "StringEnd"
    }

    MSB_SIGNATURE = b'MES\0'
    
    def __init__(self, filename, font_data, name_file="name.txt", is_32bit=False):
        self.filename = filename
        self.font_data = font_data
        self.raw_data = None
        self.magic = None
        self.version = None
        self.count = None
        self.text_offset = None
        self.strings = []
        self.current_string = ""
        self.entries = []  # List of (index, offset) tuples
        # Read player name
        self.player_surname, self.player_given_name = read_player_name(name_file)
        print(f"Player name: {self.player_surname} {self.player_given_name}")
        self.is_32bit = is_32bit

    def read_header(self):
        """Read and verify MSB header structure."""
        # Read and verify magic
        self.magic = self.raw_data[:4]
        if self.magic != self.MSB_SIGNATURE:
            raise ValueError(f"Invalid MSB file: Expected magic {self.MSB_SIGNATURE!r}, got {self.magic!r}")

        # Read version and count
        self.version = struct.unpack('<i', self.raw_data[4:8])[0]
        self.count = struct.unpack('<i', self.raw_data[8:12])[0]
        self.text_offset = struct.unpack('<i', self.raw_data[12:16])[0]

        # Read entry table
        entry_start = 16  # After main header
        for i in range(self.count):
            pos = entry_start + (i * 8)  # Each entry is 8 bytes (2 * int32)
            index, offset = struct.unpack('<ii', self.raw_data[pos:pos + 8])
            self.entries.append((index, offset))
            
        print(f"File: {self.filename}")
        print(f"Magic: {self.magic!r}")
        print(f"Version: {self.version}")
        print(f"String Count: {self.count}")
        print(f"Text Offset: {self.text_offset}")
        
    def parse(self):
        """Parse the MSB file."""
        try:
            with open(self.filename, 'rb') as file:
                self.raw_data = file.read()
                
            # Parse header structure
            self.read_header()
            
            # Seek to text_offset and parse the data from there
            self.parse_text_data()
                
            return True
            
        except Exception as e:
            print(f"Error parsing MSB file: {e}")
            return False
    
    def parse_text_data(self):
        """Parse the text data using the entries table."""
        for entry_idx, (index, offset) in enumerate(self.entries):
            # Reset current string for each entry
            current_string = ""
            
            # Calculate the length of text to read
            i = self.text_offset + offset
            
            while i < len(self.raw_data):
                # Get the current byte
                current_byte = self.raw_data[i]
                
                # Check if it's a character (high bit set)
                if current_byte >= 0x80 and current_byte < 0xFF:
                    # Handle differently based on character encoding
                    if not self.is_32bit:
                        # 16-bit mode (FTV1/FTV2): Read 2 bytes
                        if i + 1 < len(self.raw_data):
                            # Unpack 2 bytes as big-endian unsigned short (16-bit)
                            char_code = struct.unpack('>H', self.raw_data[i:i+2])[0]
                            
                            # Clear highest bit for 16-bit
                            char_code &= 0x7FFF
                            
                            # Move forward 2 bytes
                            i += 2
                    else:
                        # 32-bit mode (FTCM): Read 4 bytes
                        if i + 3 < len(self.raw_data):
                            # Unpack 4 bytes as big-endian unsigned int (32-bit)
                            char_code = struct.unpack('>I', self.raw_data[i:i+4])[0]
                            
                            # Clear highest bit for 32-bit
                            char_code &= 0x7FFFFFFF

                            # Move forward 4 bytes
                            i += 4
                    
                    # Convert to character using font data
                    char, success = hex_to_char(char_code, self.font_data)
                    if success:
                        current_string += char
                    else:
                        # If character conversion failed, add the hex code and show more context
                        print(f"Failed to convert character at entry {entry_idx}, offset {offset + i}: {char_code:08X}")
                        print(f"Following 10 bytes: {' '.join([f'{b:02X}' for b in self.raw_data[i:i+10]])}")
                        current_string += f"[{char_code:08X}]"
                else:
                    # It's a command byte
                    if current_byte == 0xFF:
                        # End of string marker, break the loop
                        break
                    elif current_byte == 0x04 and i + 3 < len(self.raw_data):
                        # Handle SetColor command with RGB values
                        r, g, b = self.raw_data[i+1:i+4]
                        current_string += f"<#{r:02X}{g:02X}{b:02X}>"
                        i += 4  # Skip command byte and 3 RGB bytes
                    elif current_byte == 0x12 and i + 2 < len(self.raw_data):
                        # Handle SetMarginLeft command with RGB values
                        margin_left = struct.unpack('>H', self.raw_data[i+1:i+3])[0]
                        current_string += f"<MarginLeft:{margin_left}>"
                        i += 3  # Skip command byte and 2 RGB bytes
                    elif current_byte == 0x20:
                        # Player surname
                        current_string += self.player_surname
                        i += 1
                    elif current_byte == 0x21:
                        # Player given name
                        current_string += self.player_given_name
                        i += 1
                    else:
                        # Regular command
                        cmd_name = self.COMMAND_CODES.get(current_byte, f"Cmd{current_byte:02X}")
                        current_string += f"[{cmd_name}]"
                        i += 1
            
            # Add the entry's string if there is one
            if current_string:
                # Add entry index to the string for better tracking
                self.strings.append(f"[{index}] {current_string}")
    
    def save_txt(self, output_file=None):
        """Save decoded strings to a text file."""
        if not output_file:
            output_file = os.path.splitext(self.filename)[0] + ".txt"
            
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f"# Extracted by msb2txt\n")
                file.write(f"# Copyright (c) 2025 Tommy Lau\n")
                file.write(f"# Player name: {self.player_surname} {self.player_given_name}\n\n")
                
                for s in self.strings:
                    file.write(f"{s}\n")
                    
            print(f"Decoded text saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving text file: {e}")
            return False

def main():
    # Print banner if no arguments provided
    if len(sys.argv) == 1:
        print_banner()
        sys.exit(0)

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='MSB text extraction tool for Mages engine games',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python msb2txt.py game.msb                      # Basic usage (16-bit mode, uses font_ftv1_2.txt)
  python msb2txt.py -o output.txt game.msb        # Specify output file
  python msb2txt.py -f custom_font.txt game.msb   # Use custom font data
  python msb2txt.py --ftcm game.msb               # Use 32-bit mode for FTCM (uses font_gl.txt)

Game Compatibility:
  FTV1 (default): Famicom Tantei Club: The Missing Heir (uses font_ftv1_2.txt)
  FTV2 (default): Famicom Tantei Club: The Girl Who Stands Behind (uses font_ftv1_2.txt)
  FTCM:           Famicom Tantei Club: Emio – The Smiling Man (uses font_gl.txt)

Note: Font and name files will be searched for in the script directory first, then the current directory.
Font files are automatically selected based on game mode unless overridden with -f/--font.

Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>
        """
    )
    
    parser.add_argument('-f', '--font', 
                        help='Font data file (overrides default font selection)')
    parser.add_argument('-o', '--output', 
                        help='Output text file (default: same as input with .txt extension)')
    parser.add_argument('-n', '--name', default='name.txt',
                        help='Player name file (default: name.txt)')
    parser.add_argument('--ftcm', action='store_true',
                        help='Use 32-bit mode for FTCM (Famicom Tantei Club Mobile)')
    parser.add_argument('input_file', 
                        help='Input MSB file to parse')
    
    args = parser.parse_args()
    
    try:
        # Determine which font file to use
        if args.font:
            # User specified custom font file takes precedence
            font_name = args.font
        else:
            # Use appropriate default font based on mode
            font_name = 'font_gl.txt' if args.ftcm else 'font_ftv1_2.txt'
            
        # Find and read font data
        font_path = find_font_file(font_name)
        font_data = read_font_data(font_path)
        print(f"Font data loaded from {font_path}")
        print(f"Font data loaded with {len(font_data)} characters.")
        print(f"Game: {'FTCM (32-bit)' if args.ftcm else 'FTV1/FTV2 (16-bit)'}")
        
        # Parse MSB file
        parser = MsbParser(args.input_file, font_data, args.name, is_32bit=args.ftcm)
        if parser.parse():
            parser.save_txt(args.output)
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
