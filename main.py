import asyncio
import logging
import sys
from datetime import datetime
from freya_app import Freya_for_OBS

from voice_recognizer import VoskVoiceRecognizer
from obs_controller import OBSRecordingController
from yaml_config import load_config
        
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
    app = Freya_for_OBS() 
    app.run()
    
    # config = load_config()
    # obs_controller = OBSRecordingController(
    #     host=config['host'],
    #     port=config['port'],
    #     password=config['password']
    # )
    
    # voice_recognize = VoskVoiceRecognizer(obs_controller)
    # try:
    #     await voice_recognize.start()
    # except KeyboardInterrupt:
    #     await voice_recognize.stop()
    #     sys.exit(0)    
    # finally:
    #     logger.info('Ended')
    

    
asyncio.run(main())

