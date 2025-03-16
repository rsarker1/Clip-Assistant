import asyncio
import logging
import sys
from datetime import datetime
from yaml_config import load_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

def setup_logging():
    log_file = logging.getLogger(__name__)
    current_date = datetime.today().strftime('%Y_%m_%d')
    logging.basicConfig(
        filename=f'clip_assistant_{current_date}.log', 
        filemode='w', 
        format='%(asctime)s:[%(levelname)s]:(%(name)s):%(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )
    return log_file

async def main():
    logger = setup_logging()
    logger.info('Started')
    
    config = load_config()
    obs_controller = OBSRecordingController(
        host=config['host'],
        port=config['port'],
        password=config['password']
    )
    await obs_controller.connect()
    hold = VoskVoiceRecognizer(obs_controller)
    try:
        await hold.start()
    except KeyboardInterrupt:
        await obs_controller.disconnect()
        sys.exit(0)    
    finally:
        logger.info('Ended')
    
asyncio.run(main())
