import math
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.route import RouteRepository
from app.schemas.ai import DynamicRerouteRequest, ETAPredictRequest, ETAPredictResponse
from app.services.ai_gemini import GeminiAIService


class ETAPredictionService:
    """
    Predictive ETA Calculation & Dynamic Route Adjustment Service.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.route_repo = RouteRepository(session=session)
        self.gemini_service = GeminiAIService()

    async def predict_eta(self, req: ETAPredictRequest) -> ETAPredictResponse:
        """
        Calculates predictive ETA incorporating distance, traffic factors, weather factors, and stop overhead.
        """
        # Calculate Haversine distance
        dist_km = self._haversine(req.pickup_lat, req.pickup_lng, req.delivery_lat, req.delivery_lng)
        if dist_km == 0.0:
            dist_km = 5.2

        # Base travel time at 40 km/h average speed
        base_minutes = (dist_km / 40.0) * 60.0

        # Traffic delay calculation
        traffic_delay = base_minutes * (req.traffic_factor - 1.0)

        # Weather delay calculation
        weather_delays = {
            "CLEAR": 0.0,
            "RAIN": 5.0,
            "SNOW": 15.0,
            "FOG": 8.0
        }
        weather_delay = weather_delays.get(req.weather_condition.upper(), 0.0)

        total_minutes = base_minutes + traffic_delay + weather_delay + req.stop_service_minutes
        eta_time = datetime.now(timezone.utc) + timedelta(minutes=total_minutes)

        return ETAPredictResponse(
            estimated_distance_km=round(dist_km, 2),
            estimated_duration_minutes=round(total_minutes, 1),
            traffic_delay_minutes=round(traffic_delay, 1),
            weather_delay_minutes=round(weather_delay, 1),
            eta_timestamp=eta_time.isoformat()
        )

    async def dynamically_reroute(self, req: DynamicRerouteRequest) -> dict:
        """
        Dynamically adjusts active route stop sequences upon delay alerts or cancellations.
        """
        # pyrefly: ignore [missing-attribute]
        route = await self.route_repo.get_route_with_stops(req.route_id)
        if not route:
            raise ValueError(f"Route {req.route_id} not found.")

        # Re-index remaining stop sequences to bypass delay
        stops = sorted(route.stops, key=lambda s: s.stop_sequence)
        adjusted_stops = []
        for stop in stops:
            if stop.stop_sequence == req.delayed_stop_sequence:
                # Move delayed stop to end of sequence
                stop.stop_sequence = len(stops)
            elif stop.stop_sequence > req.delayed_stop_sequence:
                stop.stop_sequence -= 1
            adjusted_stops.append({
                "stop_id": str(stop.id),
                "delivery_id": str(stop.delivery_id),
                "new_sequence": stop.stop_sequence
            })

        await self.session.commit()

        return {
            "route_id": str(route.id),
            "status": "DYNAMICALLY_REROUTED",
            "reason": req.delay_reason,
            "adjusted_sequence": adjusted_stops,
            "message": f"Route sequence dynamically re-ordered to bypass delay at stop {req.delayed_stop_sequence}."
        }

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
