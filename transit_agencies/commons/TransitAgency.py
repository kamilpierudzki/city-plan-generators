import datetime
import json
import os

from transit_agencies.commons.verification import verify_links_dictionary, verify_lines_list, \
    verify_stops_dictionary


def _create_json_file(raw_json: str, directory: str, json_file_name: str):
    os.makedirs(directory, exist_ok=True)
    relative_path = os.path.join(directory, json_file_name)
    f = open(relative_path, "w")
    f.write(raw_json)
    f.close()


class TransitAgency:
    _TRANSIT_AGENCY_ATTR = "transit-agency"
    _TIMESTAMP_ATTR = "lastUpdateTimestampInMillis"
    _DATA_VERSION_ATTR = "dataVersion"
    _TIMESTAMP_FORMATTED_ATTR = "lastUpdateFormatted"
    _TRAMS_ATTR = "trams"
    _BUSES_ATTR = "buses"
    _VEHICLE_NUMBER_ATTR = "number"
    _VEHICLE_DESTINATION_ATTR = "destination"
    _OUTPUT_DIR = os.path.join("output", "transit-agencies")

    _STOPS_DATA_VERSION_ATTR = "dataVersion"
    _TRAM_STOPS_ATTR = "tramStops"
    _BUS_STOPS_ATTR = "busStops"
    _STOP_NAME_ATTR = "stopName"
    _STOP_LINES_ATTR = "stopLines"
    _STOPS_OUTPUT_DIR = os.path.join("output", "stops")

    errors: list[str] = []

    def generate_data(self):
        tram_links_dictionary = self._get_tram_links_dictionary()
        tram_links_verification_result = verify_links_dictionary(tram_links_dictionary)
        if tram_links_verification_result.is_error:
            error_message = "Error, " + \
                            self.get_transit_agency_name() + \
                            ". tram links verification failed, message: " + \
                            tram_links_verification_result.error_message
            print(error_message)
            self.errors.append(error_message)
            return

        bus_links_dictionary = self._get_bus_links_dictionary()
        bus_links_verification_result = verify_links_dictionary(bus_links_dictionary)
        if bus_links_verification_result.is_error:
            error_message = "Error, " + \
                            self.get_transit_agency_name() + \
                            "bus links verification failed, message: " + \
                            bus_links_verification_result.error_message
            print(error_message)
            self.errors.append(error_message)
            return

        self._generate_lines_directions_data(tram_links_dictionary, bus_links_dictionary)
        self._generate_stops_data(tram_links_dictionary, bus_links_dictionary)

    def _generate_stops_data(self, tram_links_dictionary: dict[str, str], bus_links_dictionary: dict[str, str]):
        tram_stops_dictionary = self._create_stops_dictionary("tram", tram_links_dictionary)
        tram_stops_dictionary_verification_result = verify_stops_dictionary(tram_stops_dictionary)
        if tram_stops_dictionary_verification_result.is_error:
            error_message = "Error, " + self.get_transit_agency_name() + \
                            "tram stops dictionary verification failed, message: " + \
                            tram_stops_dictionary_verification_result.error_message
            print(error_message)
            self.errors.append(error_message)
            return
        tram_stops_json_dictionary = self._create_vehicle_json_stops_dictionary("tram", tram_stops_dictionary)

        bus_stops_dictionary = self._create_stops_dictionary("bus", bus_links_dictionary)
        bus_stops_dictionary_verification_result = verify_stops_dictionary(bus_stops_dictionary)
        if bus_stops_dictionary_verification_result.is_error:
            error_message = "Error, " + self.get_transit_agency_name() + \
                            "bus stops dictionary verification failed, message: " + \
                            bus_stops_dictionary_verification_result.error_message
            print(error_message)
            self.errors.append(error_message)
            return
        bus_stops_json_dictionary = self._create_vehicle_json_stops_dictionary("bus", bus_stops_dictionary)

        current_time = datetime.datetime.now()
        timestamp = int(current_time.timestamp())
        formatted_date = current_time.strftime("%d-%m-%Y")

        json_dict = {
            self._TRANSIT_AGENCY_ATTR: self.get_transit_agency_name(),
            self._TIMESTAMP_ATTR: timestamp,
            self._TIMESTAMP_FORMATTED_ATTR: formatted_date,
            self._STOPS_DATA_VERSION_ATTR: 1,
            self._TRAM_STOPS_ATTR: tram_stops_json_dictionary,
            self._BUS_STOPS_ATTR: bus_stops_json_dictionary
        }

        raw_json = json.dumps(json_dict, ensure_ascii=False)
        _create_json_file(raw_json, self._STOPS_OUTPUT_DIR, self._get_stops_data_json_file_name())

    def _create_vehicle_json_stops_dictionary(
            self,
            vehicle_type: str,
            vehicle_stops_dictionary: dict[str, list[str]]
    ) -> list[dict]:
        _json_stops_dictionary_list: list[dict] = []

        if len(vehicle_stops_dictionary) == 0:
            return _json_stops_dictionary_list

        for stop in vehicle_stops_dictionary:
            json_stops_dictionary = {
                self._STOP_NAME_ATTR: stop,
                self._STOP_LINES_ATTR: vehicle_stops_dictionary[stop]
            }
            print(
                self.get_transit_agency_name() + ", " +
                vehicle_type + ", " +
                str(json_stops_dictionary)
            )
            _json_stops_dictionary_list.append(json_stops_dictionary)
        if len(_json_stops_dictionary_list) == 0:
            error_message = "Error, " + self.get_transit_agency_name() + " stops json data not created"
            self.errors.append(error_message)
            raise Exception(error_message)
        return _json_stops_dictionary_list

    def _create_stops_dictionary(self, vehicle_type: str, vehicle_links_dictionary) -> dict[str, list[str]]:
        _stops_dictionary: dict[str, list[str]] = {}

        if len(vehicle_links_dictionary) == 0:
            return _stops_dictionary

        for key in vehicle_links_dictionary:
            try:
                all_stops_for_link = self._get_all_stops_for_link(vehicle_links_dictionary[key])
                for stop in all_stops_for_link:
                    try:
                        _stops_dictionary[stop] = _stops_dictionary[stop] + [key]
                    except KeyError:
                        _stops_dictionary[stop] = [key]
                    print(
                        self.get_transit_agency_name() + ", " +
                        vehicle_type + ", " +
                        stop + ": " + str(_stops_dictionary[stop])
                    )
            except Exception as e:
                error_message = "Error, " + e.__str__() + ", link " + vehicle_links_dictionary[key] + " is broken"
                self.errors.append(error_message)
                print(error_message)
                continue
        if len(_stops_dictionary) == 0:
            error_message = "Error, stops data not created"
            self.errors.append(error_message)
            raise Exception(error_message)
        return _stops_dictionary

    def _generate_lines_directions_data(
            self,
            tram_links_dictionary: dict[str, str],
            bus_links_dictionary: dict[str, str]
    ):
        tram_lines_list = self._get_vehicle_lines(tram_links_dictionary)
        tram_lines_list_verification_result = verify_lines_list(tram_lines_list)
        if tram_lines_list_verification_result.is_error:
            error_message = "Error, " + self.get_transit_agency_name() + \
                            " tram lines list verification failed, message: " + \
                            tram_lines_list_verification_result.error_message
            print(error_message)
            self.errors.append(error_message)
            return

        bus_lines_list = self._get_vehicle_lines(bus_links_dictionary)
        bus_lines_list_verification_result = verify_lines_list(bus_lines_list)
        if bus_lines_list_verification_result.is_error:
            error_message = "Error, " + self.get_transit_agency_name() + \
                            " bus lines list verification failed, message: " + \
                            bus_lines_list_verification_result.error_message
            print(error_message)
            self.errors.append(error_message)
            return

        current_time = datetime.datetime.now()
        timestamp = int(current_time.timestamp())
        formatted_date = current_time.strftime("%d-%m-%Y")

        json_dict = {
            self._TRANSIT_AGENCY_ATTR: self.get_transit_agency_name(),
            self._TIMESTAMP_ATTR: timestamp,
            self._TIMESTAMP_FORMATTED_ATTR: formatted_date,
            self._DATA_VERSION_ATTR: 1,
            self._TRAMS_ATTR: tram_lines_list,
            self._BUSES_ATTR: bus_lines_list
        }

        raw_json = json.dumps(json_dict, ensure_ascii=False)
        _create_json_file(raw_json, self._OUTPUT_DIR, self._get_line_direction_json_file_name())

    def _get_vehicle_lines(self, vehicle_links_dictionary: dict[str, str]) -> list[dict[str:str]]:
        vehicle_data: list[dict] = []
        for key in vehicle_links_dictionary:
            try:
                _directions_for_subpage: list[str] = self._get_directions_for_sub_page(vehicle_links_dictionary[key])
                _number = key
                for direction in _directions_for_subpage:
                    row = {self._VEHICLE_NUMBER_ATTR: _number, self._VEHICLE_DESTINATION_ATTR: direction}
                    vehicle_data.append(row)
                    print(self.get_transit_agency_name() + ", " + str(row))
            except Exception as e:
                error_message = "Error, " + \
                                self.get_transit_agency_name() + \
                                ". _get_vehicle_lines, message: " + \
                                str(e) + ", link " + \
                                vehicle_links_dictionary[key]
                print(error_message)
                self.errors.append(error_message)
                continue
        return vehicle_data

    def get_transit_agency_name(self) -> str:
        raise Exception("_get_transit_agency_name not implemented")

    def _get_line_direction_json_file_name(self) -> str:
        raise Exception("_get_json_file_name not implemented")

    def _get_stops_data_json_file_name(self) -> str:
        raise Exception("_get_stops_data_json_file_name not implemented")

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        raise Exception("_get_tram_links_dictionary not implemented")

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        raise Exception("_get_bus_links_dictionary not implemented")

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        raise Exception("_get_directions_for_sub_page not implemented")

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        raise Exception("_get_all_stops_for_link not implemented")
