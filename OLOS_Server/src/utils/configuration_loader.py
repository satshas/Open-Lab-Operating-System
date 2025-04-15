import os
import yaml

# class to load config file values


class ConfigurationLoader:
    def __init__(self, dictionary):
        # Keep the original dictionary
        self._original_dict = dictionary
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = ConfigurationLoader(value)
            setattr(self, key, value)

    @classmethod
    def from_yaml(cls):
        # Absolute path of the current file
        file_path = os.path.abspath(os.path.join(__file__, "../../.."))

        config_file_path = os.path.join(file_path, 'config.yaml')

        with open(config_file_path, 'r') as file:
            config_dict = yaml.safe_load(file)

        return cls(config_dict)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    # helper function to get dictionary values
    def get_dict(self, path):
        keys = path.split('.')
        current_dict = self._original_dict
        for key in keys:
            current_dict = current_dict.get(key)
            if current_dict is None:
                return None
        return current_dict
