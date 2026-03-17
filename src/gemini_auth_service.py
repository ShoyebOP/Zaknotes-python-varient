import os
import json
import time
import hashlib
import base64
import secrets
import logging
import httpx
from typing import Optional, Dict, List, TypedDict
from urllib.parse import urlencode, urlparse, parse_qs

logger = logging.getLogger(__name__)

class GeminiCliAuthRecord(TypedDict):
    access: str
    refresh: str
    expires: int
    projectId: str
    clientId: str
    clientSecret: Optional[str]
    email: Optional[str]
    status: str  # 'valid' or 'invalid'

class GeminiAuthService:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    CODE_ASSIST_ENDPOINT = "https://cloudcode-pa.googleapis.com"
    REDIRECT_URI = "http://localhost:8085/oauth2callback"
    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    def __init__(self, auth_file: str = "gemini_cli_auth.json"):
        self.auth_file = auth_file
        self.accounts: List[GeminiCliAuthRecord] = self._load_accounts()
        self.current_index = 0

    def _load_accounts(self) -> List[GeminiCliAuthRecord]:
        if not os.path.exists(self.auth_file):
            return []
        try:
            with open(self.auth_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return [data] # Handle legacy single-account format
        except (json.JSONDecodeError, IOError):
            return []

    def _save_accounts(self):
        try:
            with open(self.auth_file, 'w') as f:
                json.dump(self.accounts, f, indent=4)
        except IOError as e:
            logger.error(f"Error saving auth records: {e}")

    def generate_pkce(self):
        verifier = secrets.token_hex(32)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        return verifier, challenge

    def build_auth_url(self, client_id: str, challenge: str, verifier: str) -> str:
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": " ".join(self.SCOPES),
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": verifier,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, client_id: str, client_secret: Optional[str], code: str, verifier: str) -> GeminiCliAuthRecord:
        data = {
            "client_id": client_id,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.REDIRECT_URI,
            "code_verifier": verifier,
        }
        if client_secret:
            data["client_secret"] = client_secret

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data)
            if resp.status_code != 200:
                raise Exception(f"Token exchange failed: {resp.text}")
            
            token_data = resp.json()
            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data["expires_in"]

            if not refresh_token:
                raise Exception("No refresh token received. Ensure you haven't already authorized this app or use 'prompt=consent'.")

            email = await self._get_user_email(access_token)
            project_id = await self._discover_project(access_token)
            
            # Use 90 mins or expires_in - 5 mins, whichever is smaller to be safe
            expires_at = int(time.time() * 1000) + (expires_in * 1000) - (5 * 60 * 1000)

            record: GeminiCliAuthRecord = {
                "access": access_token,
                "refresh": refresh_token,
                "expires": expires_at,
                "projectId": project_id,
                "clientId": client_id,
                "clientSecret": client_secret,
                "email": email,
                "status": "valid"
            }
            
            # Add or update
            self._update_or_add_account(record)
            return record

    def _update_or_add_account(self, record: GeminiCliAuthRecord):
        for i, acc in enumerate(self.accounts):
            if acc["email"] == record["email"]:
                self.accounts[i] = record
                self._save_accounts()
                return
        self.accounts.append(record)
        self._save_accounts()

    async def refresh_token(self, record: GeminiCliAuthRecord) -> GeminiCliAuthRecord:
        data = {
            "client_id": record["clientId"],
            "refresh_token": record["refresh"],
            "grant_type": "refresh_token",
        }
        if record["clientSecret"]:
            data["client_secret"] = record["clientSecret"]

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data)
            if resp.status_code != 200:
                record["status"] = "invalid"
                self._save_accounts()
                raise Exception(f"Token refresh failed: {resp.text}")
            
            token_data = resp.json()
            record["access"] = token_data["access_token"]
            if "refresh_token" in token_data:
                record["refresh"] = token_data["refresh_token"]
            
            expires_in = token_data["expires_in"]
            record["expires"] = int(time.time() * 1000) + (expires_in * 1000) - (5 * 60 * 1000)
            record["status"] = "valid"
            
            self._save_accounts()
            return record

    async def _get_user_email(self, access_token: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
                if resp.status_code == 200:
                    return resp.json().get("email")
        except Exception:
            return None
        return None

    async def _discover_project(self, access_token: str) -> str:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "google-api-nodejs-client/9.15.1",
            "X-Goog-Api-Client": "gl-node/22.17.0",
        }
        
        env_project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        
        load_body = {
            "cloudaicompanionProject": env_project,
            "metadata": {
                "ideType": "IDE_UNSPECIFIED",
                "platform": "PLATFORM_UNSPECIFIED",
                "pluginType": "GEMINI",
                "duetProject": env_project,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.CODE_ASSIST_ENDPOINT}/v1internal:loadCodeAssist", headers=headers, json=load_body)
            
            data = {}
            if resp.status_code != 200:
                # Basic check for VPC-SC (simplified from gemini.ts)
                if "SECURITY_POLICY_VIOLATED" in resp.text:
                    data = {"currentTier": {"id": "standard-tier"}}
                else:
                    raise Exception(f"loadCodeAssist failed: {resp.status_code} {resp.text}")
            else:
                data = resp.json()

            if "currentTier" in data:
                project = data.get("cloudaicompanionProject")
                if isinstance(project, str) and project:
                    return project
                if isinstance(project, dict) and project.get("id"):
                    return project["id"]
                if env_project:
                    return env_project
                raise Exception("This account requires GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_PROJECT_ID to be set.")

            # Onboard if needed
            tier = data.get("allowedTiers", [{}])[0]
            tier_id = tier.get("id", "free-tier")
            
            onboard_body = {
                "tierId": tier_id,
                "metadata": {
                    "ideType": "IDE_UNSPECIFIED",
                    "platform": "PLATFORM_UNSPECIFIED",
                    "pluginType": "GEMINI",
                },
            }
            if tier_id != "free-tier" and env_project:
                onboard_body["cloudaicompanionProject"] = env_project
                onboard_body["metadata"]["duetProject"] = env_project

            onboard_resp = await client.post(f"{self.CODE_ASSIST_ENDPOINT}/v1internal:onboardUser", headers=headers, json=onboard_body)
            if onboard_resp.status_code != 200:
                raise Exception(f"onboardUser failed: {onboard_resp.status_code} {onboard_resp.text}")
            
            lro = onboard_resp.json()
            if not lro.get("done") and lro.get("name"):
                lro = await self._poll_operation(lro["name"], headers)

            proj_id = lro.get("response", {}).get("cloudaicompanionProject", {}).get("id")
            if proj_id:
                return proj_id
            if env_project:
                return env_project

        raise Exception("Could not discover or provision a Google Cloud project. Set GOOGLE_CLOUD_PROJECT.")

    async def _poll_operation(self, op_name: str, headers: dict) -> dict:
        async with httpx.AsyncClient() as client:
            for _ in range(24):
                await asyncio.sleep(5)
                resp = await client.get(f"{self.CODE_ASSIST_ENDPOINT}/v1internal/{op_name}", headers=headers)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                if data.get("done"):
                    return data
        raise Exception("Operation polling timeout")

    def get_next_account(self) -> Optional[GeminiCliAuthRecord]:
        valid_accounts = [acc for acc in self.accounts if acc["status"] == "valid"]
        if not valid_accounts:
            return None
        
        acc = valid_accounts[self.current_index % len(valid_accounts)]
        self.current_index += 1
        return acc

    async def get_valid_account(self, record: GeminiCliAuthRecord) -> GeminiCliAuthRecord:
        """Ensures the record has a valid access token, refreshing if necessary."""
        if int(time.time() * 1000) >= record["expires"]:
            logger.info(f"Refreshing token for {record['email']}")
            return await self.refresh_token(record)
        return record
