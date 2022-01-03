"""This module adds JSON based configuration handling to the program.

It implements a class that performs JSON based config handling. The interface
is simply: param passed to object method provides the value of the parameter
from the configuration file.

Author: Noor
Date: January 3, 2022
License: None
"""
import json
if __name__ == '__main__':
    from errors import InvalidConfigError
else:
    from swagger_server.controllers.common.errors import InvalidConfigError

import logging

# Setup the logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/' + __name__ + ".log")
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Path to the configuration filename in the project parent directory
config_filename = 'config.json'

class ConfigHandler():
    """
    This class implements the configuration handling capabilities.
    """
    def __init__(self):
        """This is the class constructor. It loads the config file."""
        with open(config_filename, 'r') as f:
            # load the config JSON into a python obj
            self.config = json.load(f)
            logger.info("Loaded configuration from " + config_filename)

        # validate the configuration file
        logger.info("Validating configuration")
        try:
            self._validate_config()    
        except InvalidConfigError as e:
            logger.error(f"Configuration invalid!\n {e}")
            raise InvalidConfigError(f"Configuration invalid! See 'logs/{__name__}.log'")

    def get_params(self, type):
        """This method provides the parameter types requested by the module.
        Type can be a string of value:
        1. database -> provides DB params as a dict()
        2. sniffers -> provides sniffer params as list of dict()
        """
        return self.config[type]

    def _validate_config(self):
        """This method implements basic parameter validation for the config
        file of the program."""
        # validate the "database" section
        config_sections = self.config.keys()

        # check if all the sections are present
        if "database" not in config_sections:
            raise InvalidConfigError("'database' section not defined in config.json.")

        elif "sniffers" not in config_sections:
            raise InvalidConfigError("'sniffers' section not defined in config.json.")

        logger.info("All sections ['database', 'sniffers'] exist in config.json.")
        logger.info("Validating section 'database'.")
        db_params = self.config["database"].keys()
        db_params_list = ["host", "username", "password", "database"]
        for p in db_params_list:
            if p not in db_params:
                raise InvalidConfigError(f"'{p}' not defined in 'database' section.")
        logger.info("All entries exist in 'database' section.")
        logger.info("Validating 'sniffers' section.")
        sniffer_params_list = ["host", "username", "password", "spool_dir"]
        for each_sniffer in self.config["sniffers"]:
            for each_param in sniffer_params_list:
                if each_param not in each_sniffer.keys():
                    raise InvalidConfigError(f"'{each_param}' not defined in 'sniffers' section.")
        logger.info("All entries exist in 'sniffers' section.")


    def _print_config(self):
        """Print the configuration file contents."""
        print("The configuration file is:")
        print(json.dumps(self.config, indent=4))

def test_function():
    config_handler = ConfigHandler()
    print("Database parameters: ")
    db_params = config_handler.get_params("database")
    print(json.dumps(db_params, indent=4))

    print("Sniffer parameters: ")
    for each_sniffer in config_handler.get_params("sniffers"):
        print(json.dumps(each_sniffer, indent=4))

if __name__ == '__main__':
    test_function()