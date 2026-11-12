from datetime import datetime, timezone
from flask import request
from app.extensions import db
from app.models.audit import AuditLog


def log_action(actor_user_id, action, entity_type=None, entity_id=None, change_summary=None):
    """Write a row to the audit log. Never store passwords or tokens."""
    client_ip = None
    if request:
        client_ip = (request.headers.get('CF-Connecting-IP') or
                     request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
                     request.remote_addr)
        if client_ip:
            client_ip = client_ip[:45]

    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action[:50] if action else action,
        entity_type=entity_type[:50] if entity_type else entity_type,
        entity_id=entity_id,
        change_summary=change_summary,
        ip_address=client_ip,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(entry)
    # Committed by the caller's transaction to keep audit log atomic with data changes
