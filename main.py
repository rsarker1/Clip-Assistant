import asyncio
import logging
from yaml_config import load_config
from obs_controller import OBSRecordingController
from voice_recognizer import VoskVoiceRecognizer

async def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='clip_assistant.log', filemode='w', level=logging.INFO)
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