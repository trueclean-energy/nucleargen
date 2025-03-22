import os
import json
import pytest
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from vyom.session import (
    get_user_data_dir,
    get_session_file,
    track_command_execution,
    check_command_prerequisites,
    clear_session,
    get_session_context
)

@pytest.fixture
def temp_session_dir(tmp_path):
    """Create a temporary directory for session files."""
    # Override the user data directory for testing
    os.environ['HOME'] = str(tmp_path)
    return tmp_path

@pytest.fixture
def sample_session_data():
    """Create sample session data for testing."""
    return {
        'commands_executed': [
            {
                'command': 'no-llm',
                'timestamp': datetime.now().isoformat(),
                'context': {'job_id': '123'}
            }
        ],
        'current_context': {'job_id': '123'},
        'last_updated': datetime.now().isoformat()
    }

def test_get_user_data_dir(temp_session_dir):
    """Test getting user data directory."""
    vyom_dir = get_user_data_dir()
    assert vyom_dir == temp_session_dir / '.vyom'
    assert vyom_dir.exists()

def test_get_session_file(temp_session_dir):
    """Test getting session file path."""
    session_file = get_session_file()
    assert session_file == temp_session_dir / '.vyom' / 'session.json'

def test_track_command_execution(temp_session_dir):
    """Test tracking command execution."""
    # Track a command
    track_command_execution('test_command', {'data': 'test'})
    
    # Verify session file was created
    session_file = get_session_file()
    assert session_file.exists()
    
    # Verify session data
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    assert len(session_data['commands_executed']) == 1
    assert session_data['commands_executed'][0]['command'] == 'test_command'
    assert session_data['commands_executed'][0]['context'] == {'data': 'test'}
    assert session_data['current_context'] == {'data': 'test'}
    assert 'last_updated' in session_data

def test_check_command_prerequisites(temp_session_dir, sample_session_data):
    """Test checking command prerequisites."""
    # Create session file with sample data
    session_file = get_session_file()
    with open(session_file, 'w') as f:
        json.dump(sample_session_data, f)
    
    # Test use-llm prerequisite
    assert check_command_prerequisites('use-llm') is True
    
    # Test without no-llm command
    sample_session_data['commands_executed'] = []
    with open(session_file, 'w') as f:
        json.dump(sample_session_data, f)
    assert check_command_prerequisites('use-llm') is False
    
    # Test expired session
    sample_session_data['last_updated'] = (datetime.now() - timedelta(days=8)).isoformat()
    with open(session_file, 'w') as f:
        json.dump(sample_session_data, f)
    assert check_command_prerequisites('use-llm') is False

def test_clear_session(temp_session_dir, sample_session_data):
    """Test clearing session data."""
    # Create session file
    session_file = get_session_file()
    with open(session_file, 'w') as f:
        json.dump(sample_session_data, f)
    
    # Clear session
    clear_session()
    
    # Verify session file was deleted
    assert not session_file.exists()

def test_get_session_context(temp_session_dir, sample_session_data):
    """Test getting session context."""
    # Create session file
    session_file = get_session_file()
    with open(session_file, 'w') as f:
        json.dump(sample_session_data, f)
    
    # Get context
    context = get_session_context()
    assert context == {'job_id': '123'}
    
    # Test with no session file
    clear_session()
    context = get_session_context()
    assert context is None

def test_session_expiration(temp_session_dir):
    """Test session expiration after 1 week."""
    # Create session data with old timestamp
    session_data = {
        'commands_executed': [
            {
                'command': 'no-llm',
                'timestamp': (datetime.now() - timedelta(days=8)).isoformat(),
                'context': {'job_id': '123'}
            }
        ],
        'current_context': {'job_id': '123'},
        'last_updated': (datetime.now() - timedelta(days=8)).isoformat()
    }
    
    # Write to session file
    session_file = get_session_file()
    with open(session_file, 'w') as f:
        json.dump(session_data, f)
    
    # Check prerequisites should fail due to expiration
    assert check_command_prerequisites('use-llm') is False

def test_concurrent_access(temp_session_dir):
    """Test concurrent access to session file."""
    def worker(worker_id):
        for i in range(5):
            track_command_execution(f'command_{worker_id}_{i}', {'worker': worker_id})
            time.sleep(0.1)  # Simulate work
    
    # Create multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Verify all commands were tracked
    session_file = get_session_file()
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    assert len(session_data['commands_executed']) == 15  # 3 workers * 5 commands each

def test_invalid_json(temp_session_dir):
    """Test handling of invalid JSON data."""
    session_file = get_session_file()
    
    # Write invalid JSON
    with open(session_file, 'w') as f:
        f.write('invalid json data')
    
    # Should handle gracefully
    assert check_command_prerequisites('use-llm') is False
    assert get_session_context() is None

def test_corrupted_session_file(temp_session_dir):
    """Test handling of corrupted session file."""
    session_file = get_session_file()
    
    # Create a corrupted file
    with open(session_file, 'w') as f:
        f.write('corrupted data')
    
    # Should handle gracefully
    track_command_execution('test_command', {'data': 'test'})
    
    # Verify new session was created
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    assert len(session_data['commands_executed']) == 1
    assert session_data['commands_executed'][0]['command'] == 'test_command'

def test_large_context_data(temp_session_dir):
    """Test handling of large context data."""
    # Create large context data
    large_context = {
        'data': 'x' * 1000000,  # 1MB of data
        'nested': {
            'array': ['x' * 1000 for _ in range(1000)],
            'dict': {str(i): 'x' * 100 for i in range(1000)}
        }
    }
    
    # Should handle gracefully
    track_command_execution('test_command', large_context)
    
    # Verify data was stored
    context = get_session_context()
    assert context is not None
    assert 'data' in context
    assert 'nested' in context 