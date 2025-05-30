#!/usr/bin/env python3

import sys
import os
import xml.etree.ElementTree as ET
import hashlib
from pathlib import Path

def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def parse_dat_file(dat_path):
    """Parse the DAT file and return a dictionary of ROM information."""
    tree = ET.parse(dat_path)
    root = tree.getroot()
    
    roms_dict = {}
    for game in root.findall('.//game'):
        rom = game.find('rom')
        if rom is not None:
            rom_name = rom.get('name')
            expected_sha256 = rom.get('sha256', '').lower()
            if rom_name and expected_sha256:
                roms_dict[rom_name] = {
                    'sha256': expected_sha256,
                    'game_name': game.get('name', ''),
                    'size': int(rom.get('size', 0))
                }
    return roms_dict

def verify_roms(dat_path, roms_folder):
    """Verify ROMs in the specified folder against the DAT file."""
    # Parse DAT file
    try:
        roms_dict = parse_dat_file(dat_path)
    except ET.ParseError as e:
        print(f"Error parsing DAT file: {e}")
        return
    except Exception as e:
        print(f"Unexpected error reading DAT file: {e}")
        return

    # Initialize results
    results = {
        'missing': [],
        'bad_dumps': [],
        'verified': [],
        'unknown': []
    }

    # Check each file in the ROMs folder
    roms_path = Path(roms_folder)
    dat_roms = set(roms_dict.keys())
    found_roms = set()

    for file_path in roms_path.glob('*'):
        if file_path.is_file():
            rom_name = file_path.name
            found_roms.add(rom_name)

            if rom_name in roms_dict:
                try:
                    actual_sha256 = calculate_sha256(file_path)
                    expected_sha256 = roms_dict[rom_name]['sha256']
                    
                    if actual_sha256 == expected_sha256:
                        results['verified'].append(rom_name)
                    else:
                        results['bad_dumps'].append({
                            'name': rom_name,
                            'game_name': roms_dict[rom_name]['game_name'],
                            'expected_sha256': expected_sha256,
                            'actual_sha256': actual_sha256
                        })
                except Exception as e:
                    print(f"Error processing {rom_name}: {e}")
            else:
                results['unknown'].append(rom_name)

    # Find missing ROMs
    results['missing'] = list(dat_roms - found_roms)

    return results

def write_report(results, output_file):
    """Write verification results to a file."""
    with open(output_file, 'w') as f:
        f.write("ROM Verification Report\n")
        f.write("=====================\n\n")

        f.write("Bad Dumps:\n")
        f.write("---------\n")
        if results['bad_dumps']:
            for rom in results['bad_dumps']:
                f.write(f"Game: {rom['game_name']}\n")
                f.write(f"ROM: {rom['name']}\n")
                f.write(f"Expected SHA256: {rom['expected_sha256']}\n")
                f.write(f"Actual SHA256: {rom['actual_sha256']}\n")
                f.write("\n")
        else:
            f.write("None found\n\n")

        f.write("Missing ROMs:\n")
        f.write("------------\n")
        if results['missing']:
            for rom in sorted(results['missing']):
                f.write(f"{rom}\n")
        else:
            f.write("None missing\n")
        f.write("\n")

        f.write("Unknown Files:\n")
        f.write("-------------\n")
        if results['unknown']:
            for rom in sorted(results['unknown']):
                f.write(f"{rom}\n")
        else:
            f.write("None found\n")
        f.write("\n")

        f.write("Verified ROMs:\n")
        f.write("-------------\n")
        if results['verified']:
            for rom in sorted(results['verified']):
                f.write(f"{rom}\n")
        else:
            f.write("None verified\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python rom_verifier.py <dat_file> <roms_folder>")
        sys.exit(1)

    dat_file = sys.argv[1]
    roms_folder = sys.argv[2]

    if not os.path.exists(dat_file):
        print(f"Error: DAT file '{dat_file}' not found")
        sys.exit(1)

    if not os.path.exists(roms_folder):
        print(f"Error: ROMs folder '{roms_folder}' not found")
        sys.exit(1)

    print("Verifying ROMs...")
    results = verify_roms(dat_file, roms_folder)
    
    if results:
        output_file = "verification_report.txt"
        write_report(results, output_file)
        print(f"\nVerification complete! Report written to {output_file}")
        
        # Print summary to console
        print("\nSummary:")
        print(f"- Verified: {len(results['verified'])} ROMs")
        print(f"- Bad dumps: {len(results['bad_dumps'])} ROMs")
        print(f"- Missing: {len(results['missing'])} ROMs")
        print(f"- Unknown files: {len(results['unknown'])} files")
    else:
        print("Error occurred during verification")

if __name__ == "__main__":
    main() 