import asyncio
import logging
from datetime import datetime
from yaml_config import load_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

async def main():
    logger = logging.getLogger(__name__)
    current_date = datetime.today().strftime('%Y_%m_%d')
    logging.basicConfig(
        filename=f'clip_assistant_{current_date}.log', 
        filemode='w', 
        format='%(asctime)s:[%(levelname)s]:(%(name)s):%(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )
    logger.info('Started')
    
    config = load_config()
    obs_controller = OBSRecordingController(
        host=config['host'],
        port=config['port'],
        password=config['password']
    )
    await obs_controller.connect()
    await obs_controller.disconnect()
    
    logger.info('Ended')
    
asyncio.run(main())

# Add date to log file to specify when log is from