import datetime
import json

import requests
from bs4 import BeautifulSoup

from commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

MAIN_PAGE_URL = "https://www.wroclaw.pl/rozklady-jazdy"

JSON_FILE_NAME = "wroclaw.json"

TRAM_SEARCH_KEY = "tram"
BUS_SEARCH_KEY = "auto"


def wroclaw():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Wrocław",
        TIMESTAMP_ATTR: timestamp,
        READABLE_TIME_ATTR: formatted_date,
        APP_VERSION_ATTR: 1,
        TRAMS_ATTR: trams,
        BUSES_ATTR: buses
    }

    raw_json = json.dumps(json_dict, ensure_ascii=False)
    create_json_file(raw_json, JSON_FILE_NAME)


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        sub_page_content = get_sub_page_content(vehicle_data_dict[key])
        directions = get_directions(sub_page_content)
        number = key
        for direction in directions:
            row = {VEHICLE_NUMBER_ATTR: number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(row)
            print(row)
    return _vehicle_data


def get_directions(sub_page_content):
    _all_h4 = get_all_h4(sub_page_content)
    _filtered_h4s = filtered_h4s_class_text_normal(_all_h4)
    _first_two_h4s = get_first_two_h4s(_filtered_h4s)
    return _first_two_h4s


def get_first_two_h4s(filtered_h4s):
    first_direction = filtered_h4s[0].contents[0]
    second_direction = filtered_h4s[0].contents[2]
    _result = [first_direction, second_direction]
    return _result


def filtered_h4s_class_text_normal(all_h4):
    _filtered = []
    for h4 in all_h4:
        try:
            a_class = h4.attrs['class']
            is_class_matching = a_class == ['text-normal']
            if is_class_matching:
                _filtered.append(h4)
        except KeyError:
            print()
    return _filtered


def get_all_h4(sub_page_content):
    _all_h4 = sub_page_content.find_all('h4')
    return _all_h4


def get_vehicle_types_dicts():
    _all_filtered_timetables = get_all_filtered_timetables()
    _tram_links = filtered_links_for_vehicle_type(TRAM_SEARCH_KEY, _all_filtered_timetables)
    _bus_links = filtered_links_for_vehicle_type(BUS_SEARCH_KEY, _all_filtered_timetables)

    _tram_dict = create_dict_number_link_for_vehicle_type(_tram_links)
    _bus_dict = create_dict_number_link_for_vehicle_type(_bus_links)
    return _tram_dict, _bus_dict


def create_dict_number_link_for_vehicle_type(vehicle_type_links):
    _dict = {}
    for link_for_vehicle_type in vehicle_type_links:
        number = link_for_vehicle_type.text.strip()
        link = find_link_to_sub_page(link_for_vehicle_type)
        _dict[number] = link
    return _dict


def find_link_to_sub_page(link_for_vehicle_type):
    _link = MAIN_PAGE_URL + link_for_vehicle_type.attrs['href']
    return _link


def filtered_links_for_vehicle_type(search_key, all_timetables):
    _filtered_vehicle_type_tables = filtered_vehicle_type_tables(search_key, all_timetables)
    _all_links_in_tables = _filter_all_links_for_tables(_filtered_vehicle_type_tables)
    return _all_links_in_tables


def _filter_all_links_for_tables(vehicle_type_tables):
    _result = []
    for table in vehicle_type_tables:
        _all_links = table.find_all('a')
        for link in _all_links:
            _result.append(link)
    return _result


def filtered_vehicle_type_tables(search_key, all_timetables):
    _filtered_tables = []
    for table in all_timetables:
        table_text = table.text.casefold()
        if search_key in table_text:
            _filtered_tables.append(table)
    return _filtered_tables


def get_all_filtered_timetables():
    _main_page_content = get_main_page_content()
    _filtered_timetables = get_all_filtered_tables(_main_page_content)
    return _filtered_timetables


def get_all_filtered_tables(main_page_content):
    _all_tables = main_page_content.find_all('table')
    _filtered_tables = filtered_tables(_all_tables)
    return _filtered_tables


def filtered_tables(all_tables):
    _filtered = []
    for link in all_tables:
        try:
            a_class = link.attrs['class']
            is_class_matching = a_class == ['table', 'table-bordered', 'table-schedule']
            if is_class_matching:
                _filtered.append(link)
        except KeyError:
            print()
    return _filtered


def get_main_page_content():
    _r = requests.get(MAIN_PAGE_URL)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


if __name__ == '__main__':
    wroclaw()
