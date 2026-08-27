from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


class AgentHealth(BaseModel):
    agent_id: str = Field(min_length=1)
    status: str = "healthy"
    checked_at: str
    capabilities: list[str]


class HeartbeatRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    running_task_ids: list[str] = Field(default_factory=list)
    capacity: int = Field(ge=0, default=1)


class TaskLease(BaseModel):
    task_id: str
    status: str
    payload_ref: str


app = FastAPI(title="AIOffice PC Agent", version="0.1.0")


@app.get("/health", response_model=AgentHealth)
def health() -> AgentHealth:
    return AgentHealth(
        agent_id="local-pc-agent",
        checked_at=datetime.now(UTC).isoformat(),
        capabilities=["health", "heartbeat", "task_poll"],
    )


@app.post("/heartbeat", response_model=dict[str, Any])
def heartbeat(request: HeartbeatRequest) -> dict[str, Any]:
    return {
        "accepted": True,
        "agentId": request.agent_id,
        "seenAt": datetime.now(UTC).isoformat(),
        "runningTaskIds": request.running_task_ids,
        "capacity": request.capacity,
    }


@app.get("/tasks/next", response_model=list[TaskLease])
def next_tasks() -> list[TaskLease]:
    return []
