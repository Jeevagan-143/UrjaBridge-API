import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

PORTAL_BASE_URL = "https://urja-ops.flockenergy.tech"


class PortalClient:
    def __init__(self):
        self.client = httpx.Client(
            base_url=PORTAL_BASE_URL,
            timeout=20,
            follow_redirects=True,
        )

        cookie = os.getenv("PORTAL_SESSION_COOKIE", "").strip()
        if cookie:
            self.client.headers["Cookie"] = cookie

    def _get(self, path: str):
        response = self.client.get(path)

        response.raise_for_status()
        return response.json()  
        
    def get_meter_geo(self, meter_id: str):
        return self._get(f"/portal/meters/{meter_id}/geo")

    def get_meter_energy(self, meter_id: str):
        return self._get(f"/portal/meters/{meter_id}/energy")

    def close(self):
        self.client.close()
