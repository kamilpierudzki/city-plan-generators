import datetime
import json
import os

import requests
from bs4 import BeautifulSoup

from commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, OUTPUT_DIR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "warszawa.json"


def warszawa():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Warszawa",
        TIMESTAMP_ATTR: timestamp,
        READABLE_TIME_ATTR: formatted_date,
        APP_VERSION_ATTR: 1,
        TRAMS_ATTR: trams,
        BUSES_ATTR: buses
    }

    raw_json = json.dumps(json_dict, ensure_ascii=False)
    create_json_file(raw_json, JSON_FILE_NAME)


def get_vehicle_types_dicts():
    _main_page_content = get_main_page_content()
    _filtered_links = get_filtered_links_to_all_timetables(_main_page_content)
    _tram_dict = get_dict_for_vehicle_type("Tramwaj", _filtered_links)
    _bus_dict = get_dict_for_vehicle_type("Autobus", _filtered_links)
    return (_tram_dict, _bus_dict)


def get_main_page_content():
    _r = requests.get("https://www.wtp.waw.pl/rozklady-jazdy/")
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def get_filtered_links_to_all_timetables(main_page_content):
    _all_links = main_page_content.find_all('a')
    _filtered_links = filtered_timetable_button_timetable_button_tile(_all_links)
    return _filtered_links


def filtered_timetable_button_timetable_button_tile(all_links):
    _filtered = []
    for link in all_links:
        try:
            a_class = link.attrs['class']
            is_class_matching = a_class == ['timetable-button', 'timetable-button-tile']
            if is_class_matching:
                _filtered.append(link)
        except KeyError:
            print()
    return _filtered


def get_dict_for_vehicle_type(vehicle_type, filtered_links):
    _vehicle_type_links = filtered_vehicle_type(vehicle_type, filtered_links)
    _vehicle_type_dict = create_dict_number_link_for_vehicle_type(_vehicle_type_links)
    return _vehicle_type_dict


def filtered_vehicle_type(vehicle_type: str, all_vehicles):
    _filtered = []
    for vehicle_link in all_vehicles:
        description = vehicle_link.attrs['aria-label']
        is_vehicle_found_in_description = description.find(vehicle_type) >= 0
        if is_vehicle_found_in_description:
            _filtered.append(vehicle_link)
    return _filtered


def create_dict_number_link_for_vehicle_type(vehicle_links):
    _dict = {}
    for link in vehicle_links:
        line_number = link.text.strip()
        link_to_number_timetable = link.attrs['href']
        _dict[line_number] = link_to_number_timetable
    return _dict


def get_directions(direction_dict):
    _sub_page_content = get_sub_page_content(direction_dict)
    _all_divs = _sub_page_content.find_all('div')

    _div_active_direction = get_div_timetable_line_header_summary_details_direction_item_active(_all_divs)
    _active_direction = read_active_direction(_div_active_direction)

    _div_inactive_direction = get_div_timetable_line_header_summary_details_direction_item(_all_divs)
    if _div_inactive_direction is not None:
        _inactive_direction = read_inactive_direction(_div_inactive_direction)
        return _active_direction, _inactive_direction
    else:
        return _active_direction, None


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def get_div_timetable_line_header_summary_details_direction_item_active(all_divs):
    _active_div = find_active_div_direction(all_divs)
    return _active_div


def find_active_div_direction(all_divs):
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['timetable-line-header-summary-details-direction-item', 'active']
            if is_class_matching:
                return div
        except KeyError:
            print()


def read_active_direction(div_active_direction):
    _div = div_active_direction.div
    _active_direction = _div.text.strip()
    return _active_direction


def get_div_timetable_line_header_summary_details_direction_item(all_divs):
    _inactive_div = find_inactive_div_direction(all_divs)
    return _inactive_div


def find_inactive_div_direction(all_divs):
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['timetable-line-header-summary-details-direction-item']
            if is_class_matching:
                return div
        except KeyError:
            print()


def read_inactive_direction(div_inactive_direction):
    _all_links = div_inactive_direction.find_all('a')
    _filtered_link = filtered_timetable_link_timetable_link_image_timetable_link_image_secondary(_all_links)
    _inactive_direction = read_inactive_direction_from_link(_filtered_link)
    return _inactive_direction


def filtered_timetable_link_timetable_link_image_timetable_link_image_secondary(all_links):
    for link in all_links:
        try:
            a_class = link.attrs['class']
            is_class_matching = a_class == ['timetable-link', 'timetable-link-image', 'timetable-link-image-secondary']
            if is_class_matching:
                return link
        except KeyError:
            print()
    return None


def read_inactive_direction_from_link(link):
    _inactive_direction = link.text.strip()
    return _inactive_direction


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        _vehicle_active_direction, _vehicle_inactive_direction = get_directions(vehicle_data_dict[key])
        _number = key
        row_active = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: _vehicle_active_direction}
        _vehicle_data.append(row_active)
        print(row_active)
        if _vehicle_inactive_direction is not None:
            row_inactive = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: _vehicle_inactive_direction}
            _vehicle_data.append(row_inactive)
            print(row_inactive)
    return _vehicle_data


if __name__ == '__main__':
    warszawa()
