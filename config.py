import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '89fdd0a53cb2d6e1a9cf21705a94036d'