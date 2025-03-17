import os
import logging
import yaml

logger = logging.getLogger(__name__)

def set_config_values():
    user_config = {
        'host': 'localhost',
        'port': 4455
    }
    
    user_config['host'] = prompt_user('Enter the host address: ', user_config['host'])
    
    while True:
        port = prompt_user('Enter the specified port: ', user_config['port'])
        try:
            user_config['port'] = int(port)
            break
        except ValueError:
            print('ERROR: Unexpected data type received. Try again.')
    
    while True: 
        password = prompt_user('Enter the password (Found under Tools->Websocket Server Settings->Server Password): ')  
        if not password:
            print('ERROR: A password is required. Try again.')
        else:
            user_config['password'] = password
            break
        
    return user_config

def is_valid_config(config):
    required_keys = {'host', 'port', 'password'}
    if len(config.keys()) > len(required_keys):
        return False
    
    for required in required_keys:
        if config.get(required) == None:
            return False
           
    return True
    
def prompt_user(text, default_value=None):
    user_def = input(text)
    if not user_def:
        user_def = default_value
    return user_def

def load_config(file_name='config.yaml'):
    print('Checking if config file exists...')
    if os.path.exists(file_name):
        print('Config found')
        logger.info('Config exists')
        
        with open(file_name, 'r') as file:
            config = yaml.safe_load(file)
            if is_valid_config(config):
                logger.info('Existing config valid')
            else:
                logger.warning('Existing config invalid')
                print('Existing config invalid. Generating new config...')
                config = set_config_values()
                with open(file_name, 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
    else:
        print('Config does not exist. Generating...')
        config = set_config_values()
        with open(file_name, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
            
    print('Config loaded')
    return config