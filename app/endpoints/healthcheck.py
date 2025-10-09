from fastapi import APIRouter

from app.models.dto.healthcheck import HealthcheckResponse

router: APIRouter = APIRouter(prefix="/health")


@router.get(path="/liveness")
async def handle_liveness() -> HealthcheckResponse:
    return HealthcheckResponse.alive(service="bot")


@router.get(path="/readiness")
async def handle_readiness() -> HealthcheckResponse:
    return HealthcheckResponse.ready(service="bot", ready=True)
