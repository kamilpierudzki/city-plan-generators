import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, create_links_dictionary, print_generation_results
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error


def _get_tram_and_bus_link_tags(content_div_tag: bs4.element.Tag) -> (list[bs4.element.Tag], list[bs4.element.Tag]):
    tram_link_tags: list[bs4.element.Tag] = []
    bus_link_tags: list[bs4.element.Tag] = []

    is_tram = None
    for tag in content_div_tag.contents:
        if tag.text == "Tramwaje":
            is_tram = True
            continue
        if tag.text == "Autobusy":
            is_tram = False
            continue
        if len(tag.text) == 0:
            continue

        link = tag.find_next('a')
        if link is None:
            continue

        if is_tram is None:
            raise Exception("Error: _get_tram_and_bus_link_tags did not find tram or bus")
        elif is_tram:
            tram_link_tags.append(link)
            continue
        elif not is_tram:
            bus_link_tags.append(link)
            continue

    return tram_link_tags, bus_link_tags


class MCzestochowa(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.m.rozkladzik.pl/czestochowa/rozklad_jazdy.html"
    _SUB_PAGE_LINK = "https://www.m.rozkladzik.pl/czestochowa/"

    _tram_link_tags: list[bs4.element.Tag] = []
    _bus_link_tags: list[bs4.element.Tag] = []

    def __init__(self):
        super().__init__()
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        content_div_tag = find_first_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="id",
            value_to_match="linies_div"
        )
        tram_bus_pair = _get_tram_and_bus_link_tags(content_div_tag)
        self._tram_link_tags = tram_bus_pair[0]
        self._bus_link_tags = tram_bus_pair[1]

    def get_transit_agency_name(self) -> str:
        return "Częstochowa"

    def _get_data_file_name_without_extension(self) -> str:
        return "czestochowa"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._tram_link_tags, self._SUB_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._bus_link_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_h3_tags = sub_page_content.find_all('h3')
        directions: list[str] = []
        for h3_tag in all_h3_tags:
            direction = h3_tag.text
            directions.append(direction)
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_link_tags = sub_page_content.find_all('a')
        filtered_link_tags = find_all_attribute_matching_or_error(
            elements=all_link_tags,
            attribute="class",
            value_to_match=["ui-btn"]
        )

        stops_set: set[str] = set()
        for link_tag in filtered_link_tags:
            raw_stop_name = link_tag.text
            stop_name = raw_stop_name.strip()
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    m_czestochowa = MCzestochowa()
    m_czestochowa.generate_data()
    print_generation_results(m_czestochowa.get_transit_agency_name(), m_czestochowa.errors)
