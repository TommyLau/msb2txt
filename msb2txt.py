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
      -f, --font FILE    Specify a custom font data file (default: font.txt)
      -o, --output FILE  Specify output file (default: same as input with .txt)
      -h, --help         Show this help message and exit
    
    Example:
      python msb2txt.py -f custom_font.txt -o dialog.txt game.msb
      
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
        with open(filename, 'r', encoding='utf-8') as file:
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

def hex_to_char(hex_input, font_data):
    """Convert hex input to corresponding character in font data."""
    try:
        # Convert hex string to integer
        hex_value = int(hex_input, 16)
        
        # Subtract 0x8000 to get index
        index = hex_value - 0x8000
        
        # Check if index is valid
        if 0 <= index < len(font_data):
            return font_data[index]
        else:
            return f"Error: Index {index} out of range (0-{len(font_data)-1})"
    except ValueError:
        return "Error: Invalid hexadecimal input"

class MsbParser:
    """Parser for MSB files from Mages engine."""
    
    # Define command codes
    COMMAND_CODES = {
        0x01: "CharacterName",
        0x02: "DialogueLine",
        0x09: "RubyBase",
        0x0A: "RubyTextStart",
        0x0B: "RubyTextEnd",
        0x20: "PlayerSurname",
        0x21: "PlayerGivenName",
        0x03FF: "End"
    }
    
    def __init__(self, filename, font_data, name_file="name.txt"):
        self.filename = filename
        self.font_data = font_data
        self.raw_data = None
        self.magic = None
        self.version = None
        self.count = None
        self.text_offset = None
        self.strings = []
        self.current_string = ""
        # Read player name
        self.player_surname, self.player_given_name = read_player_name(name_file)
        print(f"Player name: {self.player_surname} {self.player_given_name}")
        
    def parse(self):
        """Parse the MSB file."""
        try:
            with open(self.filename, 'rb') as file:
                self.raw_data = file.read()
                
            # Parse header (magic, version, count, text_offset)
            self.magic = self.raw_data[:4].decode('ascii', errors='ignore')
            self.version = struct.unpack('<i', self.raw_data[4:8])[0]
            self.count = struct.unpack('<i', self.raw_data[8:12])[0]
            self.text_offset = struct.unpack('<i', self.raw_data[12:16])[0]
            
            print(f"File: {self.filename}")
            print(f"Magic: {self.magic}")
            print(f"Version: {self.version}")
            print(f"String Count: {self.count}")
            print(f"Text Offset: {self.text_offset}")
            
            # Seek to text_offset and parse the data from there
            self.parse_text_data()
                
            return True
            
        except Exception as e:
            print(f"Error parsing MSB file: {e}")
            return False
    
    def parse_text_data(self):
        """Parse the text data starting from text_offset."""
        data = self.raw_data[self.text_offset:]
        i = 0
        
        self.current_string = ""
        
        while i < len(data):
            # Get the current byte
            current_byte = data[i]
            
            # Check if it's a character (high bit set)
            if current_byte >= 0x80:
                # Characters are stored as 16-bit big-endian values
                if i + 1 < len(data):
                    # Read the next byte
                    next_byte = data[i + 1]
                    
                    # Combine into a 16-bit value (big-endian)
                    char_code = (current_byte << 8) | next_byte
                    
                    # Convert to character using font data
                    char = hex_to_char(format(char_code, '04x'), self.font_data)
                    self.current_string += char
                    
                    # Move forward 2 bytes
                    i += 2
                else:
                    # Handle case where we're at the end of the file
                    self.current_string += f"[{current_byte:02X}]"
                    i += 1
            else:
                # It's a command byte
                if current_byte == 0x03 and i + 1 < len(data) and data[i + 1] == 0xFF:
                    # Special case for End command (0x03FF)
                    self.current_string += "[End]"
                    
                    # Save the current string and start a new one
                    if self.current_string:
                        self.strings.append(self.current_string)
                        self.current_string = ""
                    
                    i += 2
                elif current_byte == 0x20:
                    # Player surname
                    self.current_string += self.player_surname
                    i += 1
                elif current_byte == 0x21:
                    # Player given name
                    self.current_string += self.player_given_name
                    i += 1
                else:
                    # Regular command
                    cmd_name = self.COMMAND_CODES.get(current_byte, f"Cmd{current_byte:02X}")
                    self.current_string += f"[{cmd_name}]"
                    
                    # Special handling for specific commands
                    if current_byte == 0x01:  # CharacterName
                        # This often indicates a new dialogue entry
                        if self.current_string and len(self.current_string) > len(f"[{cmd_name}]"):
                            self.strings.append(self.current_string)
                            self.current_string = f"[{cmd_name}]"
                    
                    i += 1
        
        # Add the last string if there is one
        if self.current_string:
            self.strings.append(self.current_string)
    
    def save_txt(self, output_file=None):
        """Save decoded strings to a text file."""
        if not output_file:
            output_file = os.path.splitext(self.filename)[0] + ".txt"
            
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f"# Extracted by msb2txt\n")
                file.write(f"# Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>\n")
                file.write(f"# Player name: {self.player_surname} {self.player_given_name}\n\n")
                
                for i, string in enumerate(self.strings):
                    file.write(f"[{i}] {string}\n")
                    
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
  python msb2txt.py game.msb                      # Basic usage
  python msb2txt.py -o output.txt game.msb        # Specify output file
  python msb2txt.py -f custom_font.txt game.msb   # Use custom font data

Copyright (c) 2025 Tommy Lau <tommy.lhg@gmail.com>
        """
    )
    
    parser.add_argument('-f', '--font', default='font.txt', 
                        help='Font data file (default: font.txt)')
    parser.add_argument('-o', '--output', 
                        help='Output text file (default: same as input with .txt extension)')
    parser.add_argument('-n', '--name', default='name.txt',
                        help='Player name file (default: name.txt)')
    parser.add_argument('input_file', 
                        help='Input MSB file to parse')
    
    args = parser.parse_args()
    
    try:
        # Read and process font data
        font_data = read_font_data(args.font)
        print(f"Font data loaded with {len(font_data)} characters.")
        
        # Parse MSB file
        parser = MsbParser(args.input_file, font_data, args.name)
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
