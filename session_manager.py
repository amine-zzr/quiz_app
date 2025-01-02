"""
Session Management Module for Quiz App
Handles user session tracking, cleanup, and security
"""

from flask import request, session
from models import UserSession, db
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask_login import current_user

def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def get_client_info():
    """Get client IP and user agent"""
    return {
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    }

def create_session(user_id):
    """Create a new session for a user"""
    client_info = get_client_info()
    session_id = generate_session_id()
    
    # Create new session
    user_session = UserSession(
        user_id=user_id,
        session_id=session_id,
        ip_address=client_info['ip_address'],
        user_agent=client_info['user_agent']
    )
    
    db.session.add(user_session)
    db.session.commit()
    
    # Store session ID in Flask session
    session['session_id'] = session_id
    return user_session

def end_session(session_id):
    """End a specific session"""
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if user_session:
        user_session.is_active = False
        db.session.commit()
        return True
    return False

def end_all_sessions(user_id, except_session_id=None):
    """End all sessions for a user except the current one"""
    sessions = UserSession.query.filter_by(
        user_id=user_id,
        is_active=True
    )
    
    if except_session_id:
        sessions = sessions.filter(UserSession.session_id != except_session_id)
    
    for user_session in sessions:
        user_session.is_active = False
    
    db.session.commit()

def validate_session():
    """Validate the current session"""
    session_id = session.get('session_id')
    if not session_id:
        return False
        
    user_session = UserSession.query.filter_by(
        session_id=session_id,
        is_active=True
    ).first()
    
    if not user_session:
        return False
    
    # Update last activity
    user_session.update_activity()
    return True

def session_required(f):
    """Decorator to require valid session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_session():
            return {'message': 'Invalid or expired session'}, 401
        return f(*args, **kwargs)
    return decorated_function

def cleanup_sessions(max_age_hours=24):
    """Cleanup expired sessions"""
    return UserSession.cleanup_expired_sessions(max_age_hours)

def get_user_sessions(user_id):
    """Get all active sessions for a user"""
    return UserSession.get_active_sessions(user_id)

def get_session_info(session_id):
    """Get detailed information about a session"""
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        return None
        
    return {
        'id': user_session.id,
        'user_id': user_session.user_id,
        'ip_address': user_session.ip_address,
        'user_agent': user_session.user_agent,
        'created_at': user_session.created_at,
        'last_activity': user_session.last_activity,
        'is_active': user_session.is_active,
        'username': user_session.user_ref.username if user_session.user_ref else None
    }
