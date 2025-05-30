# ROM Verifier

A Python script to verify ROM files against a DAT file. This tool helps you ensure your ROM collection matches the expected checksums and identifies any missing or corrupted files.

## Features

- Verifies ROMs against DAT file entries using SHA256 checksums
- Identifies missing ROMs
- Detects bad dumps (ROMs with incorrect checksums)
- Lists unknown files in your ROM folder
- Generates a detailed verification report

## Requirements

- Python 3.6 or higher
- No additional dependencies required (uses only standard library modules)

## Usage

```bash
python rom_verifier.py <dat_file> <roms_folder>
```

Example:
```bash
python rom_verifier.py DatFormat.dat /path/to/roms
```

## Output

The script generates a `verification_report.txt` file containing:

1. Bad Dumps - ROMs that exist but have incorrect checksums
2. Missing ROMs - ROMs listed in the DAT file but not found in your folder
3. Unknown Files - Files in your ROM folder that aren't listed in the DAT file
4. Verified ROMs - ROMs that perfectly match their DAT file entries

A summary is also printed to the console showing the count of verified, bad, missing, and unknown files.

## DAT File Format

The script expects a DAT file in XML format with the following structure:

```xml
<datafile>
    <game name="Game Name">
        <rom name="rom_filename.ext" size="1234" sha256="hash_value"/>
    </game>
</datafile>
```

## Error Handling

The script includes error handling for:
- Missing DAT file or ROM folder
- Invalid DAT file format
- File read errors
- Invalid command-line arguments

## License

This script is provided as-is under the MIT License. Feel free to modify and distribute it as needed. # DatVerifier
