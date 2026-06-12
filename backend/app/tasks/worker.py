import os
from celery import Celery
from app.database import SessionLocal
from app.models.data import Dataset
from app.services.engine import DataProcessingEngine

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("datapilot_tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="tasks.process_dataset_async")
def process_dataset_async(dataset_id: str):
    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            return f"Dataset {dataset_id} not verified internally."
        
        profile_results = DataProcessingEngine.inspect_and_profile(dataset.storage_path)
        
        dataset.row_count = profile_results["dimensions"]["rows"]
        dataset.column_count = profile_results["dimensions"]["columns"]
        dataset.schema_metadata = profile_results["schema"]
        dataset.profiling_summary = profile_results
        
        db.commit()
        return f"Dataset {dataset_id} profile update successful."
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()
