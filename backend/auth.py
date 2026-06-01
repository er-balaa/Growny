from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt
import time

FIREBASE_PROJECT_ID = "growny-co"
GOOGLE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"

_cached_certs = None
_certs_expiry = None

security = HTTPBearer()

async def get_google_certs():
    global _cached_certs, _certs_expiry
    now = time.time()
    
    if _cached_certs and _certs_expiry and now < _certs_expiry:
        return _cached_certs
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_CERTS_URL)
            response.raise_for_status()
            _cached_certs = response.json()
            
            cache_control = response.headers.get('cache-control', '')
            max_age = 3600
            for part in cache_control.split(','):
                part = part.strip()
                if part.startswith('max-age='):
                    try:
                        max_age = int(part.split('=')[1])
                    except (ValueError, IndexError):
                        pass
            
            _certs_expiry = now + max_age
            return _cached_certs
    except Exception as e:
        if _cached_certs:
            return _cached_certs
        raise

def verify_firebase_id_token(token: str, certs: dict) -> dict:
    from cryptography.x509 import load_pem_x509_certificate
    from cryptography.hazmat.backends import default_backend
    
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError as e:
        raise ValueError(f"Invalid token format: {e}")
    
    kid = unverified_header.get('kid')
    if not kid:
        raise ValueError("Token header missing 'kid'")
    
    cert_pem = certs.get(kid)
    if not cert_pem:
        raise ValueError(f"No matching certificate found for kid: {kid}")
    
    cert = load_pem_x509_certificate(cert_pem.encode('utf-8'), default_backend())
    public_key = cert.public_key()
    
    try:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=FIREBASE_PROJECT_ID,
            issuer=f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}",
            options={
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid token: {e}")

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        if not token or token == "test":
            raise HTTPException(status_code=401, detail="Invalid token")
        
        certs = await get_google_certs()
        decoded_token = verify_firebase_id_token(token, certs)
        
        uid = decoded_token.get('user_id') or decoded_token.get('sub')
        email = decoded_token.get('email', '')
        
        user_data = {
            'uid': uid,
            'email': email,
            'name': decoded_token.get('name', ''),
            'picture': decoded_token.get('picture', ''),
            'email_verified': decoded_token.get('email_verified', False),
        }

        # Cache user email for background jobs
        if uid and email:
            import json, os, pathlib
            cache_file = str(pathlib.Path(__file__).parent / "user_emails.json")
            try:
                if os.path.exists(cache_file):
                    with open(cache_file, "r") as f:
                        cache = json.load(f)
                else:
                    cache = {}
                if cache.get(uid, {}).get("email") != email:
                    cache[uid] = {"email": email, "name": user_data['name']}
                    with open(cache_file, "w") as f:
                        json.dump(cache, f)
            except Exception:
                pass
        
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
