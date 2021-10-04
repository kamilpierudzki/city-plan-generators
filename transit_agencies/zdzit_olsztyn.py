from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_list_str, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_containing_any_of_values_or_error, \
    find_all_attribute_matching_or_error


class ZdzitOlsztyn(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.zdzit.olsztyn.eu/index.php/pl/transport-publiczny/rozklad-jazdy"
    _SUB_PAGE_LINK = "https://www.zdzit.olsztyn.eu/index.php"

    def get_transit_agency_name(self) -> str:
        return "ZDZiT Olsztyn"

    def _get_line_direction_json_file_name(self) -> str:
        return "zdzit_olsztyn.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "zdzit_olsztyn_stops.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_PAGE_LINK, verify=False)
        all_link_tags = main_page_content.find_all('a')
        filtered_link_tags = find_all_containing_any_of_values_or_error(
            elements=all_link_tags,
            attribute="class",
            values_to_match=[['ttt_cl'], ['dtt_cl'], ['gtt_cl'], ['ntt_cl'], ['stt_cl']]
        )
        return create_links_dictionary(filtered_link_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, verify=False)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["kierunek_pik"]
        )

        directions: list[str] = []
        for td_tag in filtered_td_tags:
            raw_text = td_tag.text
            split = raw_text.split(" - ")
            direction = split[0]
            directions.append(direction)

        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, verify=False)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["przystanek_pik"]
        )

        stops_set: set[str] = set()
        for td_tag in filtered_td_tags:
            link_tag = td_tag.find_next('a')
            stop_name = link_tag.text
            if len(stop_name) == 0:
                continue
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    zdzit_olsztyn = ZdzitOlsztyn()
    zdzit_olsztyn.generate_data()
    print_list_str(zdzit_olsztyn.get_transit_agency_name(), zdzit_olsztyn.errors)
