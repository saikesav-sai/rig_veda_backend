"""
Optional Session Management Utilities
This module provides session tracking for individual users.
Use this if you want to track user sessions, implement rate limiting per user, or maintain conversation history.
"""

import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional


class SessionManager:
    """
    Thread-safe session manager for tracking user sessions.
    This is optional and can be used for:
    - Rate limiting per user
    - Conversation history
    - User analytics
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        with self._lock:
            if not self._initialized:
                self.sessions: Dict[str, dict] = {}
                self.session_timeout = timedelta(hours=1)
                self._initialized = True
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session and return session ID"""
        session_id = user_id or str(uuid.uuid4())
        
        with self._lock:
            self.sessions[session_id] = {
                'created_at': datetime.now(),
                'last_active': datetime.now(),
                'request_count': 0,
                'conversation_history': []
            }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data if exists and not expired"""
        with self._lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check if session expired
            if datetime.now() - session['last_active'] > self.session_timeout:
                del self.sessions[session_id]
                return None
            
            return session
    
    def update_session(self, session_id: str, data: dict):
        """Update session data"""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id]['last_active'] = datetime.now()
                self.sessions[session_id]['request_count'] += 1
                
                # Merge additional data
                for key, value in data.items():
                    if key == 'conversation_history':
                        self.sessions[session_id]['conversation_history'].append(value)
                    else:
                        self.sessions[session_id][key] = value
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        with self._lock:
            current_time = datetime.now()
            expired = [
                sid for sid, session in self.sessions.items()
                if current_time - session['last_active'] > self.session_timeout
            ]
            
            for sid in expired:
                del self.sessions[sid]
            
            return len(expired)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        self.cleanup_expired_sessions()
        return len(self.sessions)


# Optional: Flask integration example
def init_session_middleware(app):
    """
    Add session tracking to Flask app.
    Usage in app.py:
        from utils.session_utils import init_session_middleware
        init_session_middleware(app)
    """
    from flask import g, request
    
    session_manager = SessionManager()
    
    @app.before_request
    def before_request():
        # Get or create session
        session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
        
        if not session_id or not session_manager.get_session(session_id):
            session_id = session_manager.create_session()
        
        g.session_id = session_id
        g.session_manager = session_manager
    
    @app.after_request
    def after_request(response):
        # Set session cookie
        if hasattr(g, 'session_id'):
            response.set_cookie('session_id', g.session_id, 
                              max_age=3600,  # 1 hour
                              httponly=True,
                              samesite='Lax')
        return response
    
    return session_manager


# Optional: Rate limiting per session
class RateLimiter:
    """
    Simple rate limiter per session.
    Example: Limit to 10 requests per minute per user.
    """
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window)
        self.request_history: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, session_id: str) -> bool:
        """Check if request is allowed for this session"""
        with self._lock:
            current_time = datetime.now()
            
            # Initialize history for new session
            if session_id not in self.request_history:
                self.request_history[session_id] = []
            
            # Remove old requests outside time window
            self.request_history[session_id] = [
                timestamp for timestamp in self.request_history[session_id]
                if current_time - timestamp < self.time_window
            ]
            
            # Check if limit exceeded
            if len(self.request_history[session_id]) >= self.max_requests:
                return False
            
            # Add current request
            self.request_history[session_id].append(current_time)
            return True
    
    def get_remaining_requests(self, session_id: str) -> int:
        """Get number of remaining requests in current window"""
        with self._lock:
            if session_id not in self.request_history:
                return self.max_requests
            
            current_time = datetime.now()
            recent_requests = [
                timestamp for timestamp in self.request_history[session_id]
                if current_time - timestamp < self.time_window
            ]
            
            return max(0, self.max_requests - len(recent_requests))


# Example usage in routes
"""
from utils.session_utils import SessionManager, RateLimiter
from flask import g

# In your route
@chat_bot.route("/api/chat/intent", methods=["POST"])
def chat_intent():
    session_manager = SessionManager()
    rate_limiter = RateLimiter(max_requests=10, time_window=60)
    
    # Get session
    session_id = g.get('session_id') or request.headers.get('X-Session-ID')
    if not session_id:
        session_id = session_manager.create_session()
    
    # Check rate limit
    if not rate_limiter.is_allowed(session_id):
        return jsonify({
            "error": "Rate limit exceeded. Please try again later.",
            "remaining_requests": rate_limiter.get_remaining_requests(session_id)
        }), 429
    
    # Your existing code...
    query = request.get_json().get("query", "")
    result = get_answer(query)
    
    # Update session with conversation
    session_manager.update_session(session_id, {
        'conversation_history': {
            'query': query,
            'response': result,
            'timestamp': datetime.now().isoformat()
        }
    })
    
    return jsonify(result)
"""
