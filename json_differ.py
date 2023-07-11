def json_diff(json1: dict, json2: dict, parent_key: str = '', is_recursive: bool = False) -> dict[str, any]:
    """
    Calculate the difference between two nested JSON objects and return a dictionary 
    detailing the changes. Works with nested dictionaries and lists.
    :param json1: The original JSON object.
    :param json2: The new JSON object.
    :param parent_key: The parent key for nested dictionaries or lists. Default is empty string.
    :param is_recursive: This parameter is utilized for internal checks and should only be set to True
        when the function is invoked recursively from within itself.
        It is not meant to be manipulated during standard use of the function.
    :return: A dictionary detailing the changes made from json1 to json2.
    Example:
    json1 = {
        'key1': {
            'subkey1': 'value1',
            'subkey2': 'value2'
        },
        'key2': 'value3',
        'key3': 'value4',
        'key4': [
            {
                'subkey1': 'value1',
                'subkey2': 'value2'
            },
            'value3'
        ]
    }
    json2 = {
        'key1': {
            'subkey1': 'value1_modified',
            'subkey2': 'value2'
        },
        'key2': 'value3',
        'key4': [
            {
                'subkey1': 'value1',
                'subkey2': 'value2_modified'
            },
            'value3',
            'value4'
        ]
    }
    diff = json_diff(json1, json2)
    print(diff)
    # Output (in general):
    # {
    #   'modified': {'key1.subkey1': ('value1', 'value1_modified'), 'key4[0].subkey2': ('value2', 'value2_modified')},
    #   'added': {'key4[2]': 'value4'},
    #   'removed': {'key3': 'value4'}
    # }
    Tests:

    >>>diff = json_diff(None, None)
    >>>assert diff == {'modified': {'': (None, None)}, 'added': {}, 'removed': {}}
    >>>diff = json_diff(None, {"key": "value"})
    >>>assert diff == {'modified': {'': (None, {'key': 'value'})}, 'added': {}, 'removed': {}}
    >>>diff = json_diff({"key": "value"}, None)
    >>>assert diff == {'modified': {'': ({'key': 'value'}, None)}, 'added': {}, 'removed': {}}
    >>>diff = json_diff({"key1": "value1"}, {"key1": "value1", "key2": "value2"})
    >>>assert diff == {'added': {'key2': 'value2'}}
    >>>diff = json_diff({"key1": "value1", "key2": "value2"}, {"key1": "value1"})
    >>>assert diff == {'removed': {'key2': 'value2'}}
    >>>diff = json_diff({"key1": "value1"}, {"key1": "value2"})
    >>>assert diff == {'modified': {'key1': ('value1', 'value2')}}
    >>>diff = json_diff({"key1": {"subkey": "value1"}}, {"key1": {"subkey": "value2"}})
    >>>assert diff == {'modified': {'key1.subkey': ('value1', 'value2')}}
    >>>diff = json_diff({"key1": ["value1", "value2"]}, {"key1": ["value3", "value2"]})
    >>>assert diff == {'modified': {'key1[0]': ('value1', 'value3')}}
    >>>diff = json_diff({"key1": ["value1", "value2"]}, {"key1": ["value1", "value2", "value3"]})
    >>>assert diff == {'modified': {'key1': (['value1', 'value2'], ['value1', 'value2', 'value3'])}}
    >>>diff = json_diff({"key1": ["value1", "value2", "value3"]}, {"key1": ["value1", "value2"]})
    >>>assert diff == {'modified': {'key1': (['value1', 'value2', 'value3'], ['value1', 'value2'])}}
    >>>diff = json_diff({"key1": [{"subkey": "value1"}, {"subkey": "value2"}]}, {"key1": [{"subkey": "value3"}, {"subkey": "value2"}]})
    >>>assert diff == {'modified': {'key1[0].subkey': ('value1', 'value3')}}
    """

    if json1 is None or json2 is None:
        return {'modified': {parent_key: (json1, json2)}, 'added': {}, 'removed': {}}

    # Check for valid input
    json1_type = isinstance(json1, (dict, list, type(None)))
    json2_type = isinstance(json2, (dict, list, type(None)))
    if is_recursive is False and not (json1_type or json2_type):
        raise ValueError('Both json1 and json2 should be either a dictionary, list, or None')

    diff = {'modified': {}, 'added': {}, 'removed': {}}

    if isinstance(json1, dict) and isinstance(json2, dict):
        keys1 = set(json1.keys())
        keys2 = set(json2.keys())

        # keys in json1 and not in json2
        for k in keys1 - keys2:
            full_key = f'{parent_key}.{k}' if parent_key else k
            diff['removed'][full_key] = json1[k]

        # keys in json2 and not in json1
        for k in keys2 - keys1:
            full_key = f'{parent_key}.{k}' if parent_key else k
            diff['added'][full_key] = json2[k]

        # common keys
        for k in keys1 & keys2:
            full_key = f'{parent_key}.{k}' if parent_key else k
            sub_diff = json_diff(json1[k], json2[k], full_key, is_recursive=True)
            for key, value in sub_diff.items():
                diff[key].update(value)

    elif isinstance(json1, list) and isinstance(json2, list):
        if len(json1) != len(json2):
            diff['modified'][parent_key] = (json1, json2)
        else:
            for i, (item1, item2) in enumerate(zip(json1, json2)):
                full_key = f'{parent_key}[{i}]'
                sub_diff = json_diff(item1, item2, full_key, is_recursive=True)
                for key, value in sub_diff.items():
                    diff[key].update(value)

    else:
        if json1 != json2:
            diff['modified'][parent_key] = (json1, json2)

    # Removing empty keys
    diff = {k: v for k, v in diff.items() if v}

    return diff
