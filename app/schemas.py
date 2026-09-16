from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    source: str = Field(..., min_length=1)
    destination: str | None = None


class OrganizeRequest(BaseModel):
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    dry_run: bool = True


class VerifyRequest(BaseModel):
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)


class PlanRequest(BaseModel):
    source: str = Field(..., min_length=1)


class ExecuteRequest(BaseModel):
    source: str = Field(..., min_length=1)
    dry_run: bool = True


class DashboardState(BaseModel):
    total_media: int = 0
    planned: int = 0
    review_required: int = 0
    conflicts: int = 0
    copied: int = 0
    verified: int = 0
    duplicates: int = 0
    failed: int = 0
    skipped: int = 0


class HealthResponse(BaseModel):
    status: str
    app: str
