from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from influencer_agent.app.db.session import SessionLocal
from influencer_agent.app.services.analytics_service import AnalyticsService
from influencer_agent.app.tasks.scheduler_tasks import weekly_planning_task
from influencer_agent.worker.celery_app import celery_app 

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/report")
async def get_weekly_report(db: Session = Depends(get_db)):
    """
    Generates a full AI-powered performance report for the week.
    """
    service = AnalyticsService(db)
    report = await service.generate_weekly_report()
    return report

@router.post("/generate-calendar/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def trigger_weekly_planner(user_id: int):
    """
    Feature 2: Manually triggers the AI to generate next week's content calendar.
    (Simulates the Monday morning cron job).
    """
    # 1. IMMEDIATE CONNECTION ATTEMPT (WINDOWS FIX - Bypassing connection error)
    try:
        # This forces the API to connect to Redis/Memurai before sending the task, preventing 10061 error.
        with celery_app.connection_for_write() as conn:
            conn.connect()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Broker Connection Error (Redis): The server cannot send tasks to the worker. Is Memurai/Redis running? Error: {e}"
        )

    # 2. SEND TASK
    weekly_planning_task.delay(user_id)
    
    return {
        "status": "Planning started", 
        "message": f"Weekly calendar generation task queued for user {user_id}. Check DB for DRAFTs shortly."
    }
