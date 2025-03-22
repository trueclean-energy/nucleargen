import os
import json
import logging
import fcntl
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MAX_CONTEXT_SIZE = 10 * 1024 * 1024  # 10MB limit for context data
SESSION_EXPIRY_HOURS = 24

def get_user_data_dir() -> Path:
    """Get the user data directory for storing session data."""
    # Use ~/.vyom directory in user's home folder
    home = Path.home()
    vyom_dir = home / '.vyom'
    vyom_dir.mkdir(exist_ok=True)
    return vyom_dir

def get_session_file() -> Path:
    """Get the path to the session file."""
    return get_user_data_dir() / "session.json"

def _acquire_file_lock(file_handle, max_retries: int = 10, retry_delay: float = 0.1) -> bool:
    """Acquire an exclusive lock on the file with retries."""
    for attempt in range(max_retries):
        try:
            fcntl.flock(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError) as e:
            if attempt < max_retries - 1:
                logger.debug(f"Lock attempt {attempt + 1} failed, retrying: {e}")
                time.sleep(retry_delay)
            else:
                logger.warning(f"Failed to acquire lock after {max_retries} attempts")
    return False

def _release_file_lock(file_handle):
    """Release the lock on the file."""
    try:
        fcntl.flock(file_handle, fcntl.LOCK_UN)
    except (IOError, OSError) as e:
        logger.warning(f"Failed to release lock: {e}")

def _validate_context_size(data: Dict[str, Any]) -> bool:
    """Validate that context data is within size limits."""
    try:
        serialized = json.dumps(data)
        return len(serialized.encode('utf-8')) <= MAX_CONTEXT_SIZE
    except (TypeError, OverflowError):
        return False

def _read_session_data(file_handle) -> Dict[str, Any]:
    """Read and parse session data from file handle."""
    try:
        file_handle.seek(0)
        content = file_handle.read().strip()
        if not content:
            return _create_fresh_session()
        data = json.loads(content)
        if not isinstance(data, dict) or 'commands_executed' not in data:
            return _create_fresh_session()
        return data
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read session data, starting fresh: {e}")
        return _create_fresh_session()

def _create_fresh_session() -> Dict[str, Any]:
    """Create a fresh session data structure."""
    return {
        'commands_executed': [],
        'current_context': None,
        'last_updated': datetime.now().isoformat()
    }

def track_command_execution(command_name: str, data_context: Optional[Dict[str, Any]] = None) -> bool:
    """Track command execution in the session file."""
    if data_context and not _validate_context_size(data_context):
        logger.warning("Context data exceeds size limit")
        return False

    session_file = get_session_file()
    try:
        os.makedirs(os.path.dirname(session_file), exist_ok=True)
        
        # Open in read+ mode to handle concurrent access properly
        with open(session_file, 'r+' if os.path.exists(session_file) else 'w+') as f:
            if not _acquire_file_lock(f):
                return False
            
            try:
                session_data = _read_session_data(f)
                
                command_data = {
                    'command': command_name,
                    'timestamp': datetime.now().isoformat(),
                    'context': data_context
                }
                
                session_data['commands_executed'].append(command_data)
                session_data['current_context'] = data_context
                session_data['last_updated'] = datetime.now().isoformat()
                
                f.seek(0)
                f.truncate()
                json.dump(session_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
                return True
                
            finally:
                _release_file_lock(f)
                
    except Exception as e:
        logger.warning(f"Unable to track session: {e}")
        return False

def check_command_prerequisites(command_name: str) -> bool:
    """Check if the prerequisites for a command have been met."""
    session_file = get_session_file()
    
    try:
        if not os.path.exists(session_file):
            return False
            
        with open(session_file, 'r') as f:
            if not _acquire_file_lock(f):
                return False
                
            try:
                session_data = _read_session_data(f)
                if not session_data or 'commands_executed' not in session_data:
                    return False
                
                # Check session expiration
                try:
                    last_updated = datetime.fromisoformat(session_data['last_updated'])
                    if datetime.now() - last_updated > timedelta(hours=SESSION_EXPIRY_HOURS):
                        return False
                except (KeyError, ValueError):
                    return False
                
                # Check command history
                if command_name == 'use-llm':
                    return any(cmd['command'] == 'no-llm' for cmd in session_data['commands_executed'])
                
                return True
                
            finally:
                _release_file_lock(f)
                
    except Exception as e:
        logger.warning(f"Error checking command prerequisites: {e}")
        return False

def clear_session() -> bool:
    """Clear all session data by deleting the session file."""
    session_file = get_session_file()
    
    try:
        if os.path.exists(session_file):
            os.remove(session_file)
        return True
        
    except Exception as e:
        logger.warning(f"Error clearing session: {e}")
        return False

def get_session_context() -> Optional[Dict[str, Any]]:
    """Get the current session context."""
    session_file = get_session_file()
    
    try:
        if not os.path.exists(session_file):
            return None
            
        with open(session_file, 'r') as f:
            if not _acquire_file_lock(f):
                return None
                
            try:
                session_data = _read_session_data(f)
                return session_data.get('current_context')
            finally:
                _release_file_lock(f)
                
    except Exception as e:
        logger.warning(f"Unable to read session context: {e}")
        return None 