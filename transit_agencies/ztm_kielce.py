import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error, filtered_tags


class ZtmKielce(TransitAgency):
    _MAIN_PAGE_LINK = "https://ztm.kielce.pl/rozkad-jazdy-sp-429094646.html"
    _SUB_PAGE_LINK = "https://ztm.kielce.pl"

    def get_transit_agency_name(self) -> str:
        return "ZTM Kielce"

    def _get_data_file_name_without_extension(self) -> str:
        return "ztm_kielce"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        first_div_tag = find_first_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["rozklad_jazdy_aticle"]
        )
        next_ul_tag = first_div_tag.find_next('ul')
        all_link_tags = next_ul_tag.find_all('a')

        filtered_all_link_tags: list[bs4.element.Tag] = filtered_tags(all_link_tags)
        return create_links_dictionary(filtered_all_link_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_div_tags = sub_page_content.find_all('div')
        filtered_main_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="style",
            value_to_match="margin: 20px 0 20px 0; font-weight: bold; color: #000;"
        )
        directions_set: set[str] = set()
        for div_tag in filtered_main_div_tags:
            raw_text = div_tag.text
            direction = raw_text.split(":")[1]
            direction = direction.strip()
            directions_set.add(direction)

        try:
            filtered_variant_div_tags = find_all_attribute_matching_or_error(
                elements=all_div_tags,
                attribute="style",
                value_to_match="margin: 20px 0 20px 0; font-weight: bold; text-decoration: underline; color: #000; cursor: pointer;"
            )

            for div_tag in filtered_variant_div_tags:
                raw_text = div_tag.text
                directions = raw_text.split("-")
                for direction in directions:
                    _direction = direction.strip()
                    directions_set.add(_direction)
        except Exception:
            None

        directions_list = list(directions_set)
        return directions_list

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_div_tags = sub_page_content.find_all('div')
        filtered_main_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="style",
            value_to_match="margin-right: 15px;"
        )
        stops_set: set[str] = set()
        for div_tag in filtered_main_div_tags:
            link_tags = div_tag.find_all('a')
            filtered_link_tags: list[bs4.element.Tag] = filtered_tags(link_tags)
            for link_tag in filtered_link_tags:
                stop_name = link_tag.text
                stops_set.add(stop_name)

        try:
            filtered_variant_div_tags = find_all_attribute_matching_or_error(
                elements=all_div_tags,
                attribute="style",
                value_to_match="margin-right: 15px; display: none;"
            )

            for div_tag in filtered_variant_div_tags:
                link_tags = div_tag.find_all('a')
                filtered_link_tags: list[bs4.element.Tag] = filtered_tags(link_tags)
                for link_tag in filtered_link_tags:
                    stop_name = link_tag.text
                    stops_set.add(stop_name)
        except Exception:
            None

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    ztm_kielce = ZtmKielce()
    ztm_kielce.generate_data()
    print_generation_results(ztm_kielce.get_transit_agency_name(), ztm_kielce.errors)
