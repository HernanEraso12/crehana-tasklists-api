"""Endpoint de invitaciones a una lista (`/api/v1/lists/{list_id}/invitations`,
docs/04-api.md, E3). Sin lógica de negocio: llama al caso de uso."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.invite_to_list import InviteToList
from app.infrastructure.api.dependencies import get_invite_to_list_use_case
from app.infrastructure.api.schemas import InvitationCreate, InvitationResponse

router = APIRouter(prefix="/api/v1", tags=["invitations"])


@router.post(
    "/lists/{list_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def invite_to_list(
    list_id: UUID,
    payload: InvitationCreate,
    use_case: InviteToList = Depends(get_invite_to_list_use_case),
) -> InvitationResponse:
    use_case.execute(list_id=list_id, email=payload.email)
    return InvitationResponse(list_id=list_id, email=payload.email)
