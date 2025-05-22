#!/usr/bin/env python3

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

def main():
    try:
        # Read and process font data
        font_data = read_font_data('font.txt')
        print(f"Font data loaded. Total characters: {len(font_data)}")
        
        # Get user input
        while True:
            hex_input = input("Enter hex values (e.g., '80 D8 80 E3') or 'q' to quit: ")
            
            if hex_input.lower() == 'q':
                break
                
            # Remove all spaces and check if input length is valid
            cleaned_input = hex_input.replace(" ", "")
            if len(cleaned_input) % 2 != 0:
                print("Error: Input length must be divisible by 2")
                continue
                
            # Process input in pairs of 2 characters (1 byte)
            result = ""
            hex_pairs = []
            
            for i in range(0, len(cleaned_input), 4):
                if i+3 < len(cleaned_input):
                    # Take 4 characters (2 bytes) to form a hex value
                    hex_pair = cleaned_input[i:i+4]
                    hex_value = "0x" + hex_pair
                    hex_pairs.append(hex_value)
                    
                    # Convert to integer and map to character
                    try:
                        char_result = hex_to_char(hex_pair, font_data)
                        result += char_result
                    except Exception as e:
                        print(f"Error processing {hex_value}: {e}")
            
            # Print the hex pairs and the result
            print(f"Processed hex pairs: {', '.join(hex_pairs)}")
            print(f"Mapped result: {result}")
            
    except FileNotFoundError:
        print("Error: font.txt file not found")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
