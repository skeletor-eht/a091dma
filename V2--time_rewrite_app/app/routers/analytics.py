from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db import SessionLocal
from ..deps import get_current_user
from ..models import Client, TimeEntry, RewriteRecord, AuditEvent

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return comprehensive dashboard metrics for billing analytics.
    """
    # Total metrics
    total_rewrites = db.query(RewriteRecord).count()
    total_hours = db.query(func.sum(TimeEntry.hours)).scalar() or 0.0
    total_clients = db.query(Client).count()

    # Calculate 30-day trends
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)

    recent_rewrites = db.query(RewriteRecord).filter(
        RewriteRecord.created_at >= thirty_days_ago
    ).count()

    prev_rewrites = db.query(RewriteRecord).filter(
        RewriteRecord.created_at >= sixty_days_ago,
        RewriteRecord.created_at < thirty_days_ago
    ).count()

    recent_hours = db.query(func.sum(TimeEntry.hours)).filter(
        TimeEntry.created_at >= thirty_days_ago
    ).scalar() or 0.0

    prev_hours = db.query(func.sum(TimeEntry.hours)).filter(
        TimeEntry.created_at >= sixty_days_ago,
        TimeEntry.created_at < thirty_days_ago
    ).scalar() or 0.0

    # Calculate percentage changes
    rewrites_change = 0.0
    if prev_rewrites > 0:
        rewrites_change = ((recent_rewrites - prev_rewrites) / prev_rewrites) * 100

    hours_change = 0.0
    if prev_hours > 0:
        hours_change = ((recent_hours - prev_hours) / prev_hours) * 100

    # Client activity breakdown
    client_stats = []
    clients = db.query(Client).all()

    for client in clients:
        entry_count = db.query(TimeEntry).filter(
            TimeEntry.client_id == client.id
        ).count()

        client_hours = db.query(func.sum(TimeEntry.hours)).filter(
            TimeEntry.client_id == client.id
        ).scalar() or 0.0

        if entry_count > 0:
            client_stats.append({
                "id": client.id,
                "name": client.name,
                "entries": entry_count,
                "hours": float(client_hours),
            })

    # Sort by hours descending
    client_stats = sorted(client_stats, key=lambda x: x["hours"], reverse=True)

    # Monthly trend data (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)

        month_rewrites = db.query(RewriteRecord).filter(
            RewriteRecord.created_at >= month_start,
            RewriteRecord.created_at < month_end
        ).count()

        month_hours = db.query(func.sum(TimeEntry.hours)).filter(
            TimeEntry.created_at >= month_start,
            TimeEntry.created_at < month_end
        ).scalar() or 0.0

        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "rewrites": month_rewrites,
            "hours": float(month_hours),
        })

    # Average hours per entry
    avg_hours = total_hours / total_rewrites if total_rewrites > 0 else 0.0

    return {
        "overview": {
            "total_rewrites": total_rewrites,
            "total_hours": float(total_hours),
            "total_clients": total_clients,
            "avg_hours_per_entry": float(avg_hours),
            "rewrites_change_30d": float(rewrites_change),
            "hours_change_30d": float(hours_change),
        },
        "client_breakdown": client_stats[:10],  # Top 10 clients
        "monthly_trend": monthly_data,
        "recent_activity": {
            "last_30_days": {
                "rewrites": recent_rewrites,
                "hours": float(recent_hours),
            },
            "previous_30_days": {
                "rewrites": prev_rewrites,
                "hours": float(prev_hours),
            }
        }
    }
