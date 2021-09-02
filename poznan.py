import datetime
import json

import requests
from bs4 import BeautifulSoup

from commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "poznan.json"


def poznan():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Poznań",
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
    _all_divs = _main_page_content.find_all('div')
    _content_div = find_content_div(_all_divs)
    _tram_timetable_links, _bus_timetable_links = get_tram_and_bus_timetable_links(_content_div)
    _tram_dict = create_dict(_tram_timetable_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _tram_dict, _bus_dict


def get_main_page_content():
    _r = requests.get("https://www.mpk.poznan.pl/rozklad-jazdy")
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def find_content_div(all_divs):
    for div in all_divs:
        try:
            a_id = div.attrs['id']
            is_id_matching = a_id == 'content'
            if is_id_matching:
                return div
        except KeyError:
            print()
    return None


def get_tram_and_bus_timetable_links(content_div):
    _all_divs_in_content_div = content_div.find_all('div')
    _tram_timetable_links = get_tram_timetable_links(_all_divs_in_content_div)
    _bus_timetable_links = get_bus_timetable_links(_all_divs_in_content_div)

    return _tram_timetable_links, _bus_timetable_links


def get_tram_timetable_links(all_divs_in_content_div):
    _div_box_tram = find_div_box_tram(all_divs_in_content_div)
    _tram_timetable_links = _div_box_tram.find_all('a')
    return _tram_timetable_links


def find_div_box_tram(all_divs_in_content_div):
    for div in all_divs_in_content_div:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['box_tram']
            if is_class_matching:
                return div
        except KeyError:
            print()
    return None


def get_bus_timetable_links(all_divs_in_content_div):
    _div_box_buses = find_div_box_buses(all_divs_in_content_div)
    _bus_timetable_links = _div_box_buses[0].find_all('a') + _div_box_buses[1].find_all('a')
    return _bus_timetable_links


def find_div_box_buses(all_divs_in_content_div):
    _divs = []
    for div in all_divs_in_content_div:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['box_bus']
            if is_class_matching:
                _divs.append(div)
        except KeyError:
            print()
    return _divs


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = link.attrs['href']
        _dict[line_number] = link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])

        if _directions_for_subpage is None:
            continue

        _number = key
        for direction in _directions_for_subpage:
            _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(_row)
            print(_row)
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_h2s = _sub_page_content.find_all('h2')
    _filtered_h2 = filtered_h2_line_title_name(_all_h2s)
    if _filtered_h2 is not None:
        _filtered_directions = filtered_h2_directions(_filtered_h2)
        return _filtered_directions
    else:
        return None


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_h2_line_title_name(all_h2s):
    for h2 in all_h2s:
        try:
            a_class = h2.attrs['class']
            is_class_matching = a_class == ['line-title__name']
            if is_class_matching:
                return h2
        except KeyError:
            print()
    return None


def filtered_h2_directions(filtered_h2):
    _filtered = filtered_h2.text.split('&leftrightarrow')
    _directions = []
    for direction in _filtered:
        stripped = direction.strip()
        _directions.append(stripped)
    return _directions


if __name__ == '__main__':
    poznan()
