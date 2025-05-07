import os
import yaml
import pytest
import shutil
from yaml_config import *


@pytest.fixture(autouse=True)
def backup_and_restore_config():
    backup_file = None
    if os.path.exists(FILE_NAME):
        backup_file = f"{FILE_NAME}.bak"
        shutil.copy(FILE_NAME, backup_file)
        os.remove(FILE_NAME)

    yield

    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
    if backup_file and os.path.exists(backup_file):
        shutil.move(backup_file, FILE_NAME)

def test_is_valid_config_returns_true_for_default():
    assert is_valid_config(DEFAULT_CONFIG)
    
def test_is_valid_config_returns_false_for_missing_key():
    config = DEFAULT_CONFIG.copy()
    config.pop('host', None)
    assert not is_valid_config(config)
    
def test_save_and_get_config():
    save_config(DEFAULT_CONFIG)
    result = get_config()
    assert result == DEFAULT_CONFIG

def test_save_config_with_updates():
    updates = {'host': '127.0.0.1'}
    save_config(DEFAULT_CONFIG, updates=updates)
    result = get_config()
    assert result['host'] == '127.0.0.1'
    for key in DEFAULT_CONFIG:
        assert key in result

def test_load_config_creates_default_if_missing():
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
    result = load_config()
    assert result == DEFAULT_CONFIG

def test_load_config_reads_existing_config():
    with open(FILE_NAME, 'w') as f:
        yaml.dump(DEFAULT_CONFIG, f)
    result = load_config()
    assert result == DEFAULT_CONFIG

def test_load_config_invalid_triggers_regeneration(caplog):
    invalid = {'host': 'localhost'}  
    with open(FILE_NAME, 'w') as f:
        yaml.dump(invalid, f)

    with caplog.at_level('WARNING'):
        result = load_config()
        assert result == DEFAULT_CONFIG
        assert 'invalid' in caplog.text.lower()
        
def test_load_config_invalid_values_triggers_regeneration(caplog):
    invalid_values = {
        'host': 123,
        'port': 'string',
        'password': 1111,
        'notifications': 1111,
        'startup': 1111
    } 
    with open(FILE_NAME, 'w') as f:
        yaml.dump(invalid_values, f)
    
    with caplog.at_level('WARNING'):
        result = load_config()
        assert result == DEFAULT_CONFIG
        assert 'invalid' in caplog.text.lower()