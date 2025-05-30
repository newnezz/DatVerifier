#!/usr/bin/env python3

import sys
import os
import xml.etree.ElementTree as ET
import hashlib
from pathlib import Path
import shutil
import argparse
import time

def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def parse_dat_file(dat_path):
    """Parse the DAT file and return dictionaries of ROM information."""
    tree = ET.parse(dat_path)
    root = tree.getroot()
    
    roms_by_name = {}
    roms_by_sha256 = {}
    
    for game in root.findall('.//game'):
        rom = game.find('rom')
        if rom is not None:
            rom_name = rom.get('name')
            expected_sha256 = rom.get('sha256', '').lower()
            if rom_name and expected_sha256:
                rom_info = {
                    'sha256': expected_sha256,
                    'game_name': game.get('name', ''),
                    'size': int(rom.get('size', 0))
                }
                roms_by_name[rom_name] = rom_info
                roms_by_sha256[expected_sha256] = {'name': rom_name, **rom_info}
    
    return roms_by_name, roms_by_sha256

def verify_roms(dat_path, roms_folder, remove_unknown=False):
    """Verify ROMs in the specified folder against the DAT file."""
    try:
        roms_by_name, roms_by_sha256 = parse_dat_file(dat_path)
    except ET.ParseError as e:
        print(f"Error parsing DAT file: {e}")
        return
    except Exception as e:
        print(f"Unexpected error reading DAT file: {e}")
        return

    results = {
        'missing': [],           # ROMs in DAT but not found by name or checksum
        'bad_dumps': [],         # ROMs that don't match any DAT checksum
        'verified': [],          # ROMs that match both name and checksum
        'renamed': [],           # ROMs that matched checksum but had wrong name
        'unknown': [],           # Files not in DAT and don't match any checksum
        'removed': []            # Files that were removed (when remove_unknown is True)
    }

    roms_path = Path(roms_folder)
    processed_sha256s = set()
    
    # First pass: Check files by name and build SHA256 map
    for file_path in roms_path.glob('*'):
        if not file_path.is_file():
            continue
            
        rom_name = file_path.name
        try:
            actual_sha256 = calculate_sha256(file_path)
            
            # Case 1: Perfect match (name and checksum)
            if rom_name in roms_by_name and actual_sha256 == roms_by_name[rom_name]['sha256']:
                results['verified'].append(rom_name)
                processed_sha256s.add(actual_sha256)
                continue
                
            # Case 2: Checksum matches but name doesn't (misnamed ROM)
            if actual_sha256 in roms_by_sha256 and rom_name != roms_by_sha256[actual_sha256]['name']:
                correct_name = roms_by_sha256[actual_sha256]['name']
                new_path = file_path.parent / correct_name
                
                # Rename the file
                try:
                    shutil.move(str(file_path), str(new_path))
                    results['renamed'].append({
                        'old_name': rom_name,
                        'new_name': correct_name,
                        'game_name': roms_by_sha256[actual_sha256]['game_name']
                    })
                    processed_sha256s.add(actual_sha256)
                    continue
                except Exception as e:
                    print(f"Error renaming {rom_name} to {correct_name}: {e}")
            
            # Case 3: Unknown file (doesn't match any DAT checksum)
            if actual_sha256 not in roms_by_sha256:
                if remove_unknown:
                    try:
                        os.remove(file_path)
                        results['removed'].append(rom_name)
                    except Exception as e:
                        print(f"Error removing unknown file {rom_name}: {e}")
                        results['unknown'].append(rom_name)
                else:
                    results['unknown'].append(rom_name)
                continue
                
            # Case 4: Bad dump (name matches but checksum doesn't)
            if rom_name in roms_by_name:
                results['bad_dumps'].append({
                    'name': rom_name,
                    'game_name': roms_by_name[rom_name]['game_name'],
                    'expected_sha256': roms_by_name[rom_name]['sha256'],
                    'actual_sha256': actual_sha256
                })
                
        except Exception as e:
            print(f"Error processing {rom_name}: {e}")

    # Find truly missing ROMs (not found by name or checksum)
    for sha256, rom_info in roms_by_sha256.items():
        if sha256 not in processed_sha256s:
            results['missing'].append(rom_info['name'])

    return results

def write_report(results, output_file, remove_unknown=False):
    """Write verification results to a file."""
    # Remove existing report file if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except Exception as e:
            print(f"Warning: Could not remove existing report file: {e}")
            # Generate unique filename instead
            base, ext = os.path.splitext(output_file)
            output_file = f"{base}_{int(time.time())}{ext}"
            print(f"Writing to alternate file: {output_file}")

    with open(output_file, 'w') as f:
        f.write("ROM Verification Report\n")
        f.write("=====================\n\n")

        # Only write sections for issues and changes
        if results['renamed']:
            f.write("Renamed ROMs (Matched checksum but had wrong name):\n")
            f.write("-----------------------------------------------\n")
            for rom in results['renamed']:
                f.write(f"Game: {rom['game_name']}\n")
                f.write(f"Old name: {rom['old_name']}\n")
                f.write(f"Renamed to: {rom['new_name']}\n")
                f.write("\n")

        if remove_unknown and results['removed']:
            f.write("Removed Unknown Files:\n")
            f.write("--------------------\n")
            for rom in sorted(results['removed']):
                f.write(f"{rom}\n")
            f.write("\n")

        if results['bad_dumps']:
            f.write("Bad Dumps (Incorrect checksum):\n")
            f.write("-----------------------------\n")
            for rom in results['bad_dumps']:
                f.write(f"Game: {rom['game_name']}\n")
                f.write(f"ROM: {rom['name']}\n")
                f.write(f"Expected SHA256: {rom['expected_sha256']}\n")
                f.write(f"Actual SHA256: {rom['actual_sha256']}\n")
                f.write("\n")

        if results['missing']:
            f.write("Missing ROMs (Not found by name or checksum):\n")
            f.write("----------------------------------------\n")
            for rom in sorted(results['missing']):
                f.write(f"{rom}\n")
            f.write("\n")

        if not remove_unknown and results['unknown']:
            f.write("Unknown Files (Don't match any DAT checksums):\n")
            f.write("-----------------------------------------\n")
            for rom in sorted(results['unknown']):
                f.write(f"{rom}\n")
            f.write("\n")

def main():
    parser = argparse.ArgumentParser(description='Verify ROM files against a DAT file')
    parser.add_argument('dat_file', help='Path to the DAT file')
    parser.add_argument('roms_folder', help='Path to the folder containing ROMs')
    parser.add_argument('--remove-unknown', action='store_true',
                      help='Remove files that don\'t match any DAT checksums')
    parser.add_argument('--output', default='verification_report.txt',
                      help='Output report filename (default: verification_report.txt)')
    
    args = parser.parse_args()

    if not os.path.exists(args.dat_file):
        print(f"Error: DAT file '{args.dat_file}' not found")
        sys.exit(1)

    if not os.path.exists(args.roms_folder):
        print(f"Error: ROMs folder '{args.roms_folder}' not found")
        sys.exit(1)

    print("Verifying ROMs...")
    results = verify_roms(args.dat_file, args.roms_folder, args.remove_unknown)
    
    if results:
        write_report(results, args.output, args.remove_unknown)
        print(f"\nVerification complete! Report written to {args.output}")
        
        # Print summary to console
        print("\nSummary:")
        print(f"- Verified: {len(results['verified'])} ROMs")
        print(f"- Renamed: {len(results['renamed'])} ROMs")
        print(f"- Bad dumps: {len(results['bad_dumps'])} ROMs")
        print(f"- Missing: {len(results['missing'])} ROMs")
        if args.remove_unknown:
            print(f"- Removed: {len(results['removed'])} unknown files")
        else:
            print(f"- Unknown files: {len(results['unknown'])} files")
    else:
        print("Error occurred during verification")

if __name__ == "__main__":
    main() 