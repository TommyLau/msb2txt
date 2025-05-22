#!/usr/bin/env python3
import os
import sys
import struct
import argparse
from pathlib import Path

class MPKHeader:
    MPK_SIGNATURE = b'MPK\0'
    FILE_HEADER_LENGTH = 256
    FIRST_ENTRY_OFFSET = 64
    FILENAME_LENGTH = 224  # 256 - 32 (header fields)

class MPKFile:
    def __init__(self):
        self.filename = ""
        self.id = 0
        self.is_compressed = False
        self.offset = 0
        self.size = 0
        self.actual_size = 0  # For compressed files

class MPKExtractor:
    def __init__(self, mpk_path):
        self.mpk_path = Path(mpk_path)
        self.files = []
        self.version_major = 0
        self.version_minor = 0
        self.mpk_data = None  # Store entire MPK file data

    def load_mpk(self):
        # Read entire MPK file into memory
        with open(self.mpk_path, 'rb') as f:
            self.mpk_data = f.read()
            print(f"Loaded {len(self.mpk_data):,} bytes into memory")

    def read_header(self):
        if not self.mpk_data:
            raise ValueError("MPK file not loaded. Call load_mpk() first.")

        # Create a memoryview for efficient slicing
        data = memoryview(self.mpk_data)
        
        # Read and verify magic number
        if data[:4].tobytes() != MPKHeader.MPK_SIGNATURE:
            raise ValueError("Invalid MPK file format")

        # Read version (4 bytes total)
        self.version_minor = struct.unpack('<H', data[4:6].tobytes())[0]  # 2 bytes for minor
        self.version_major = struct.unpack('<H', data[6:8].tobytes())[0]  # 2 bytes for major
        
        # Read file count
        file_count = struct.unpack('<Q', data[8:16].tobytes())[0]  # 64-bit integer for count

        # Read file entries
        for i in range(file_count):
            mpk_file = MPKFile()
            
            # Calculate entry position
            entry_pos = MPKHeader.FIRST_ENTRY_OFFSET + (i * MPKHeader.FILE_HEADER_LENGTH)
            entry_data = data[entry_pos:entry_pos + MPKHeader.FILE_HEADER_LENGTH]
            
            # Read entry header
            mpk_file.is_compressed = struct.unpack('<I', entry_data[0:4].tobytes())[0] == 1
            mpk_file.id = struct.unpack('<I', entry_data[4:8].tobytes())[0]
            mpk_file.offset = struct.unpack('<Q', entry_data[8:16].tobytes())[0]
            mpk_file.size = struct.unpack('<Q', entry_data[16:24].tobytes())[0]
            mpk_file.actual_size = struct.unpack('<Q', entry_data[24:32].tobytes())[0]
            
            # Read filename (224 bytes, null-terminated UTF-8)
            filename_bytes = entry_data[32:32+MPKHeader.FILENAME_LENGTH].tobytes()
            mpk_file.filename = filename_bytes.split(b'\0')[0].decode('utf-8').strip()
            
            self.files.append(mpk_file)

    def extract_files(self):
        # Use MPK filename without extension as output directory
        output_dir = self.mpk_path.stem
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for mpk_file in self.files:
            print(f"  {mpk_file.filename} ({'compressed' if mpk_file.is_compressed else 'uncompressed'})")
        
            file_path = output_path / mpk_file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # TODO: Add decompression support if is_compressed is True
            if mpk_file.is_compressed:
                print(f"Warning: Compressed file {mpk_file.filename} will be extracted as-is (decompression not implemented)")

            # Get file data directly from mpk_data
            file_data = self.mpk_data[mpk_file.offset:mpk_file.offset + mpk_file.size]
            with open(file_path, 'wb') as out_file:
                out_file.write(file_data)

def main():
    parser = argparse.ArgumentParser(description='Extract files from MPK archive')
    parser.add_argument('mpk_file', help='Path to the MPK file')
    args = parser.parse_args()

    try:
        extractor = MPKExtractor(args.mpk_file)
        print(f"Reading MPK file: {args.mpk_file}")
        
        # Load entire MPK file into memory
        extractor.load_mpk()
        
        # Parse headers and file entries
        extractor.read_header()
        print(f"MPK Version: {extractor.version_major}.{extractor.version_minor}")
        print(f"Found {len(extractor.files)} files")
        
        # List files
        output_dir = Path(args.mpk_file).stem
        print(f"Files will be extracted to: {output_dir}/")

        # Extract files
        print("\nExtracting files...")
        extractor.extract_files()
        print("Extraction complete!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
