from fastapi import APIRouter

from fieldwork.api.v1.endpoints import triage

router = APIRouter()

router.include_router(triage.router, tags=["Triage"])