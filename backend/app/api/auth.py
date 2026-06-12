from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_auth_status():
    return {"status": "auth_subsystem_active"}
