import os
import ConfigParser

package_directory = os.path.dirname(__file__)
config_file = os.path.join(package_directory, 'config.ini')

config = ConfigParser.ConfigParser()
config.read(config_file)

usgs_username = config.get('USGS','username')
usgs_password = config.get('USGS','password')