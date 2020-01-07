import os
import sys
import string
import random

##Virtualenv Settings
activate_this = '/usr/share/item_catalog/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

##Replace the standard out
sys.stdout = sys.stderr

##Add this file path to sys.path in order to import settings
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

##Add this file path to sys.path in order to import app
sys.path.append('/usr/share/item_catalog/')

##Create appilcation for our app
from item_catalog.server import item_catalog_app as application
application.secret_key = "secret_key"