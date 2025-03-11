import logging
import asyncio
import simpleobsws

class OBSController:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        try:
            self.ws = simpleobsws.WebSocketClient(
                url=f'ws://{self.host}:{self.port}',
                password=self.password
            )
            await self.ws.connect()
            await self.ws.wait_until_identified()
            self.logger.info('Connected to OBS WebSocket successfully')
            return True
        except Exception as e:
            self.logger.error(f"ERROR: Connection failed, {e}")
            return False
    
    async def start_recording(self):
        if not self.ws:
            self.logger.error('ERROR: Not connected to OBS. Attempting to reconnect...')
            await self.connect()
        
        try:
            rec_request = simpleobsws.Request('GetRecordStatus')
            rec_response = await self.ws.call(rec_request)
            
            if not rec_response.ok():
                self.logger.error('ERROR: Failed to get recording status')
                return

            if not rec_response.responseData['outputActive']:
                start_rec_req = simpleobsws.Request('StartRecord')
                start_rec_res = await self.ws.call(start_rec_req)
                
                if start_rec_res.ok():
                    self.logger.info('Recording started sucessfully')
                else:
                    self.logger.error(f"ERROR: Failed to start recording, {e}")
            else:
                self.logger.info('Recording already in progress')
        except Exception as e:
            self.logger.error(f"ERROR: Failed to start recording, {e}")
            
            