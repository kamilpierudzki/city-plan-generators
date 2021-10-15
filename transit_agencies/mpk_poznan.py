import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import create_links_dictionary, get_page_content, print_generation_results
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
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
    div_box_tram = find_first_attribute_matching_or_error(
        elements=all_divs_in_content_div,
        attribute="class",
        value_to_match=["box_tram"]
    )
    tram_timetable_links = div_box_tram.find_all('a')
    tram_timetable_links_filtered = \
        [link_tag
         for link_tag in tram_timetable_links
         if type(link_tag) is bs4.element.Tag]
    return tram_timetable_links_filtered


def _read_directions_from_h2(h2: bs4.element.Tag) -> list[str]:
    filtered = h2.text.split(" &leftrightarrow ")
    directions = []
    for direction in filtered:
        directions.append(direction)
    return directions


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
        pair: (bs4.element.Tag, bs4.element.Tag) = self._get_tram_and_bus_timetable_links()
        self._tram_tag_links = pair[0]
        self._bus_tag_links = pair[1]

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._tram_tag_links)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._bus_tag_links)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_h2_tags = sub_page_content.find_all('h2')
        filtered_h2_tag = find_first_attribute_matching_or_error(
            elements=all_h2_tags,
            attribute="class",
            value_to_match=["line-title__name"]
        )
        directions = _read_directions_from_h2(filtered_h2_tag)
        return directions

    def get_transit_agency_name(self):
        return "MPK Poznań"

    def _get_data_file_name_without_extension(self):
        return "mpk_poznan"

    def _get_tram_and_bus_timetable_links(self) -> (list[bs4.element.Tag], list[bs4.element.Tag]):
        all_divs_in_content_div = self._content_div.find_all('div')
        tram_timetable_links = _get_tram_timetable_links(all_divs_in_content_div)
        bus_timetable_links = _get_bus_timetable_links(all_divs_in_content_div)
        return tram_timetable_links, bus_timetable_links

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_span_tags = sub_page_content.find_all('span')
        filtered_span_tags = find_all_attribute_matching_or_error(
            elements=all_span_tags,
            attribute="class",
            value_to_match=["line-stop__name"]
        )

        stops_set: set[str] = set()
        for span_tag in filtered_span_tags:
            raw_text = span_tag.text
            stops_set.add(raw_text)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mpk_poznan = MpkPoznan()
    mpk_poznan.generate_data()
    print_generation_results(mpk_poznan.get_transit_agency_name(), mpk_poznan.errors)
