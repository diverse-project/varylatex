import os
import json


def merge_configs(json_config_path, config):
    """
    Adds the variables contained in config to the json config file
    """
    with open(json_config_path) as f:
        conf_source = json.load(f)
        res_conf = merge_dicts(conf_source, config)
    with open(json_config_path, 'w') as f:
        json.dump(res_conf, f, indent=4)


def merge_dicts(base_dict, second_dict):
    """
    Recursively creates a dictionary with the contents of two dicts.
    In case of a key conflicts, the dicts are merged, the arrays are concatenated and the values are replaced by
    the ones of the second dict.
    """
    output_dict = base_dict.copy()
    for key, value in second_dict.items():
        if key in base_dict:
            if type(value) == list:
                output_dict[key] += value
            elif type(value) == dict:
                output_dict[key] = merge_dicts(output_dict[key], value)
            else:
                output_dict[key] = value
        else:
            output_dict[key] = value
    return output_dict


def init_variables_json(path):
    """
    Sets up the "variables.json" file if it is empty or incomplete.
    """
    json_path = os.path.join(path, "variables.json")
    open(json_path, 'a').close()  # Creates the file if it is missing
    with open(json_path, 'r+') as f:
        if not f.read():  # If the file is empty (or has just been created)
            f.write("{}")
    template = {
        "booleans": [],
        "numbers": {},
        "enums": {},
        "choices": []
    }
    merge_configs(json_path, template)
