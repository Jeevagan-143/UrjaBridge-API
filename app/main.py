from fastapi import FastAPI, HTTPException
import httpx

from app.client import PortalClient

app = FastAPI(
    title="UrjaBridge - Meter Operations API",
    description="Read-only API for legacy meter operations",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "project": "UrjaBridge",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


def portal_request(meter_id: str, data_type: str):
    if not meter_id.replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid meter ID")

    client = PortalClient()

    try:
        if data_type == "geo":
            return client.get_meter_geo(meter_id)

        return client.get_meter_energy(meter_id)

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        print(f"Portal HTTP error: {status}")

        if status == 401:
            raise HTTPException(
                status_code=502,
                detail="Portal authentication failed; valid portal access is required.",
            )

        raise HTTPException(
            status_code=502,
            detail=f"Portal returned HTTP {status}",
        )

    except RuntimeError as exc:
        print(f"Portal authentication error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Portal authentication failed.",
        )

    except httpx.RequestError as exc:
        print(f"Portal connection error: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the portal",
        )

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="Portal returned invalid JSON",
        )

    finally:
        client.close()


@app.get("/meters/{meter_id}/geo")
def meter_geo(meter_id: str):
    return portal_request(meter_id, "geo")


@app.get("/meters/{meter_id}/energy")
def meter_energy(meter_id: str):
    return portal_request(meter_id, "energy")
