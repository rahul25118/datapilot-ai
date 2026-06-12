from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.auth import User
from app.models.data import Dataset
from app.models.analytics import ChatHistory
from app.api.deps import get_current_user
from app.services.ai import AISemanticAnalyst

router = APIRouter()
analyst_engine = AISemanticAnalyst()

class QueryRequestSchema(BaseModel):
    dataset_id: str
    prompt: str
    language: str = "en"

@router.post("/chat")
async def execute_semantic_data_query(
    payload: QueryRequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == payload.dataset_id,
        Dataset.organization_id == current_user.organization_id
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Target processing context reference database mismatch.")

    ai_response = analyst_engine.analyze_and_respond(
        user_query=payload.prompt,
        dataset_path=dataset.storage_path,
        profiling_summary=dataset.profiling_summary or {},
        target_lang=payload.language
    )

    chat_log = ChatHistory(
        dataset_id=dataset.id,
        user_id=current_user.id,
        prompt=payload.prompt,
        response_text=ai_response.get("response_text", ""),
        visualization_config=ai_response.get("visualization_config", {})
    )
    db.add(chat_log)
    db.commit()

    return ai_response


