#!/usr/bin/env python3
"""
Validate circuit terminations CSV files
Check that all site references in terminations exist in the sites CSVs
"""
import csv
from pathlib import Path

# Load all sites from all site CSV files
sites = {}
site_files = [
    'lab/netbox_dc_sites.csv',
    'lab/netbox_sites_emea.csv',
    'lab/netbox_sites_amer.csv',
    'lab/netbox_sites_apac.csv'
]

print("Loading sites...")
for site_file in site_files:
    if Path(site_file).exists():
        with open(site_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('name'):
                    sites[row['name']] = {
                        'slug': row.get('slug', ''),
                        'file': site_file
                    }
print(f"Loaded {len(sites)} sites\n")

# Check all termination files
term_files = [
    'lab/netbox_dc_circuits_terminations.csv',
    'lab/netbox_circuits_terminations_emea.csv',
    'lab/netbox_circuits_terminations_amer.csv',
    'lab/netbox_circuits_terminations_apac.csv'
]

all_valid = True
for term_file in term_files:
    if not Path(term_file).exists():
        continue

    print(f"Checking {term_file}...")
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        line_num = 1

        for row in reader:
            line_num += 1
            site = row.get('site', '')
            circuit = row.get('circuit', '')

            if site and site not in sites:
                print(f"  ❌ Line {line_num}: Circuit '{circuit}' references unknown site '{site}'")
                all_valid = False

    if all_valid:
        print(f"  ✅ All site references valid\n")
    else:
        print()

if all_valid:
    print("✅ All termination files are valid!")
else:
    print("❌ Some terminations have invalid site references")
