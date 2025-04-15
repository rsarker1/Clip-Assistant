import asyncio
import logging
import sys
from datetime import datetime
from freya_app import Freya_for_OBS
        
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
    
asyncio.run(main())
