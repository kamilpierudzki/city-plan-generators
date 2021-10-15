import bs4.element


def find_first_attribute_matching_or_error(
        elements: list[bs4.element.Tag],
        attribute: str,
        value_to_match
) -> bs4.element.Tag:
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_attr_matching = attr == value_to_match
            if is_attr_matching:
                return element
        except KeyError:
            continue
    raise Exception("Error, elements do not match")


def find_all_attribute_matching_or_error(
        elements: bs4.element.ResultSet,
        attribute: str,
        value_to_match
) -> list[bs4.element.Tag]:
    _result: list[bs4.element.Tag] = []
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_attr_matching = attr == value_to_match
            if is_attr_matching:
                _result.append(element)
        except KeyError:
            continue
    if len(_result) == 0:
        raise Exception("Error, elements do not match")
    return _result


def find_all_containing_value_or_error(
        elements: list[bs4.element.Tag],
        attribute: str,
        value_to_match: str
) -> list[bs4.element.Tag]:
    _result: list[bs4.element.Tag] = []
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_element_containing_value = value_to_match in attr
            if is_element_containing_value:
                _result.append(element)
        except KeyError:
            continue
    if len(_result) == 0:
        raise Exception("Error, elements do not match")
    return _result


def find_all_containing_values_or_error(
        elements: list[bs4.element.Tag],
        attribute: str,
        values_to_match: list[str]
) -> list[bs4.element.Tag]:
    _result: list[bs4.element.Tag] = []
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_element_containing_all_values = is_element_contains_all_to_values(attr, values_to_match)
            if is_element_containing_all_values:
                _result.append(element)
        except KeyError:
            continue
    if len(_result) == 0:
        raise Exception("Error, elements do not match")
    return _result


def is_element_contains_all_to_values(element: str, values_to_match: list[str]) -> bool:
    for value in values_to_match:
        is_element_not_containing_value = value not in element
        if is_element_not_containing_value:
            return False
    return True


def find_first_containing_values_or_error(
        elements: list[bs4.element.Tag],
        attribute: str,
        values_to_match: list[str]
) -> bs4.element.Tag:
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_element_containing_all_values = is_element_contains_all_to_values(attr, values_to_match)
            if is_element_containing_all_values:
                return element
        except KeyError:
            continue
    raise Exception("Error, elements do not match")


def find_all_containing_any_of_values_or_error(
        elements: list[bs4.element.Tag],
        attribute: str,
        values_to_match: []
) -> list[bs4.element.Tag]:
    _result: list[bs4.element.Tag] = []
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_any_element_matching_value = is_any_element_matching_to_value(
                elements=values_to_match,
                value_to_match=attr
            )
            if is_any_element_matching_value:
                _result.append(element)
        except KeyError:
            continue
    if len(_result) == 0:
        raise Exception("Error, elements do not match")
    return _result


def is_any_element_matching_to_value(elements: [], value_to_match) -> bool:
    for element in elements:
        if element == value_to_match:
            return True
    return False


def filtered_tags(elements) -> list[bs4.element.Tag]:
    _filtered_tags: list[bs4.element.Tag] = []
    for tag in elements:
        if type(tag) == bs4.element.Tag:
            _filtered_tags.append(tag)
    return _filtered_tags
