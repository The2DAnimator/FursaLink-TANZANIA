"""Google Maps geocoding & nearby search (mock fallback when unconfigured)."""
import requests

from apps.integrations.base import BaseService


class MapsService(BaseService):
    name = "google_maps"
    required_keys = ("GOOGLE_MAPS_API_KEY",)

    def geocode(self, address: str):
        if not self.is_live:
            # Deterministic pseudo-coordinates around Dar es Salaam for demos.
            return self._mock("geocode", address=address, lat=-6.7924, lng=39.2083)
        try:  # pragma: no cover - network dependent
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": address, "key": self.config["GOOGLE_MAPS_API_KEY"]},
                timeout=15,
            )
            data = resp.json()
            if data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                return {"status": "ok", "lat": loc["lat"], "lng": loc["lng"]}
            return {"status": "not_found"}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "detail": str(exc)}
