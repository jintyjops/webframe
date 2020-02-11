"""Handles reading from config file."""

def config(name, location="settings.conf"):
    """Read a string from config."""
    config = None
    with open(location, 'r') as f:
        config = f.read()

    return dict([
        (ln.partition('=')[0].strip(), ln.partition('=')[2].strip())
        for ln in config.split('\n') 
        if len(ln) and ln.strip()[:2] != '//'
    ])[name]

def config_bool(*args, **kwargs):
    """Read a boolean from config."""
    return True if config(*args, **kwargs) == 'true' else False

def config_int(*args, **kwargs):
    """Read a integer from config."""
    return int(config(*args, **kwargs))