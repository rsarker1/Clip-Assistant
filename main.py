import os
import asyncio
import logging
import yaml
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

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
    
def prompt_user(text, default_value=None):
    user_def = input(text)
    if not user_def:
        user_def = default_value
    return user_def

def load_config(file_name='config.yaml'):
    print('Checking if config file exists...')
    if os.path.exists(file_name):
        print('Config found')
        with open(file_name, 'r') as file:
            config = yaml.safe_load(file)
    else:
        print('Config does not exist. Generating...')
        config = set_config_values()
        with open(file_name, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
            
    print('Config loaded')
    return config

async def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='clip_assistant.log', level=logging.INFO)
    logger.info('Started')
    config = load_config()
    obs_controller = OBSRecordingController(
        host=config['host'],
        port=config['port'],
        password=config['password']
    )
    await obs_controller.connect()
    
    
    
    logger.info('Ended')
    
asyncio.run(main())
