from fastapi import Depends, HTTPException, Request
from fastapi_versionizer.versionizer import api_version

from skynet.env import summary_minimum_payload_length

from skynet.utils import get_app_id, get_customer_id, get_router

from ..jobs import create_job, get_job as get_job
from .models import (
    ActionItemsDocumentPayload,
    BaseJob,
    DocumentMetadata,
    DocumentPayload,
    JobId,
    JobType,
    SummaryDocumentPayload,
)

router = get_router()


def get_metadata(request: Request) -> DocumentMetadata:
    return DocumentMetadata(app_id=get_app_id(request), customer_id=get_customer_id(request))


def validate_payload(payload: DocumentPayload) -> None:
    if len(payload.text) < summary_minimum_payload_length:
        raise HTTPException(status_code=422, detail="Payload is too short")


@api_version(1)
@router.post("/action-items", dependencies=[Depends(validate_payload)])
async def get_action_items(payload: ActionItemsDocumentPayload, request: Request) -> JobId:
    """
    Starts a job to extract action items from the given payload.
    """

    return await create_job(job_type=JobType.ACTION_ITEMS, payload=payload, metadata=get_metadata(request))


@api_version(1)
@router.post("/summary", dependencies=[Depends(validate_payload)])
async def get_summary(payload: SummaryDocumentPayload, request: Request) -> JobId:
    """
    Starts a job to summarize the given payload.
    """

    return await create_job(job_type=JobType.SUMMARY, payload=payload, metadata=get_metadata(request))


@api_version(1)
@router.get("/job/{id}")
async def get_job_result(id: str) -> BaseJob | None:
    """
    Returns the job identified by **id**.
    """

    job = await get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return BaseJob(**(job.model_dump() | {"duration": job.computed_duration}))
