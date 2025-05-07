import os
import logging
import yaml

logger = logging.getLogger(__name__)

FILE_NAME = 'config.yaml'
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 4455,
    'password': 'password',
    'notifications': 'TTS',
    'startup': False
}

def is_valid_config(config):
    for key, value in DEFAULT_CONFIG.items():
        if config.get(key) == None or not type(value) is type(config.get(key)):
            return False
              
    return True

def load_config():
    logger.info('Checking if config file exists...')
    if os.path.exists(FILE_NAME):
        logger.info('Config found')
        
        with open(FILE_NAME, 'r') as file:
            config = yaml.safe_load(file)
            if is_valid_config(config):
                logger.info('Existing config valid')
            else:
                logger.warning('Existing config invalid. Creating default config instead...')
                config = DEFAULT_CONFIG
                save_config(config)
    else:
        logger.info('Config does not exist. Generating...')
        config = DEFAULT_CONFIG
        save_config(config)
            
    logger.info('Config loaded correctly')
    return config

def save_config(config, updates=None):
    logger.info('Config saved')
    if updates:
        for key, val in updates.items():
            config[key] = val

    with open(FILE_NAME, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
        
def get_config():
    with open(FILE_NAME, 'r') as file:
        config = yaml.safe_load(file)
    return config