import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, print_generation_results, create_links_dictionary
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error


def _read_directions(td_tag: bs4.element.Tag) -> list[str]:
    strong_tag = td_tag.find_next('strong')
    directions = [str(strong_tag.contents[0]), str(strong_tag.contents[2])]
    return directions


class ZdtmSzczecin(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.zditm.szczecin.pl/pl/pasazer/rozklady-jazdy,wedlug-linii"
    _SUB_PAGE_LINK = "https://www.zditm.szczecin.pl/"

    def __init__(self):
        super().__init__()
        self._all_h2_tags: list[bs4.element.Tag] = []

    def generate_data(self):
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        self._all_h2_tags = main_page_content.find_all('h2')
        TransitAgency.generate_data(self)

    def get_transit_agency_name(self) -> str:
        return "ZDiTM Szczecin"

    def _get_data_file_name_without_extension(self) -> str:
        return "zditm_szczecin"

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
        bus_h2_tags: list[bs4.element.Tag] = []
        for value in [['adz'], ['adz1'], ['adp'], ['anz']]:
            tag = find_first_attribute_matching_or_error(
                elements=self._all_h2_tags,
                attribute="class",
                value_to_match=value
            )
            bus_h2_tags.append(tag)

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
    print_generation_results(zdtm_szczecin.get_transit_agency_name(), zdtm_szczecin.errors)
