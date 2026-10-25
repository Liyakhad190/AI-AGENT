"""Background scheduler worker to automatically dispatch due reminders & tasks."""
from __future__ import annotations

import asyncio
import datetime
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.database.models.scheduler import ScheduledJob
from app.database.models.call import CallSession
from app.telephony.adapter import get_telephony_provider
from app.telephony.base import CallDirection
from app.agent.orchestrator import Orchestrator
from app.observability.logging import get_logger

logger = get_logger("scheduler")


async def run_scheduler_loop() -> None:
    """Continuously check for scheduled reminder calls and dispatch them when due."""
    logger.info("Background reminder call scheduler loop started.")
    while True:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(ScheduledJob)
                    .where(ScheduledJob.is_active == True)
                    .where(ScheduledJob.run_at <= now)
                )
                res = await session.execute(stmt)
                due_jobs = res.scalars().all()

                for job in due_jobs:
                    try:
                        payload = job.payload or {}
                        to_number = payload.get("to_number", "+1234567890")
                        reminder_text = payload.get("reminder_text", "Scheduled Voice Reminder")
                        logger.info("Dispatching scheduled reminder call", job_id=str(job.id), to_number=to_number)

                        # Create agent task
                        orchestrator = Orchestrator()
                        task = await orchestrator.create_task(
                            user_id=str(job.user_id),
                            goal=f"[Scheduled Call] {reminder_text}",
                        )

                        # Initiate voice call
                        provider = get_telephony_provider()
                        call_result = await provider.initiate_call(
                            to_number=to_number,
                            from_number="+15550192834",
                            webhook_url="http://localhost:8000/api/v1/calls/webhook",
                            status_callback_url="http://localhost:8000/api/v1/calls/webhook",
                            max_duration_seconds=300,
                        )

                        # Save call session
                        call = CallSession(
                            user_id=job.user_id,
                            provider_call_id=call_result.provider_call_id,
                            direction=CallDirection.OUTBOUND.value,
                            from_number=call_result.from_number,
                            to_number=to_number,
                            status=call_result.status.value,
                            provider_status=call_result.status.value,
                            max_duration_seconds=300,
                        )
                        session.add(call)

                        # Update job
                        job.is_active = False
                        job.run_count += 1
                        job.last_run_at = now
                        job.task_id = task.id
                        await session.commit()
                        logger.info("Scheduled reminder dispatched successfully", job_id=str(job.id))
                    except Exception as job_exc:
                        job.failure_count += 1
                        job.last_error = str(job_exc)
                        await session.commit()
                        logger.error("Error executing scheduled reminder", error=str(job_exc), job_id=str(job.id))
        except Exception as exc:
            logger.error("Error in scheduler loop", error=str(exc))

        await asyncio.sleep(10)
