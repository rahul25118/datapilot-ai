import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User
from app.models.data import Dataset
from app.api.deps import get_current_user
from app.tasks.worker import process_dataset_async

router = APIRouter()
STORAGE_DIR = "/tmp/datapilot_storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_business_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_extensions = [".csv", ".xlsx", ".xls"]
    file_ext = os.path.splitext(file.filename)[-1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid data transmission structure format.")

    import uuid
    dataset_id = uuid.uuid4()
    target_filename = f"{dataset_id}{file_ext}"
    saved_path = os.path.join(STORAGE_DIR, target_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_dataset = Dataset(
        id=dataset_id,
        name=file.filename,
        storage_path=saved_path,
        organization_id=current_user.organization_id
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)

    process_dataset_async.delay(str(new_dataset.id))

    return {
        "dataset_id": new_dataset.id,
        "name": new_dataset.name,
        "status": "queued_for_profiling_matrix"
    }

@router.get("/{dataset_id}/profile")
async def get_dataset_profiling_results(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, 
        Dataset.organization_id == current_user.organization_id
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset target signature resource location missing.")
        
    return {
        "id": dataset.id,
        "name": dataset.name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "schema": dataset.schema_metadata,
        "profiling_summary": dataset.profiling_summary
    }
