import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error


class MpkSwidnica(TransitAgency):
    _MAIN_PAGE_LINK = "http://rozklad.mpk.swidnica.pl/"

    _main_page_content: bs4.BeautifulSoup = None
    _number_h6_tag_dict: dict[str, bs4.element.Tag] = {}

    def generate_data(self):
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)

        all_h6_tags = self._main_page_content.find_all('h6')
        filtered_h6_tags = find_all_attribute_matching_or_error(
            elements=all_h6_tags,
            attribute="class",
            value_to_match=["mb-0"]
        )

        for h6_tag in filtered_h6_tags:
            all_span_tags = h6_tag.find_all('span')
            try:
                first_span_tag = find_first_attribute_matching_or_error(
                    elements=all_span_tags,
                    attribute="class",
                    value_to_match=["badge", "badge-warning"]
                )
                number_int = int(first_span_tag.text)
                number_str = str(number_int)
                self._number_h6_tag_dict[number_str] = h6_tag
            except Exception:
                continue
        TransitAgency.generate_data(self)

    def get_transit_agency_name(self) -> str:
        return "MPK Świdnica"

    def _get_data_file_name_without_extension(self) -> str:
        return "mpk_swidnica"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        all_div_tags = self._main_page_content.find_all("div")
        first_div_matching = find_first_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="id",
            value_to_match="linie"
        )
        all_link_tags = first_div_matching.find_all('a')
        return create_links_dictionary(all_link_tags, self._MAIN_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        current_number = url.split("#T")[1]
        h6_tag = self._number_h6_tag_dict[current_number]
        h7_tags = h6_tag.parent.parent.parent.parent.find_all('h7')

        directions: list[str] = []
        for h7_tag in h7_tags:
            try:
                all_span_tags = h7_tag.find_all('span')
                first_span_tag = find_first_attribute_matching_or_error(
                    elements=all_span_tags,
                    attribute="class",
                    value_to_match=["badge", "badge-warning"]
                )
                raw_text = first_span_tag.text
                direction = raw_text.strip()
                directions.append(direction)
            except Exception:
                continue
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        current_number = url.split("#T")[1]
        h6_tag = self._number_h6_tag_dict[current_number]
        ul_tags = h6_tag.parent.parent.parent.parent.find_all('ul')
        filtered_ul_tags = find_all_attribute_matching_or_error(
            elements=ul_tags,
            attribute="class",
            value_to_match=["lista-ulic"]
        )

        stops_set: set[str] = set()
        for ul_tag in filtered_ul_tags:
            all_link_tags = ul_tag.find_all('a')
            for link_tag in all_link_tags:
                stop_name = link_tag.text
                stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mpk_swidnica = MpkSwidnica()
    mpk_swidnica.generate_data()
    print_generation_results(mpk_swidnica.get_transit_agency_name(), mpk_swidnica.errors)
