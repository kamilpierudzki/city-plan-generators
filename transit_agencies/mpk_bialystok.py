import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error, \
    find_all_containing_values_or_error


def _create_links_dictionary(vehicle_link_tags: list[bs4.element.Tag], sub_link_to_append: str = "") -> dict[
    str, str]:
    dictionary: dict[str, str] = {}
    for link in vehicle_link_tags:
        line_number = link.text.strip()
        link_to_timetable = sub_link_to_append + line_number
        dictionary[line_number] = link_to_timetable
    if len(dictionary) == 0:
        raise Exception("Error, vehicle tag link list is empty")
    return dictionary


class MpkBialystok(TransitAgency):
    _MAIN_LINK = "https://www.bstok.pl/mpk/"
    _SUB_PAGE_LINK = "https://www.komunikacja.bialystok.pl/?page=lista_przystankow&nr="

    def get_transit_agency_name(self) -> str:
        return "MPK Białystok"

    def _get_line_direction_json_file_name(self) -> str:
        return "mpk_bialystok.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_LINK)
        all_link_tags = main_page_content.find_all('a')
        filtered_link_tags = find_all_attribute_matching_or_error(
            elements=all_link_tags,
            attribute="class",
            value_to_match=["btn", "btn-default", "btn-lg"]
        )
        return _create_links_dictionary(filtered_link_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_thead_tags = sub_page_content.find_all('thead')
        directions: list[str] = []
        for thead_tag in all_thead_tags:
            direction = thead_tag.text.strip().replace('kierunek: ', "")
            directions.append(direction)

        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_link_tags = sub_page_content.find_all('a')
        filtered_link_tags = find_all_containing_values_or_error(
            elements=all_link_tags,
            attribute="href",
            values_to_match=["przystanek", "nrl", "nrp", "rozklad"]
        )

        stops_set: set[str] = set()
        for link_tag in filtered_link_tags:
            stop_name = link_tag.contents[0].strip()
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mpk_bialystok = MpkBialystok()
    mpk_bialystok.generate_data()
    print_generation_results(mpk_bialystok.get_transit_agency_name(), mpk_bialystok.errors)
