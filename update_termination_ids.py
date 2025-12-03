#!/usr/bin/env python3
"""
Update circuit terminations to use numeric site IDs
Parse sites_with_ids.csv to get site name -> ID mapping
Then update all termination files
"""
import csv
from pathlib import Path

# Build site name -> ID mapping from the exported NetBox sites
site_to_id = {}

# Since user provided the data inline, let me parse from the key DC sites
# EMEA-DC-CLOUD = 387
# EMEA-DC-ONPREM = 388
# APAC-DC-CLOUD = 389
# APAC-DC-ONPREM = 390
# AMER-DC-CLOUD = 391
# AMER-DC-ONPREM = 392

# Parse from inline data (extracting just the sites we need from user's export)
sites_data = """EMEA-DC-CLOUD,387
EMEA-DC-ONPREM,388
APAC-DC-CLOUD,389
APAC-DC-ONPREM,390
AMER-DC-CLOUD,391
AMER-DC-ONPREM,392
FR-Agency1,95
FR-Agency2,96
DE-Agency1,97
DE-Agency2,98
GB-Agency1,99
GB-Agency2,100
NL-Agency1,101
NL-Agency2,102
BE-Agency1,103
BE-Agency2,104
LU-Agency1,105
LU-Agency2,106
CH-Agency1,107
CH-Agency2,108
AT-Agency1,109
AT-Agency2,110
IE-Agency1,111
IE-Agency2,112
MC-Agency1,113
MC-Agency2,114
ES-Agency1,115
ES-Agency2,116
PT-Agency1,117
PT-Agency2,118
IT-Agency1,119
IT-Agency2,120
GR-Agency1,121
GR-Agency2,122
MT-Agency1,123
MT-Agency2,124
CY-Agency1,125
CY-Agency2,126
AD-Agency1,127
AD-Agency2,128
SM-Agency1,129
SM-Agency2,130
SE-Agency1,131
SE-Agency2,132
NO-Agency1,133
NO-Agency2,134
DK-Agency1,135
DK-Agency2,136
FI-Agency1,137
FI-Agency2,138
IS-Agency1,139
IS-Agency2,140
PL-Agency1,141
PL-Agency2,142
CZ-Agency1,143
CZ-Agency2,144
HU-Agency1,145
HU-Agency2,146
RO-Agency1,147
RO-Agency2,148
BG-Agency1,149
BG-Agency2,150
SK-Agency1,151
SK-Agency2,152
SI-Agency1,153
SI-Agency2,154
HR-Agency1,155
HR-Agency2,156
RS-Agency1,157
RS-Agency2,158
UA-Agency1,159
UA-Agency2,160
LT-Agency1,161
LT-Agency2,162
LV-Agency1,163
LV-Agency2,164
EE-Agency1,165
EE-Agency2,166
AE-Agency1,167
AE-Agency2,168
SA-Agency1,169
SA-Agency2,170
QA-Agency1,171
QA-Agency2,172
KW-Agency1,173
KW-Agency2,174
BH-Agency1,175
BH-Agency2,176
OM-Agency1,177
OM-Agency2,178
IL-Agency1,179
IL-Agency2,180
JO-Agency1,181
JO-Agency2,182
LB-Agency1,183
LB-Agency2,184
TR-Agency1,185
TR-Agency2,186
ZA-Agency1,187
ZA-Agency2,188
DZ-Agency1,189
DZ-Agency2,190
MA-Agency1,191
MA-Agency2,192
NG-Agency1,193
NG-Agency2,194
KE-Agency1,195
KE-Agency2,196
GH-Agency1,197
GH-Agency2,198
TN-Agency1,199
TN-Agency2,200
SN-Agency1,201
SN-Agency2,202
CI-Agency1,203
CI-Agency2,204
MU-Agency1,205
MU-Agency2,206
CN-Agency1,207
CN-Agency2,208
JP-Agency1,209
JP-Agency2,210
KR-Agency1,211
KR-Agency2,212
TW-Agency1,213
TW-Agency2,214
HK-Agency1,215
HK-Agency2,216
MO-Agency1,217
MO-Agency2,218
MN-Agency1,219
MN-Agency2,220
SG-Agency1,221
SG-Agency2,222
MY-Agency1,223
MY-Agency2,224
TH-Agency1,225
TH-Agency2,226
ID-Agency1,227
ID-Agency2,228
VN-Agency1,229
VN-Agency2,230
PH-Agency1,231
PH-Agency2,232
MM-Agency1,233
MM-Agency2,234
KH-Agency1,235
KH-Agency2,236
LA-Agency1,237
LA-Agency2,238
BN-Agency1,239
BN-Agency2,240
TL-Agency1,241
TL-Agency2,242
IN-Agency1,243
IN-Agency2,244
PK-Agency1,245
PK-Agency2,246
BD-Agency1,247
BD-Agency2,248
LK-Agency1,249
LK-Agency2,250
NP-Agency1,251
NP-Agency2,252
BT-Agency1,253
BT-Agency2,254
MV-Agency1,255
MV-Agency2,256
AF-Agency1,257
AF-Agency2,258
AU-Agency1,259
AU-Agency2,260
NZ-Agency1,261
NZ-Agency2,262
PG-Agency1,263
PG-Agency2,264
FJ-Agency1,265
FJ-Agency2,266
WS-Agency1,267
WS-Agency2,268
TO-Agency1,269
TO-Agency2,270
VU-Agency1,271
VU-Agency2,272
SB-Agency1,273
SB-Agency2,274
NC-Agency1,275
NC-Agency2,276
PF-Agency1,277
PF-Agency2,278
GU-Agency1,279
GU-Agency2,280
PW-Agency1,281
PW-Agency2,282
FM-Agency1,283
FM-Agency2,284
MH-Agency1,285
MH-Agency2,286
KI-Agency1,287
KI-Agency2,288
NR-Agency1,289
NR-Agency2,290
TV-Agency1,291
TV-Agency2,292
KZ-Agency1,293
KZ-Agency2,294
UZ-Agency1,295
UZ-Agency2,296
TM-Agency1,297
TM-Agency2,298
KG-Agency1,299
KG-Agency2,300
TJ-Agency1,301
TJ-Agency2,302
US-Agency1,303
US-Agency2,304
CA-Agency1,305
CA-Agency2,306
MX-Agency1,307
MX-Agency2,308
GT-Agency1,309
GT-Agency2,310
BZ-Agency1,311
BZ-Agency2,312
HN-Agency1,313
HN-Agency2,314
SV-Agency1,315
SV-Agency2,316
NI-Agency1,317
NI-Agency2,318
CR-Agency1,319
CR-Agency2,320
PA-Agency1,321
PA-Agency2,322
CU-Agency1,323
CU-Agency2,324
JM-Agency1,325
JM-Agency2,326
HT-Agency1,327
HT-Agency2,328
DO-Agency1,329
DO-Agency2,330
PR-Agency1,331
PR-Agency2,332
BS-Agency1,333
BS-Agency2,334
TT-Agency1,335
TT-Agency2,336
BB-Agency1,337
BB-Agency2,338
LC-Agency1,339
LC-Agency2,340
GD-Agency1,341
GD-Agency2,342
VC-Agency1,343
VC-Agency2,344
AG-Agency1,345
AG-Agency2,346
DM-Agency1,347
DM-Agency2,348
KN-Agency1,349
KN-Agency2,350
AW-Agency1,351
AW-Agency2,352
CW-Agency1,353
CW-Agency2,354
KY-Agency1,355
KY-Agency2,356
VG-Agency1,357
VG-Agency2,358
VI-Agency1,359
VI-Agency2,360
BR-Agency1,361
BR-Agency2,362
AR-Agency1,363
AR-Agency2,364
CO-Agency1,365
CO-Agency2,366
PE-Agency1,367
PE-Agency2,368
VE-Agency1,369
VE-Agency2,370
CL-Agency1,371
CL-Agency2,372
EC-Agency1,373
EC-Agency2,374
BO-Agency1,375
BO-Agency2,376
PY-Agency1,377
PY-Agency2,378
UY-Agency1,379
UY-Agency2,380
GY-Agency1,381
GY-Agency2,382
SR-Agency1,383
SR-Agency2,384
GF-Agency1,385
GF-Agency2,386"""

for line in sites_data.strip().split('\n'):
    if ',' in line:
        name, id_str = line.split(',')
        site_to_id[name] = id_str

print(f"Loaded {len(site_to_id)} site name -> ID mappings\n")

# Update termination files
term_files = [
    'lab/netbox_dc_circuits_terminations.csv',
    'lab/netbox_circuits_terminations_emea.csv',
    'lab/netbox_circuits_terminations_amer.csv',
    'lab/netbox_circuits_terminations_apac.csv'
]

for term_file in term_files:
    if not Path(term_file).exists():
        continue

    print(f"Processing {term_file}...")

    # Read terminations
    terminations = []
    updated_count = 0
    missing_count = 0

    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            site_name = row.get('site', '')

            # Convert site name to ID
            if site_name and site_name in site_to_id:
                term_id = site_to_id[site_name]
                updated_count += 1
            else:
                term_id = ''
                if site_name:
                    print(f"  ⚠️  Site not found: {site_name}")
                    missing_count += 1

            new_row = {
                'circuit': row['circuit'],
                'term_side': row['term_side'],
                'termination_type': 'dcim.site',
                'termination_id': term_id,
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': row['description']
            }
            terminations.append(new_row)

    # Write with termination_type and numeric termination_id
    fieldnames = ['circuit', 'term_side', 'termination_type', 'termination_id',
                  'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {updated_count} terminations with numeric IDs")
    if missing_count > 0:
        print(f"  ⚠️  {missing_count} terminations missing site IDs")

print("\n✅ All termination files updated with numeric site IDs")
