from enum import Enum

class Phrases(Enum):
    START_REC_PHRASE = 'freya start recording'
    STOP_REC_PHRASE = 'freya stop recording'
    START_REPLAY_PHRASE = 'freya start the replay'
    STOP_REPLAY_PHRASE = 'freya stop the replay'
    START_EVERYTHING_PHRASE = 'freya start everything'
    STOP_EVERYTHING_PHRASE = 'freya stop everything'
    CLIP_PHRASE = ['freya clip it', 'freya clip that']

class Options(Enum):
    TTS_OPTION = 'TTS'
    TRAY_OPTION = 'System Tray'
    NONE_OPTION = 'None'