import logging
import sys
from simpleobsws import WebSocketClient, Request

from PySide6.QtCore import QObject, Signal, Slot

class OBSRecordingController(QObject):
    def __init__(self, host, port, password):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        
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
            self.logger.error(f'OBS connection failed: {e}')
            raise
    
    async def disconnect(self):
        if self.ws:
            await self.ws.disconnect()
            self.logger.info('Disconnected from OBS WebSocket')
    
    async def establish_connection(self):
        if not self.ws:
            self.logger.warning('Not connected to OBS. Attempting to reconnect...')
            await self.connect()
    
    async def start_recording(self):
        await self.establish_connection()
        
        try:
            rec_request = Request('GetRecordStatus')
            rec_response = await self.ws.call(rec_request)
            
            if not rec_response.ok():
                raise Exception('Could not get recording status')

            if not rec_response.responseData['outputActive']:
                start_rec_req = Request('StartRecord')
                start_rec_res = await self.ws.call(start_rec_req)
                
                if start_rec_res.ok():
                    self.logger.info('Recording started sucessfully')
                else:
                    raise Exception('Could not start recording')
            else:
                self.logger.warning('Recording already in progress')
                
        except Exception as e:
            self.logger.error(f'Failed to start recording: {e}')
            raise
            
    async def stop_recording(self):
        await self.establish_connection()
        
        try:
            rec_request = Request('GetRecordStatus')
            rec_response = await self.ws.call(rec_request)
            
            if not rec_response.ok():
                raise Exception('Could not get recording status')
            
            if rec_response.responseData['outputActive']:
                stop_rec_req = Request('StopRecord')
                stop_rec_res = await self.ws.call(stop_rec_req)
                
                if stop_rec_res.ok():
                    self.logger.info('Recording stopped sucessfully')
                else:
                    raise Exception('Could not stop recording')
            else:
                self.logger.warning('No active recording')
            
        except Exception as e:
            self.logger.error(f'Failed to stop recording: {e}')
            raise
            
    async def start_replay_buffer(self):
        await self.establish_connection()
        
        try:
            replay_request = Request('GetReplayBufferStatus')
            replay_response = await self.ws.call(replay_request)
            
            if not replay_response.ok():
                raise Exception('Could not get replay status')
                
            if not replay_response.responseData['outputActive']:
                start_replay_req = Request('StartReplayBuffer')
                start_replay_res = await self.ws.call(start_replay_req)
                
                if start_replay_res.ok():
                    self.logger.info('Replay buffer started successfully')
                else:
                    raise Exception('Could not start replay buffer')
            else:
                self.logger.warning('Replay buffer already active')
            
        except Exception as e:
            self.logger.error(f'Failed to start replay buffer: {e}')
            raise
            
    async def stop_replay_buffer(self):
        await self.establish_connection()
        
        try:
            replay_request = Request('GetReplayBufferStatus')
            replay_response = await self.ws.call(replay_request)
            
            if not replay_response.ok():
                raise Exception('Could not get replay status')
                
            if replay_response.responseData['outputActive']:
                stop_replay_req = Request('StopReplayBuffer')
                stop_replay_res = await self.ws.call(stop_replay_req)
                
                if stop_replay_res.ok():
                    self.logger.info('Replay buffer stopped successfully')
                else:
                    raise Exception('Could not stop replay buffer')
            else:
                self.logger.warning('Replay buffer not active')
            
        except Exception as e:
            self.logger.error(f'Failed to stop replay buffer: {e}')
            raise
        
    async def save_replay_buffer(self):
        await self.establish_connection()
        
        try:
            replay_request = Request('GetReplayBufferStatus')
            replay_response = await self.ws.call(replay_request)
            if not replay_response.ok():
                raise Exception('Could not get replay status') 
                
            if replay_response.responseData['outputActive']:
                save_replay_req = Request('SaveReplayBuffer')
                save_replay_res = await self.ws.call(save_replay_req)
                
                if save_replay_res.ok():
                    self.logger.info('Replay buffer saved successfully')
                else:
                    raise Exception('Could not save replay buffer')
            else:
                self.logger.warning('Replay buffer already saving')
            
        except Exception as e:
            self.logger.error(f'Failed to save replay buffer: {e}')
            raise