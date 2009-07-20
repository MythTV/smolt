import config

def get_config_attr(attr, default=""):
    if hasattr(config, attr):
        return getattr(config, attr)
    else:
        return default
