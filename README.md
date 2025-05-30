# ROM Verifier

A Python script to verify ROM files against a DAT file. This tool helps you ensure your ROM collection matches the expected checksums and identifies any missing or corrupted files. It can also automatically fix misnamed ROMs by matching their checksums against the DAT file.

## Features

- Verifies ROMs against DAT file entries using SHA256 checksums
- Automatically renames misnamed ROMs to match DAT entries
- Identifies truly missing ROMs (not found by name or checksum)
- Detects bad dumps (ROMs with incorrect checksums)
- Lists unknown files (don't match any DAT checksums)
- Option to automatically remove unknown files
- Generates a detailed verification report of issues and changes
- Supports custom output report filenames

## Requirements

- Python 3.6 or higher
- No additional dependencies required (uses only standard library modules)

## Usage

Basic usage:
```bash
python rom_verifier.py <dat_file> <roms_folder>
```

To automatically remove unknown files:
```bash
python rom_verifier.py <dat_file> <roms_folder> --remove-unknown
```

To specify a custom output file:
```bash
python rom_verifier.py <dat_file> <roms_folder> --output custom_report.txt
```

Example:
```bash
# Just verify ROMs
python rom_verifier.py DatFormat.dat /path/to/roms

# Verify and remove unknown files
python rom_verifier.py DatFormat.dat /path/to/roms --remove-unknown

# Verify and write to custom report file
python rom_verifier.py DatFormat.dat /path/to/roms --output my_report.txt
```

## Output

The script provides two types of output:

### Console Summary
Shows counts for all categories:
- Verified ROMs (perfect matches)
- Renamed ROMs
- Bad dumps
- Missing ROMs
- Unknown/Removed files

### Report File
The report file (default: `verification_report.txt`) only shows issues and changes:

1. Renamed ROMs - Files that matched a DAT checksum but had the wrong name (automatically renamed)
2. Removed Files - Files that were removed because they didn't match any DAT checksums (only when --remove-unknown is used)
3. Bad Dumps - ROMs that exist but have incorrect checksums
4. Missing ROMs - ROMs listed in the DAT file but not found by name or checksum
5. Unknown Files - Files that don't match any DAT checksums (only shown when --remove-unknown is not used)

Note: Successfully verified ROMs are only shown in the console summary, not in the report file.

If the output file already exists, it will be overwritten. If the file cannot be overwritten for any reason, a new file with a timestamp will be created instead (e.g., `verification_report_1234567890.txt`).

## How It Works

The script uses the following logic to categorize ROMs:

1. If a file's name and checksum both match a DAT entry → Verified ROM
2. If a file's checksum matches a DAT entry but the name doesn't → Misnamed ROM (automatically renamed)
3. If a file's name matches a DAT entry but the checksum doesn't → Bad Dump
4. If a file's checksum doesn't match any DAT entry → Unknown File (optionally removed)
5. If a DAT entry has no matching file by name or checksum → Missing ROM

## Command Line Options

- `dat_file`: Path to the DAT file (required)
- `roms_folder`: Path to the folder containing ROMs (required)
- `--remove-unknown`: Remove files that don't match any DAT checksums (optional)
- `--output`: Specify custom output report filename (optional, default: verification_report.txt)

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
- File read/write errors
- File renaming errors
- File removal errors
- Report file access/write errors
- Invalid command-line arguments

## License

This script is provided as-is under the MIT License. Feel free to modify and distribute it as needed.
