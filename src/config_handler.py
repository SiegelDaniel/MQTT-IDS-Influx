import simplejson

class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

class config_loader(Singleton):
    
    def __init__(self,JSON_PATH):
        self.__config = self.__load_config("./")

    def __load_config(self,JSON_PATH):
        """Loads config from a given JSON file, extracts the relevant config parameters"""
        with open(JSON_PATH) as json_file:
            data = simplejson.load(json_file)
        return data

    def get_config(self,module):
        """Get the config attributes for 
        the corresponding module from the initially loaded data
        Takes a string as module description
        Returns a dict with the configuration points as keys
        """
        if module in self.__config:
            return self.__config[module]
        else:
            return None

    def get_config_point(self,configpoint,config):
        """Extracts a certain config point (as string) from the configuration dictionary"""
        if configpoint in config:
            return config[configpoint]