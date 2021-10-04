import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "gzm.json"
MAIN_PAGE_LINK = "https://rj.metropoliaztm.pl/"
SUB_SUB_PAGE_LINK = "https://rj.metropoliaztm.pl"


def gzm():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Górnośląsko-Zagłębowska Metropolia",
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
    _tram_timetable_links = get_tram_timetable_links(_all_divs)
    _bus_timetable_links = get_bus_timetable_links(_all_divs)
    _tram_dict = create_dict(_tram_timetable_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _tram_dict, _bus_dict


def get_bus_timetable_links(all_divs):
    _bus_divs = find_bus_divs(all_divs)
    _bus_timetable_links = []
    for bus_div in _bus_divs:
        bus_sub_div = bus_div.find_next('div')
        all_bus_sub_div_links = bus_sub_div.find_all('a')
        _bus_timetable_links.append(all_bus_sub_div_links)
    _bus_timetable_links_flatten = [item for sublist in _bus_timetable_links for item in sublist]
    return _bus_timetable_links_flatten


def get_tram_timetable_links(all_divs):
    _tram_div = find_tram_div(all_divs)
    _tram_divs = _tram_div.find_next('div')
    _tram_timetable_links = _tram_divs.find_all('a')
    return _tram_timetable_links


def find_tram_div(all_divs):
    for div in all_divs:
        try:
            a_id = div.attrs['id']
            is_id_matching = a_id == 'line_type-2-1'
            if is_id_matching:
                return div
        except KeyError:
            print()
    raise Exception("Error: tram div not found")


def find_bus_divs(all_divs):
    _filtered_divs = []
    for div in all_divs:
        try:
            a_id = div.attrs['id']
            is_id_matching = a_id == 'line_type-2-1' or \
                             a_id == 'line_type-5-1' or \
                             a_id == 'line_type-1-13' or \
                             a_id == 'line_type-1-1' or \
                             a_id == 'line_type-1-2' or \
                             a_id == 'line_type-1-9' or \
                             a_id == 'line_type-1-7'
            if is_id_matching:
                _filtered_divs.append(div)
        except KeyError:
            print()
    if len(_filtered_divs) == 0:
        raise Exception("Error: bus divs not found")
    return _filtered_divs


def get_main_page_content():
    _r = requests.get(MAIN_PAGE_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = MAIN_PAGE_LINK + link.attrs['href']
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
            continue
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_divs = _sub_page_content.find_all('div')
    try:
        _filtered_div_directions = filtered_div_class_list_group_item_list_group_item_warning(_all_divs)
        _directions = get_directions(_filtered_div_directions)
    except Exception:
        _url_sub_sub_page_link_tag = get_sub_sub_page_link_tag(_all_divs)
        _url_sub_sub_page_link = SUB_SUB_PAGE_LINK + _url_sub_sub_page_link_tag.attrs['href']
        return get_directions_for_subpage(_url_sub_sub_page_link)
    return _directions


def get_sub_sub_page_link_tag(all_divs):
    div_with_links = find_class_panel_heading_text_center(all_divs)
    _sub_sub_page_link_tag = div_with_links.find_next('a')
    return _sub_sub_page_link_tag


def find_class_panel_heading_text_center(all_divs):
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['panel-heading', 'text-center']
            if is_class_matching:
                return div
        except KeyError:
            print()
    raise Exception("Error: div in sub sub page not found")


def get_directions(div_directions):
    _directions = []
    for div_direction in div_directions:
        strong_tag = div_direction.find_next('strong')
        direction = strong_tag.text
        _directions.append(direction)
    if len(_directions) == 0:
        raise Exception("Error: did not found directions")
    return _directions


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_div_class_list_group_item_list_group_item_warning(all_divs):
    _filtered = []
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['list-group-item', 'list-group-item-warning']
            if is_class_matching:
                _filtered.append(div)
        except KeyError:
            print()
    if len(_filtered) == 0:
        raise Exception("Error: directions not found")
    return _filtered


if __name__ == '__main__':
    gzm()
