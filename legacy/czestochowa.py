import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "czestochowa.json"
MAIN_PAGE_LINK = "https://www.m.rozkladzik.pl/czestochowa/rozklad_jazdy.html"
SUB_PAGE_LINK = "https://www.m.rozkladzik.pl/czestochowa/"


def czestochowa():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Częstochowa",
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
    _r = requests.get(MAIN_PAGE_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def find_content_div(all_divs):
    for div in all_divs:
        try:
            a_id = div.attrs['id']
            is_id_matching = a_id == 'linies_div'
            if is_id_matching:
                return div
        except KeyError:
            print()
    raise Exception("Error: did not find id \'lines_div\'")


def get_tram_and_bus_timetable_links(content_div):
    _tram_timetable_links = []
    _bus_timetable_links = []
    is_tram = None
    for tag in content_div.contents:
        if tag.text == 'Tramwaje':
            is_tram = True
            continue
        if tag.text == 'Autobusy':
            is_tram = False
            continue

        link = tag.find_next('a')
        if link is None:
            continue

        if is_tram is None:
            raise Exception("Error: did not find tram or bus")
        elif is_tram:
            _tram_timetable_links.append(link)
            continue
        elif not is_tram:
            _bus_timetable_links.append(link)
            continue

    return _tram_timetable_links, _bus_timetable_links


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
    _all_h3s = _sub_page_content.find_all('h3')
    _directions = get_directions(_all_h3s)
    return _directions


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def get_directions(all_h3s):
    _directions = []
    for h3 in all_h3s:
        _directions.append(h3.text)
    if len(_directions) == 0:
        raise Exception("Error: directions did not find")
    return _directions


if __name__ == '__main__':
    czestochowa()
