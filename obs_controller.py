import logging
from simpleobsws import WebSocketClient, Request

class OBSRecordingController:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        try:
            self.ws = WebSocketClient(
                url=f'ws://{self.host}:{self.port}',
                password=self.password
            )
            await self.ws.connect()
            await self.ws.wait_until_identified()
            self.logger.info('Connected to OBS WebSocket successfully')
        except Exception as e:
            self.logger.error(f'ERROR: Connection failed, {e}')
    
    async def disconnect(self):
        if self.ws:
            await self.ws.disconnect()
            self.logger.info('Disconnected from OBS WebSocket')
    
    async def establish_connection(self):
        if not self.ws:
            self.logger.error('ERROR: Not connected to OBS. Attempting to reconnect...')
            await self.connect()
    
    async def start_recording(self):
        await self.establish_connection()
        
        try:
            rec_request = Request('GetRecordStatus')
            rec_response = await self.ws.call(rec_request)
            
            if not rec_response.ok():
                self.logger.error('ERROR: Failed to get recording status')
                return

            if not rec_response.responseData['outputActive']:
                start_rec_req = Request('StartRecord')
                start_rec_res = await self.ws.call(start_rec_req)
                
                if start_rec_res.ok():
                    self.logger.info('Recording started sucessfully')
                else:
                    self.logger.error(f'ERROR: Failed to start recording, {e}')
            else:
                self.logger.info('Recording already in progress')
        except Exception as e:
            self.logger.error(f'ERROR: Failed to start recording, {e}')
            
    async def stop_recording(self):
        await self.establish_connection()
        
        try:
            rec_request = Request('GetRecordStatus')
            rec_response = await self.ws.call(rec_request)
            
            if not rec_response.ok():
                self.logger.error('ERROR: Failed to get recording status')
                return
            
            if not rec_response.responseData['outputActive']:
                stop_rec_req = Request('StopRecord')
                stop_rec_res = await self.ws.call(stop_rec_req)
                
                if stop_rec_res.ok():
                    self.logger.info('Recording stopped sucessfully')
                else:
                    self.logger.error(f'ERROR: Failed to stop recording, {e}')
            else:
                self.logger.info('No active recording')
            
        except Exception as e:
            self.logger.error(f'ERROR: Failed to stop recording, {e}')
            