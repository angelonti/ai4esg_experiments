from uuid import UUID, uuid4

from db.engine import db
from modules.penalty.models import PenaltyModel, PenaltySummaryModel
from modules.penalty.schemas import Penalty, PenaltyCreate, PenaltySummary, PenaltySummaryCreate
from typing import Union


def get(id: UUID) -> Union[Penalty, None]:
    penalty_model = db.session.query(PenaltyModel).get(id)
    if penalty_model is None:
        return None
    return Penalty.from_orm(penalty_model)


def get_all() -> list[Penalty]:
    penalty_models = db.session.query(PenaltyModel).all()
    return [Penalty.from_orm(penalty_model) for penalty_model in penalty_models]


def get_by_document_id(document_id: UUID) -> list[Penalty]:
    penalty_models = db.session.query(PenaltyModel).filter(
        PenaltyModel.document_id == document_id).all()
    return [Penalty.from_orm(penalty_model) for penalty_model in penalty_models]


def create(penalty: PenaltyCreate) -> Penalty:
    penalty_obj = PenaltyModel(**penalty.dict(), id=uuid4())
    db.session.add(penalty_obj)
    db.session.commit()
    db.session.refresh(penalty_obj)
    return Penalty.from_orm(penalty_obj)


def delete(penalty_id: str | None = None) -> None:
    if not penalty_id:
        db.session.query(PenaltyModel).delete()
    else:
        db.session.query(PenaltyModel).filter(
            PenaltyModel.id == penalty_id
        ).delete()
    db.session.commit()


def create_summary(penalty_summary: PenaltySummaryCreate) -> PenaltySummary:
    penalty_summary_obj = PenaltySummaryModel(**penalty_summary.dict(), id=uuid4())
    db.session.add(penalty_summary_obj)
    db.session.commit()
    db.session.refresh(penalty_summary_obj)
    return PenaltySummary.from_orm(penalty_summary_obj)


def get_summary_by_document_id(document_id: UUID) -> Union[PenaltySummary, None]:
    penalty_summary_model = db.session.query(PenaltySummaryModel).filter(
        PenaltySummaryModel.document_id == document_id).first()
    if penalty_summary_model is None:
        return None
    return PenaltySummary.from_orm(penalty_summary_model)
