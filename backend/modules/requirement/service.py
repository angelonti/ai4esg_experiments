from uuid import UUID, uuid4

from db.engine import db
from modules.requirement.models import RequirementModel, RequirementSummaryModel
from modules.requirement.schemas import Requirement, RequirementCreate, RequirementSummary, RequirementSummaryCreate
from typing import Union


def get(id: UUID) -> Union[Requirement, None]:
    requirement_model = db.session.query(RequirementModel).get(id)
    if requirement_model is None:
        return None
    return Requirement.from_orm(requirement_model)


def get_all() -> list[Requirement]:
    requirement_models = db.session.query(RequirementModel).all()
    return [Requirement.from_orm(requirement_model) for requirement_model in requirement_models]


def get_by_document_id(document_id: UUID) -> list[Requirement]:
    requirement_models = db.session.query(RequirementModel).filter(
        RequirementModel.document_id == document_id).all()
    return [Requirement.from_orm(requirement_model) for requirement_model in requirement_models]


def create(requirement: RequirementCreate) -> Requirement:
    requirement_obj = RequirementModel(**requirement.dict(), id=uuid4())
    db.session.add(requirement_obj)
    db.session.commit()
    db.session.refresh(requirement_obj)
    return Requirement.from_orm(requirement_obj)


def delete(requirement_id: str | None = None) -> None:
    if not requirement_id:
        db.session.query(RequirementModel).delete()
    else:
        db.session.query(RequirementModel).filter(
            RequirementModel.id == requirement_id
        ).delete()
    db.session.commit()


def create_summary(requirement_summary: RequirementSummaryCreate) -> RequirementSummary:
    requirement_summary_obj = RequirementSummaryModel(**requirement_summary.dict(), id=uuid4())
    db.session.add(requirement_summary_obj)
    db.session.commit()
    db.session.refresh(requirement_summary_obj)
    return RequirementSummary.from_orm(requirement_summary_obj)


def get_summary_by_document_id(document_id: UUID) -> Union[RequirementSummary, None]:
    requirement_summary_model = db.session.query(RequirementSummaryModel).filter(
        RequirementSummaryModel.document_id == document_id).first()
    if requirement_summary_model is None:
        return None
    return RequirementSummary.from_orm(requirement_summary_model)
