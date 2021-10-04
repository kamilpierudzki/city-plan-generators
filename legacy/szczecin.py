import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "szczecin.json"

SUB_PAGE_LINK = "https://www.zditm.szczecin.pl/"


def szczecin():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Szczecin",
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
    _all_h2s = _main_page_content.find_all('h2')

    _tram_h2 = find_h2_for_vehicle_tpe_class(['tdz'], _all_h2s)

    _bus_h2_0 = find_h2_for_vehicle_tpe_class(['adz'], _all_h2s)
    _bus_h2_1 = find_h2_for_vehicle_tpe_class(['adz1'], _all_h2s)
    _bus_h2_2 = find_h2_for_vehicle_tpe_class(['adp'], _all_h2s)
    _bus_h2_3 = find_h2_for_vehicle_tpe_class(['ada'], _all_h2s)
    _bus_h2_4 = find_h2_for_vehicle_tpe_class(['anz'], _all_h2s)

    _tram_h2_sibling = get_sibling_for_h2(_tram_h2)
    _bus_h2_0_sibling = get_sibling_for_h2(_bus_h2_0)
    _bus_h2_1_sibling = get_sibling_for_h2(_bus_h2_1)
    _bus_h2_2_sibling = get_sibling_for_h2(_bus_h2_2)
    _bus_h2_3_sibling = get_sibling_for_h2(_bus_h2_3)
    _bus_h2_4_sibling = get_sibling_for_h2(_bus_h2_4)

    _tram_timetable_links = find_all_links_for_element(_tram_h2_sibling)
    _bus_timetable_links = find_all_links_for_element(_bus_h2_0_sibling) + \
                           find_all_links_for_element(_bus_h2_1_sibling) + \
                           find_all_links_for_element(_bus_h2_2_sibling) + \
                           find_all_links_for_element(_bus_h2_3_sibling) + \
                           find_all_links_for_element(_bus_h2_4_sibling)

    _tram_dict = create_dict(_tram_timetable_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _tram_dict, _bus_dict


def find_all_links_for_element(element):
    _all_links = element.find_all('a')
    return _all_links


def get_sibling_for_h2(h2):
    _sibling = h2.find_next_sibling('ul')
    return _sibling


def get_main_page_content():
    _r = requests.get("https://www.zditm.szczecin.pl/pl/pasazer/rozklady-jazdy,wedlug-linii")
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def find_h2_for_vehicle_tpe_class(class_to_find, all_h2s):
    for h2 in all_h2s:
        try:
            a_class = h2.attrs['class']
            is_class_matching = a_class == class_to_find
            if is_class_matching:
                return h2
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
        _dict[line_number] = SUB_PAGE_LINK + link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])

        if len(_directions_for_subpage) == 0:
            print("ERROR: sub-page error for: " + vehicle_data_dict[key])
            continue

        _number = key
        for direction in _directions_for_subpage:
            _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(_row)
            print(_row)
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_tds = _sub_page_content.find_all('td')
    _filtered_tds = filtered_td2_of_class_trasa2(_all_tds)
    _result = []
    for td in _filtered_tds:
        _filtered_directions = filtered_td_directions(td)
        _result.append(_filtered_directions)
    _result_flatten = [item for sublist in _result for item in sublist]
    return _result_flatten


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_td2_of_class_trasa2(all_tds):
    _result = []
    for td in all_tds:
        try:
            a_class = td.attrs['class']
            is_class_matching = a_class == ['trasa2']
            if is_class_matching:
                _result.append(td)
        except KeyError:
            print()
    return _result


def filtered_td_directions(filtered_td):
    _strong = filtered_td.find_next('strong')
    _result = [_strong.contents[0], _strong.contents[2]]
    return _result


if __name__ == '__main__':
    szczecin()
