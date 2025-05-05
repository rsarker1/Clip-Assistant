import logging
import asyncio

from PySide6.QtCore import QThread, Signal, Slot

class VoiceRecognizerThread(QThread):
    error_occured = Signal(str)
    
    def __init__(self, voice_recognizer):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.voice_recognizer = voice_recognizer
        self.exec_loop = None

    def run(self):
        self.exec_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.exec_loop)

        try:
            self.voice_task = self.exec_loop.create_task(self.voice_recognizer.start())
            self.voice_task.add_done_callback(self.on_completion)
            self.exec_loop.run_forever()
        except Exception as e:
            self.logger.error(f'Thread encountered an issue: {e}', exc_info=True)
        finally:
            self.logger.info('Event loop closing. Shutting down thread.')
            self.exec_loop.close()
            
    def on_completion(self, task):
        self.logger.info('Task has been completed')
        try:
            # This re-raises any exception the task had
            task.result()
        except Exception as e:
            self.logger.error(f'Voice recognizer task failed: {e}')
            self.error_occured.emit('Could not connect to OBS. Change connection parameters then try again.')
            self.exec_loop.stop()
            return
                
        if self.exec_loop.is_running():
            self.voice_recognizer.isRunning = False
            self.logger.info('Shutting down voice recognition execution')
            try:
                self.stop_task = self.exec_loop.create_task(self.voice_recognizer.stop())
            except Exception as e:
                self.logger.error(f'Thread encountered an issue: {e}', exc_info=True)
            finally:
                self.exec_loop.call_soon_threadsafe(self.exec_loop.stop)    
    
    def req_stop(self):
        # Breaks guard clause in voice_recognizer to end task
        self.voice_recognizer.isRunning = False