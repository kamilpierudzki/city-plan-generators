import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error, \
    find_first_attribute_matching_or_error


def _read_directions(i_tag: bs4.element.Tag) -> list[str]:
    link_tag = i_tag.find_next('a')
    raw_text = link_tag.text
    directions = raw_text.split(" - ")
    return directions


class ZimSlupsk(TransitAgency):
    _MAIN_PAGE_LINK = "https://rozklad.zimslupsk.pl/"

    def get_transit_agency_name(self) -> str:
        return "ZIM Słupsk"

    def _get_data_file_name_without_extension(self) -> str:
        return "zim_slupsk"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_link_tags = main_page_content.find_all('a')
        filtered_link_tags = find_all_attribute_matching_or_error(
            elements=all_link_tags,
            attribute="class",
            value_to_match=["stretched-link", "p-3", "text-center", "badge", "badge-primary", "d-block"]
        )
        return create_links_dictionary(filtered_link_tags, self._MAIN_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_i_tags = sub_page_content.find_all('i')
        first_i_tag = find_first_attribute_matching_or_error(
            elements=all_i_tags,
            attribute="class",
            value_to_match=["bi", "bi-arrow-right-short", "mr-2"]
        )
        directions = _read_directions(first_i_tag)
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_i_tags = sub_page_content.find_all('i')
        filtered_i_tags = find_all_attribute_matching_or_error(
            elements=all_i_tags,
            attribute="class",
            value_to_match=["bi", "bi-arrow-right-short", "mr-2"]
        )

        stops_set: set[str] = set()
        for i_tag in filtered_i_tags:
            link_tag = i_tag.find_next('a')
            direction_url = self._MAIN_PAGE_LINK + link_tag.attrs['href']
            sub_sub_page_content = get_page_content(direction_url)
            all_ul_tags = sub_sub_page_content.find_all('ul')
            first_ul_tag = find_first_attribute_matching_or_error(
                elements=all_ul_tags,
                attribute="class",
                value_to_match=["list-unstyled"]
            )
            all_link_tags = first_ul_tag.find_all('a')
            for link_tag in all_link_tags:
                stop_name = str(link_tag.contents[0])
                stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    zim_slupsk = ZimSlupsk()
    zim_slupsk.generate_data()
    print_generation_results(zim_slupsk.get_transit_agency_name(), zim_slupsk.errors)
