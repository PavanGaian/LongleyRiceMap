#working
import re
import json
import requests
import os

# Regular expression patterns
pattern_callsign = r'Site Analysis Report For:\s+(.*)'
pattern_coordinates = r'Site location:\s+(\d+\.\d+)\s+North\s+/\s+(\d+\.\d+)\s+West'
pattern_terrain = r'Average terrain at\s+(\d+)\s+degrees azimuth:\s+(\d+\.\d+)\s+meters AMSL'
pattern_antenna_height_agl = r'Antenna height:\s+(\d+\.\d+)\s+meters AGL / (\d+\.\d+)\s+meters AMSL'
pattern_antenna_haat = r'Antenna height above average terrain:\s+(\d+\.\d+)\s+meters'
pattern_ground_elevation_amsl = r'Ground elevation:\s+(\d+\.\d+)\s+meters AMSL'

# Function to process each file
def process_site_report(file_path):
    terrain_data = []
    source_coordinates = {
        "latitude": None,
        "longitude": None
    }
    antenna_height_amsl = None
    antenna_height_agl = None
    antenna_haat = None
    ground_elevation_amsl = None
    callsign = None

    # Extract site report name from file path
    base_name = os.path.basename(file_path)
    site_report_name = os.path.splitext(base_name)[0].replace('-site_report', '')

    # Create output folder path
    output_folder = os.path.join('/home/gaian/Downloads', site_report_name)
    os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist

    # Read the file to extract callsign, source coordinates, and heights
    with open(file_path, 'r', encoding='latin-1') as file:
        for line in file:
            # Match callsign
            match_callsign = re.match(pattern_callsign, line)
            if match_callsign:
                callsign = match_callsign.group(1).strip()

            # Match latitude and longitude
            match_coordinates = re.match(pattern_coordinates, line)
            if match_coordinates:
                source_coordinates["latitude"] = float(match_coordinates.group(1))
                source_coordinates["longitude"] = -float(match_coordinates.group(2))  # Convert to negative for West

            # Match antenna height AGL and AMSL
            match_antenna_height_agl = re.match(pattern_antenna_height_agl, line)
            if match_antenna_height_agl:
                antenna_height_agl = float(match_antenna_height_agl.group(1))
                antenna_height_amsl = float(match_antenna_height_agl.group(2))

            # Match antenna HAAT
            match_antenna_haat = re.match(pattern_antenna_haat, line)
            if match_antenna_haat:
                antenna_haat = float(match_antenna_haat.group(1))

            # Match ground elevation AMSL
            match_ground_elevation_amsl = re.match(pattern_ground_elevation_amsl, line)
            if match_ground_elevation_amsl:
                ground_elevation_amsl = float(match_ground_elevation_amsl.group(1))

            # Match terrain data
            match_terrain = re.match(pattern_terrain, line)
            if match_terrain:
                terrain_height = float(match_terrain.group(2))
                terrain_data.append(str(terrain_height))  # Convert to string as per the example

    # Create final JSON structure
    output_data = {
        "latitude": str(source_coordinates["latitude"]),
        "longitude":str(source_coordinates["longitude"]),
        "callsign": str(site_report_name.replace('-site_report','')),
        "antenna_height_AMSL": str(antenna_height_amsl),
        "antenna_height_AGL": str(antenna_height_agl),
        "antenna_haat": str(antenna_haat),
        "ground_elevation_AMSL": str(ground_elevation_amsl),
        "average_terrain_height_AMSL_per_azimuth": terrain_data
    }
    print(output_data)


    # Output as JSON
    output_file = os.path.join(output_folder, f"{site_report_name}.json")
    kml_file= '{site_report_name}.kml'
    with open(output_file, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)


    # Send POST request
    url = 'https://ig.mobiusdtaas.ai/tf-entity-ingestion/v1.0/schemas/667ec6b8d7baf73d1c4e627e/instance?upsert=true'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3Ny1NUVdFRTNHZE5adGlsWU5IYmpsa2dVSkpaWUJWVmN1UmFZdHl5ejFjIn0.eyJleHAiOjE3MTg5MjcxNjksImlhdCI6MTcxODg5MTE2OSwianRpIjoiNzlhMGZkMDktNTc0Mi00NGE4LWEwNDItZDcyYWI3ZTMyYWYzIiwiaXNzIjoiaHR0cDovL2tleWNsb2FrLmtleWNsb2FrLnN2Yy5jbHVzdGVyLmxvY2FsOjgwODAvcmVhbG1zL21hc3RlciIsImF1ZCI6WyJCT0xUWk1BTk5fQk9UIiwiUEFTQ0FMX0lOVEVMTElHRU5DRSIsIk1PTkVUIiwiYWNjb3VudCIsIlZJTkNJIl0sInN1YiI6IjMwMzdkZjZiLWE0YTUtNDE1Ni1hMTI4LWQwZTdkYTM5YzA3OCIsInR5cCI6IkJlYXJlciIsImF6cCI6IkhPTEFDUkFDWSIsInNlc3Npb25fc3RhdGUiOiJjNzE0YTU0Yi1kYjZjLTQzNDctYjJmZS1mZWZmYmU3YTczMDgiLCJuYW1lIjoibW9iaXVzIG1vYml1cyIsImdpdmVuX25hbWUiOiJtb2JpdXMiLCJmYW1pbHlfbmFtZSI6Im1vYml1cyIsInByZWZlcnJlZF91c2VybmFtZSI6InBhc3N3b3JkX3RlbmFudF9tb2JpdXNAbW9iaXVzZHRhYXMuYWkiLCJlbWFpbCI6InBhc3N3b3JkX3RlbmFudF9tb2JpdXNAbW9iaXVzZHRhYXMuYWkiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyIvKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1tYXN0ZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiQk9MVFpNQU5OX0JPVCI6eyJyb2xlcyI6WyJCT0xUWk1BTk5fQk9UX1VTRVIiXX0sIlBBU0NBTF9JTlRFTExJR0VOQ0UiOnsicm9sZXMiOlsiUEFTQ0FMX0lOVEVMTElHRU5DRV9VU0VSIl19LCJNT05FVCI6eyJyb2xlcyI6WyJNT05FVF9VU0VSIl19LCJIT0xBQ1JBQ1kiOnsicm9sZXMiOlsiSE9MQUNSQUNZX1VTRVIiXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfSwiVklOQ0kiOnsicm9sZXMiOlsiVklOQ0lfVVNFUiJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsInNpZCI6ImM3MTRhNTRiLWRiNmMtNDM0Ny1iMmZlLWZlZmZiZTdhNzMwOCIsInRlbmFudElkIjoiMzAzN2RmNmItYTRhNS00MTU2LWExMjgtZDBlN2RhMzljMDc4In0=.DwwruONaKN0rcezDHphMMgMkPt2XajPUiKQWADWiS06nFD-OxxGKSQ2F9xLYsNlOrDHPVLIzIChKkpk-mTSFYCEKyxB8R4jdv0AtZcvFj9yiE92i7twflCiu0z3QOM1lVitHKKLKfwEvvckZ6tGrEav0yITTiuII17XHdxAhQnbtJ130LH-rJqlVsAL66NOY1gTi5hL6b_KZ5GnmAjPC9s2PTJ3i6cDGM6vQt5E_7UNZ_aXWWRTfrgvRoHP4hh0B8kQ--WB47yURExywugSvsoacEzzGC5-PNHZoX8lkrt72S6rMW5-D1fZf5kkZhwi7mG4T0kJvkTl0V4s6PHy-rQ'
    }

    response = requests.post(url, headers=headers, data=json.dumps(output_data,indent = 4))
    print(json.dumps(output_data,indent = 4))
    print(f'Status Code: {response.status_code}, Response: {response.json()}')

# Directory containing the site reports
directory = '/home/gaian/Desktop/lrmfolder'

files = os.listdir(directory)

for file in files:
    if file.endswith('site_report.txt'):
        file_path = os.path.join(directory, file)
        process_site_report(file_path)
#KMFC-LD____(remove this from schema)