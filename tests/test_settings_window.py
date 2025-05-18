import pytest
from settings_window import SettingsWindow
from enums import Options
from PySide6.QtCore import Qt

@pytest.fixture(autouse=True)
def disable_get_config(monkeypatch):
    monkeypatch.setattr('settings_window.get_config', lambda: {'notifications': Options.TTS_OPTION.value, 'startup': False})
    
@pytest.mark.parametrize('notification, startup', [
    (Options.TTS_OPTION.value, False),
    (Options.TRAY_OPTION.value, True),
    (Options.NONE_OPTION.value, False),
])
def test_general_tab_initial_values(monkeypatch, qtbot, notification, startup):
    config = {'notifications': notification, 'startup': startup}
    monkeypatch.setattr('settings_window.get_config', lambda: config)

    win = SettingsWindow()
    qtbot.addWidget(win)

    dropdown = win.notif_dropdown
    checkbox = win.startup_checkbox

    assert dropdown.currentText() == notification
    assert checkbox.isChecked() == startup

def test_save_general_settings_emits_on_dropdown_change(qtbot):
    win = SettingsWindow()
    qtbot.addWidget(win)

    new_index = (win.notif_dropdown.currentIndex() + 1) % win.notif_dropdown.count()

    with qtbot.waitSignal(win.general_settings_updated, timeout=500) as sig:
        win.notif_dropdown.setCurrentIndex(new_index)

    new_value, new_startup = sig.args
    assert new_value == win.notif_dropdown.currentText()
    assert isinstance(new_startup, bool)
    
def test_save_general_settings_emits_on_checkbox_toggle(qtbot):
    win = SettingsWindow()
    qtbot.addWidget(win)

    with qtbot.waitSignal(win.general_settings_updated, timeout=500) as sig:
        win.startup_checkbox.toggle()
    new_value, new_startup = sig.args
    assert new_startup == win.startup_checkbox.isChecked()
    
def test_save_obs_settings_validation_errors(qtbot):
    win = SettingsWindow()
    qtbot.addWidget(win)

    win.host_input.setText('')
    win.port_input.setText('')
    win.password_input.setText('')
    win.save_obs_settings()
    assert win.error_label.text() == 'Error: Empty text not allowed'

    win.host_input.setText('host')
    win.port_input.setText('invalid')
    win.password_input.setText('pass')
    win.save_obs_settings()
    assert win.error_label.text() == 'Error: Port must be an integer'

def test_save_obs_settings_emits_and_closes(qtbot):
    win = SettingsWindow()
    qtbot.addWidget(win)

    host, port, pw = 'host', 8080, 'pass'
    win.host_input.setText(host)
    win.port_input.setText(str(port))
    win.password_input.setText(pw)

    with qtbot.waitSignal(win.obs_settings_updated, timeout=500) as sig:
        win.save_obs_settings()

    sig_host, sig_port, sig_pw = sig.args
    assert sig_host == host
    assert sig_port == port
    assert sig_pw == pw

    assert not win.isVisible()