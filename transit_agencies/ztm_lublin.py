import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_list_str, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error, \
    find_first_attribute_matching_or_error


def _get_all_links(div_tags: list[bs4.element.Tag]) -> list[bs4.element.Tag]:
    _links = []
    for div in div_tags:
        all_links_in_div_tag = div.find_all('a')
        _links.append(all_links_in_div_tag)

    _flatten_links = [item for sublist in _links for item in sublist]
    return _flatten_links


def _read_direction(span_tag: bs4.element.Tag) -> str:
    direction = span_tag.find_next('span').text
    return direction


def _select_every_other_td_tag(all_td_tags: list[bs4.element.Tag]) -> list[bs4.element.Tag]:
    every_n = 2
    counter = 0
    _filtered: list[bs4.element.Tag] = []
    for i, td_tag in enumerate(all_td_tags):
        counter = counter + 1
        if i == 1:
            _filtered.append(td_tag)
            counter = 0
            every_n = 3
        elif counter == every_n:
            _filtered.append(td_tag)
            counter = 0
    if len(_filtered) == 0:
        raise Exception("Error, _select_every_other_td_tag did not filter any tag")
    return _filtered


def _read_stop_name(td_tag: bs4.element.Tag) -> str:
    stop_name = td_tag.text.strip()
    return stop_name


class ZtmLublin(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.ztm.lublin.eu"

    _main_page_content: bs4.BeautifulSoup = None

    def __init__(self):
        super().__init__()
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_span_tags = sub_page_content.find_all('span')
        filtered_span_tags = find_all_attribute_matching_or_error(
            elements=all_span_tags,
            attribute="class",
            value_to_match=["icon-wheel"]
        )
        directions: list[str] = []
        for span_tag in filtered_span_tags:
            directions.append(_read_direction(span_tag))
        if len(directions) == 0:
            raise Exception("Error: _get_directions_for_sub_page did not find any directions for: " + url)
        return directions

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        all_div_tags = self._main_page_content.find_all('div')
        filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["col-xs-12", "autobusy"]
        )
        bus_link_tags = _get_all_links(filtered_div_tags)
        return create_links_dictionary(bus_link_tags, self._MAIN_PAGE_LINK)

    def get_transit_agency_name(self) -> str:
        return "ZTM Lublin"

    def _get_line_direction_json_file_name(self) -> str:
        return "ztm_lublin.json"

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_article_tags = sub_page_content.find_all('article')
        article_tag = find_first_attribute_matching_or_error(
            elements=all_article_tags,
            attribute="class",
            value_to_match=["trasa-linii"]
        )
        all_td_tags = article_tag.find_all('td')
        td_tags_with_stops = _select_every_other_td_tag(all_td_tags)

        stops_set: set[str] = set()
        for td_tag in td_tags_with_stops:
            stops_set.add(_read_stop_name(td_tag))

        stops_list: list[str] = list(stops_set)
        return stops_list


if __name__ == '__main__':
    ztm_lublin = ZtmLublin()
    ztm_lublin.generate_data()
    print_list_str(ztm_lublin.get_transit_agency_name(), ztm_lublin.errors)
