import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, print_generation_results, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error, \
    find_first_containing_values_or_error


class KmPlock(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.kmplock.eu/rozklady/"

    def get_transit_agency_name(self) -> str:
        return "KM Płock"

    def _get_line_direction_json_file_name(self) -> str:
        return "km_plock.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["list-type"]
        )

        all_link_tags: list[bs4.element.Tag] = []
        for div_tag in filtered_div_tags:
            link_tags = div_tag.find_all('a')
            for link_tag in link_tags:
                all_link_tags.append(link_tag)

        return create_links_dictionary(all_link_tags, self._MAIN_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["text-center", "bg-lightgray"]
        )

        directions_set: set[str] = set()
        for td_tag in filtered_td_tags:
            raw_text = td_tag.text
            if "Kierunek:" in raw_text:
                strong_tag = td_tag.find_next('strong')
                direction = strong_tag.text
                directions_set.add(direction)

        directions_list: list[str] = list(directions_set)
        return directions_list

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_table_tags = sub_page_content.find_all('table')
        filtered_table_tags = find_all_attribute_matching_or_error(
            elements=all_table_tags,
            attribute="class",
            value_to_match=["route"]
        )

        stops_set: set[str] = set()
        for table_tag in filtered_table_tags:
            link_tags = table_tag.find_all('a')
            if len(link_tags) == 0:
                continue

            try:
                first_link_tag = find_first_containing_values_or_error(
                    elements=link_tags,
                    attribute="href",
                    values_to_match=["rozklad"]
                )
                stop_name = first_link_tag.text
                stops_set.add(stop_name)
            except Exception:
                continue

        stops_list: list[str] = list(stops_set)
        return stops_list


if __name__ == '__main__':
    km_plock = KmPlock()
    km_plock.generate_data()
    print_generation_results(km_plock.get_transit_agency_name(), km_plock.errors)
