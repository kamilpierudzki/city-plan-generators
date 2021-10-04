import os

CITY_ATTR = "city"
TIMESTAMP_ATTR = "lastUpdateTimestampInMillis"
APP_VERSION_ATTR = "appVersion"
READABLE_TIME_ATTR = "humanReadableLastUpdateTimestamp"
TRAMS_ATTR = "trams"
BUSES_ATTR = "buses"

VEHICLE_NUMBER_ATTR = "number"
VEHICLE_DESTINATION_ATTR = "destination"

OUTPUT_DIR = "../output"


def create_json_file(raw_json, json_file_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    relative_path = os.path.join(OUTPUT_DIR, json_file_name)
    f = open(relative_path, "w")
    f.write(raw_json)
    f.close()
