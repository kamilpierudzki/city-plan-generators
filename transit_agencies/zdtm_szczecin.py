import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, print_list_str, create_links_dictionary
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error


def _get_bus_h2_tags(
        all_h2_tags: list[bs4.element.Tag],
        values_to_match: list[list[str]]
) -> list[bs4.element.Tag]:
    tags: list[bs4.element.Tag] = []
    for value in values_to_match:
        tag = find_first_attribute_matching_or_error(
            elements=all_h2_tags,
            attribute="class",
            value_to_match=value
        )
        tags.append(tag)
    return tags


def _read_directions(td_tag: bs4.element.Tag) -> list[str]:
    strong_tag = td_tag.find_next('strong')
    directions = [str(strong_tag.contents[0]), str(strong_tag.contents[2])]
    return directions


class ZdtmSzczecin(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.zditm.szczecin.pl/pl/pasazer/rozklady-jazdy,wedlug-linii"
    _SUB_PAGE_LINK = "https://www.zditm.szczecin.pl/"

    _all_h2_tags: list[bs4.element.Tag] = None

    def __init__(self):
        super().__init__()
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        self._all_h2_tags = main_page_content.find_all('h2')

    def get_transit_agency_name(self) -> str:
        return "ZDiTM Szczecin"

    def _get_line_direction_json_file_name(self) -> str:
        return "zditm_szczecin.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        tram_h2_tag = find_first_attribute_matching_or_error(
            elements=self._all_h2_tags,
            attribute="class",
            value_to_match=["tdz"]
        )
        tram_ul_tag = tram_h2_tag.find_next_sibling('ul')
        tram_all_link_tags = tram_ul_tag.find_all('a')
        return create_links_dictionary(tram_all_link_tags, self._SUB_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_h2_tags = _get_bus_h2_tags(self._all_h2_tags, [['adz'], ['adz1'], ['adp'], ['ada'], ['anz']])

        bus_all_link_tags: list[bs4.element.Tag] = []
        for h2_tag in bus_h2_tags:
            h2_tag_sibling = h2_tag.find_next_sibling('ul')
            link_tags = h2_tag_sibling.find_all('a')
            bus_all_link_tags = bus_all_link_tags + link_tags

        return create_links_dictionary(bus_all_link_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["trasa2"]
        )
        directions: list[str] = []
        for td_tag in filtered_td_tags:
            directions = directions + _read_directions(td_tag)
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["przystanek"]
        )

        stops_set: set[str] = set()
        for td_tag in filtered_td_tags:
            link_tag = td_tag.find_next('a')
            stop_name = str(link_tag.text)
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    zdtm_szczecin = ZdtmSzczecin()
    zdtm_szczecin.generate_data()
    print_list_str(zdtm_szczecin.get_transit_agency_name(), zdtm_szczecin.errors)
