
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate, JobResponse

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    job = Job(**job_data.model_dump())

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("/", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    updates = job_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Prevent deletion if applications reference this job
    if job.applications:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a job linked to applications",
        )

    db.delete(job)
    db.commit()