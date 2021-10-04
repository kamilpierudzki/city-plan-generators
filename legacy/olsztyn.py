import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "olsztyn.json"
MAIN_PAGE_LINK = "https://www.zdzit.olsztyn.eu/index.php/pl/transport-publiczny/rozklad-jazdy"
SUB_PAGE_LINK = "https://www.zdzit.olsztyn.eu/index.php"


def olsztyn():
    bus_dict = get_vehicle_types_dicts()
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Olsztyn",
        TIMESTAMP_ATTR: timestamp,
        READABLE_TIME_ATTR: formatted_date,
        APP_VERSION_ATTR: 1,
        TRAMS_ATTR: [],
        BUSES_ATTR: buses
    }

    raw_json = json.dumps(json_dict, ensure_ascii=False)
    create_json_file(raw_json, JSON_FILE_NAME)


def get_vehicle_types_dicts():
    _main_page_content = get_main_page_content()
    _all_links = _main_page_content.find_all('a')
    _bus_timetable_links = filtered_links_with_class(_all_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _bus_dict


def get_main_page_content():
    _r = requests.get(MAIN_PAGE_LINK, verify=False)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_links_with_class(all_links):
    _filtered = []
    for link in all_links:
        try:
            a_class = link.attrs['class']
            is_class_matching = \
                a_class == ['ttt_cl'] or \
                a_class == ['dtt_cl'] or \
                a_class == ['gtt_cl'] or \
                a_class == ['ntt_cl'] or \
                a_class == ['stt_cl']
            if is_class_matching:
                _filtered.append(link)
        except KeyError:
            print()
    if len(_filtered) == 0:
        raise Exception("Error: did not find classes")
    return _filtered


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
        link_to_timetable = SUB_PAGE_LINK + link.attrs['href']
        _dict[line_number] = link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        try:
            _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])
            _number = key
            for direction in _directions_for_subpage:
                _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
                _vehicle_data.append(_row)
                print(_row)
        except Exception:
            print("Error: link " + vehicle_data_dict[key] + " is broken")
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_h2s = _sub_page_content.find_all('h2')
    _filtered_h2s = filter_h2s(_all_h2s)
    _directions = get_directions(_filtered_h2s)
    return _directions


def filter_h2s(all_h2s):
    _filtered = []
    for h2 in all_h2s:
        try:
            h2.attrs['class']
        except KeyError:
            _filtered.append(h2)
    if len(_filtered) == 0:
        raise Exception("Error: directions not found")
    return _filtered


def get_sub_page_content(url):
    _r = requests.get(url, verify=False)
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


def get_directions(h2s):
    _directions = []
    for h2 in h2s:
        raw_text = h2.text
        split = raw_text.split(' - ')
        direction = split[0]
        _directions.append(direction)
    if len(_directions) == 0:
        raise Exception("Error: directions not found")
    return _directions


if __name__ == '__main__':
    olsztyn()
