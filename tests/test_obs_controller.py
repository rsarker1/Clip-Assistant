import pytest
import asyncio
from simpleobsws import WebSocketClient, Request
from obs_controller import OBSRecordingController

@pytest.fixture
def controller():
    return OBSRecordingController(host='localhost', port=4455, password='password')

class FakeResponse:
    def __init__(self, active=True, ok=True):
        self.responseData = {'outputActive': active}
        self.ok_val = ok
        
    def ok(self):
        return self.ok_val

def create_ws_and_setup(monkeypatch, controller, fake_call):
    fake_ws = type('W', (), {'call': fake_call})()
    monkeypatch.setattr(controller, 'ws', fake_ws)
    monkeypatch.setattr(controller, 'establish_connection', lambda: asyncio.sleep(0))
    
def create_fake_call(responses):
    async def fake_call(self, req):
        tup = responses.get(req.requestType, responses.get('default'))
        active, ok = tup
        return FakeResponse(active=active, ok=ok)
    return fake_call

@pytest.mark.asyncio
async def test_connect_success(monkeypatch, controller):
    class DummyWS:
        def __init__(self, url, password):
            assert url == 'ws://localhost:4455'
            assert password == 'password'
        async def connect(self): pass
        async def wait_until_identified(self): pass

    monkeypatch.setattr('obs_controller.WebSocketClient', DummyWS)
    await controller.connect()
    assert isinstance(controller.ws, DummyWS)
    
@pytest.mark.asyncio
async def test_start_recording_when_recording_inactive(monkeypatch, controller):
    fake_call = create_fake_call({
        'GetRecordStatus': (False, True),
        'StartRecord': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    await controller.start_recording()
    
@pytest.mark.asyncio
async def test_start_recording_when_recording_active(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('WARNING')
    await controller.start_recording()
    assert 'Recording already in progress' in caplog.text

@pytest.mark.asyncio
async def test_start_recording_raises_if_status_not_ok(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.start_recording()
    assert 'Could not get recording status' in str(exc.value)
    assert 'Failed to start recording' in caplog.text
    
@pytest.mark.asyncio
async def test_start_recording_raises_if_start_fails(monkeypatch, controller, caplog): 
    fake_call = create_fake_call({
        'GetRecordStatus': (False, True),
        'StartRecord': (False, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)

    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.start_recording()
    assert 'Could not start recording' in str(exc.value)
    assert 'Failed to start recording' in caplog.text
    
@pytest.mark.asyncio
async def test_stop_recording_when_recording_active(monkeypatch, controller):
    fake_call = create_fake_call({
        'GetRecordStatus': (True, True),
        'StopRecord': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    await controller.stop_recording()
    
@pytest.mark.asyncio
async def test_stop_recording_when_recording_inactive(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('WARNING')
    await controller.stop_recording()
    assert 'No active recording' in caplog.text
    
@pytest.mark.asyncio
async def test_stop_recording_raises_if_status_not_ok(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.stop_recording()
    assert 'Could not get recording status' in str(exc.value)
    assert 'Failed to stop recording' in caplog.text
    
@pytest.mark.asyncio
async def test_stop_recording_raises_if_stop_fails(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'GetRecordStatus': (True, True),
        'StopRecord': (True, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)

    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.stop_recording()
    assert 'Could not stop recording' in str(exc.value)
    assert 'Failed to stop recording' in caplog.text
    
@pytest.mark.asyncio
async def test_start_replay_buffer_when_buffer_inactive(monkeypatch, controller):
    fake_call = create_fake_call({
        'GetReplayBufferStatus': (False, True),
        'StartReplayBuffer': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    await controller.start_replay_buffer()

@pytest.mark.asyncio
async def test_start_replay_buffer_when_buffer_active(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('WARNING')
    await controller.start_replay_buffer()
    assert 'Replay buffer already active' in caplog.text
    
@pytest.mark.asyncio
async def test_start_replay_buffer_raises_if_status_not_ok(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, False),
    })  
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.start_replay_buffer()
    assert 'Could not get replay status' in str(exc.value)
    assert 'Failed to start replay buffer' in caplog.text
    
@pytest.mark.asyncio
async def test_start_replay_buffer_raises_if_start_fails(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'GetReplayBufferStatus': (False, True),
        'StartReplayBuffer': (False, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)

    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.start_replay_buffer()
    assert 'Could not start replay buffer' in str(exc.value)
    assert 'Failed to start replay buffer' in caplog.text
    
@pytest.mark.asyncio
async def test_stop_replay_buffer_when_buffer_active(monkeypatch, controller):
    fake_call = create_fake_call({
        'GetReplayBufferStatus': (True, True),
        'StopReplayBuffer': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    await controller.stop_replay_buffer()
    
@pytest.mark.asyncio
async def test_stop_replay_buffer_when_buffer_inactive(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('WARNING')
    await controller.stop_replay_buffer()
    assert 'Replay buffer not active' in caplog.text

@pytest.mark.asyncio
async def test_stop_replay_buffer_raises_if_status_not_ok(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.stop_replay_buffer()
    assert 'Could not get replay status' in str(exc.value)
    assert 'Failed to stop replay buffer' in caplog.text
    
@pytest.mark.asyncio
async def test_stop_replay_buffer_raises_if_stop_fails(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'GetReplayBufferStatus': (True, True),
        'StopReplayBuffer': (True, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)

    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.stop_replay_buffer()
    assert 'Could not stop replay buffer' in str(exc.value)
    assert 'Failed to stop replay buffer' in caplog.text
    
@pytest.mark.asyncio
async def test_save_replay_buffer_when_buffer_active(monkeypatch, controller):
    fake_call = create_fake_call({
        'GetReplayBufferStatus': (True, True),
        'SaveReplayBuffer': (True, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    await controller.save_replay_buffer()
    
@pytest.mark.asyncio
async def test_save_replay_buffer_when_buffer_inactive(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, True),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('WARNING')
    await controller.save_replay_buffer()
    assert 'Replay buffer already saving' in caplog.text
    
@pytest.mark.asyncio
async def test_save_replay_buffer_raises_if_status_not_ok(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'default': (False, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)
    
    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.save_replay_buffer()
    assert 'Could not get replay status' in str(exc.value)
    assert 'Failed to save replay buffer' in caplog.text
    
@pytest.mark.asyncio
async def test_save_replay_buffer_raises_if_stop_fails(monkeypatch, controller, caplog):
    fake_call = create_fake_call({
        'GetReplayBufferStatus': (True, True),
        'SaveReplayBuffer': (True, False),
    })
    create_ws_and_setup(monkeypatch, controller, fake_call)

    caplog.set_level('ERROR')
    with pytest.raises(Exception) as exc:
        await controller.save_replay_buffer()
    assert 'Could not save replay buffer' in str(exc.value)
    assert 'Failed to save replay buffer' in caplog.text