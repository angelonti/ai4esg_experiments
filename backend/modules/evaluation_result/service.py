from uuid import UUID, uuid4

from db.engine import db
from modules.document.models import DocumentModel
from modules.embedding.models import EmbeddingModel
from modules.evaluation_result.models import EvaluationResultModel
from modules.evaluation_result.schemas import EvaluationResult, EvaluationResultCreate
from typing import Union


def get(id: UUID) -> Union[EvaluationResult, None]:
    evaluation_result_model = db.session.query(EvaluationResultModel).get(id)
    if evaluation_result_model is None:
        return None
    return EvaluationResult.from_orm(evaluation_result_model)


def get_all() -> list[EvaluationResult]:
    evaluation_result_models = db.session.query(EvaluationResultModel).all()
    return [EvaluationResult.from_orm(evaluation_result_model) for evaluation_result_model in evaluation_result_models]


def create(evaluation_result: EvaluationResultCreate) -> EvaluationResult:
    evaluation_result_obj = EvaluationResultModel(**evaluation_result.dict(), id=uuid4())
    db.session.add(evaluation_result_obj)
    db.session.commit()
    db.session.refresh(evaluation_result_obj)
    return EvaluationResult.from_orm(evaluation_result_obj)


def delete(evaluation_result_id: str | None = None) -> None:
    if not evaluation_result_id:
        db.session.query(EvaluationResultModel).delete()
    else:
        db.session.query(EvaluationResultModel).filter(
            EvaluationResultModel.id == evaluation_result_id
        ).delete()
    db.session.commit()