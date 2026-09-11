import hashlib
import hmac
from influencer_agent.app.core.config import settings

def verify_signature(payload: bytes, signature: str) -> bool:
    
    if not signature:
        return False
        
    expected = hmac.new(
        key=settings.INSTAGRAM_APP_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha1
    ).hexdigest()
    
    # Meta sends signature as "sha1=..."
    return hmac.compare_digest(f"sha1={expected}", signature)
