import bs4

from TransitAgency import TransitAgency
from implementation.commons.generation_util import create_links_dictionary, get_page_content, print_list
from implementation.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error


def _get_bus_timetable_links(all_divs_in_content_div) -> list[bs4.element.Tag]:
    div_box_buses = find_all_attribute_matching_or_error(
        elements=all_divs_in_content_div,
        attribute="class",
        value_to_match=["box_bus"]
    )
    _bus_timetable_links = div_box_buses[0].find_all('a') + div_box_buses[1].find_all('a')
    return _bus_timetable_links


def _get_tram_timetable_links(all_divs_in_content_div) -> list[bs4.element.Tag]:
    _div_box_tram = find_first_attribute_matching_or_error(
        elements=all_divs_in_content_div,
        attribute="class",
        value_to_match=["box_tram"]
    )
    _tram_timetable_links = _div_box_tram.find_all('a')
    _tram_timetable_links_filtered = \
        [link_tag
         for link_tag in _tram_timetable_links
         if type(link_tag) is bs4.element.Tag]
    return _tram_timetable_links_filtered


def _read_directions_from_h2(h2: bs4.element.Tag) -> list[str]:
    _filtered = h2.text.split(" &leftrightarrow ")
    _directions = []
    for direction in _filtered:
        _directions.append(direction)
    return _directions


class MpkPoznan(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.mpk.poznan.pl/rozklad-jazdy"

    _main_page_content: bs4.BeautifulSoup = None
    _all_divs: bs4.element.ResultSet = None
    _content_div: bs4.element.Tag = None
    _tram_tag_links: list[bs4.element.Tag] = None
    _bus_tag_links: list[bs4.element.Tag] = None

    def __init__(self):
        super().__init__()
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        self._all_divs = self._main_page_content.find_all('div')
        self._content_div = find_first_attribute_matching_or_error(
            elements=self._all_divs,
            attribute="id",
            value_to_match="content"
        )
        _pair: (bs4.element.Tag, bs4.element.Tag) = self._get_tram_and_bus_timetable_links()
        self._tram_tag_links = _pair[0]
        self._bus_tag_links = _pair[1]

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._tram_tag_links)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._bus_tag_links)

    def _get_directions_for_sub_page(self, link: str) -> list[str]:
        _sub_page_content = get_page_content(link)
        _all_h2s = _sub_page_content.find_all('h2')
        _filtered_h2 = find_first_attribute_matching_or_error(
            elements=_all_h2s,
            attribute="class",
            value_to_match=["line-title__name"]
        )
        _directions = _read_directions_from_h2(_filtered_h2)
        return _directions

    def get_transit_agency_name(self):
        return "MPK Poznań"

    def _get_line_direction_json_file_name(self):
        return "mpk_poznan.json"

    def _get_tram_and_bus_timetable_links(self) -> (list[bs4.element.Tag], list[bs4.element.Tag]):
        all_divs_in_content_div = self._content_div.find_all('div')
        tram_timetable_links = _get_tram_timetable_links(all_divs_in_content_div)
        bus_timetable_links = _get_bus_timetable_links(all_divs_in_content_div)
        return tram_timetable_links, bus_timetable_links

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        _sub_page_content = get_page_content(url)
        _all_span_tags = _sub_page_content.find_all('span')
        _filtered_span_tags = find_all_attribute_matching_or_error(
            elements=_all_span_tags,
            attribute="class",
            value_to_match=["line-stop__name"]
        )
        _result_set: set[str] = set()
        for span_tag in _filtered_span_tags:
            raw_text = span_tag.text
            _result_set.add(raw_text)

        _result_list = list(_result_set)
        return _result_list

    def _get_stops_data_json_file_name(self) -> str:
        return "mpk_poznan_stops.json"


if __name__ == '__main__':
    mpk_poznan = MpkPoznan()
    mpk_poznan.generate_data()
    print_list(mpk_poznan.get_transit_agency_name(), mpk_poznan.errors)
