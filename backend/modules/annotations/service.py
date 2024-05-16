from uuid import UUID, uuid4

from db.engine import db
from modules.annotations.models import AnnotationTaskModel, AnnotatorModel
from modules.annotations.schemas import AnnotationTask, AnnotationTaskCreate, Annotator, AnnotatorCreate
from typing import Union


def get_annotator_by_number(annotator_number: int) -> Union[Annotator, None]:
    annotator_model = db.session.query(AnnotatorModel).filter(AnnotatorModel.annotator_number == annotator_number).first()
    if annotator_model is None:
        return None
    return Annotator.from_orm(annotator_model)

def get_annotator_by_password(password: str) -> Union[Annotator, None]:
    annotator_model = db.session.query(AnnotatorModel).filter(AnnotatorModel.password == password).first()
    if annotator_model is None:
        return None
    return Annotator.from_orm(annotator_model)


def get_all_annotators() -> list[Annotator]:
    annotator_models = db.session.query(AnnotatorModel).all()
    return [Annotator.from_orm(annotator_model) for annotator_model in annotator_models]


def create_annotator(annotator: AnnotatorCreate) -> Annotator:
    annotator_obj = AnnotatorModel(**annotator.dict(), id=uuid4())
    db.session.add(annotator_obj)
    db.session.commit()
    db.session.refresh(annotator_obj)
    return Annotator.from_orm(annotator_obj)


def crete_annotation_task(annotation_task: AnnotationTaskCreate) -> AnnotationTask:
    annotation_task_obj = AnnotationTaskModel(**annotation_task.dict(), id=uuid4())
    db.session.add(annotation_task_obj)
    db.session.commit()
    db.session.refresh(annotation_task_obj)
    return AnnotationTask.from_orm(annotation_task_obj)


def set_annotation_task_finished(annotation_task_id: UUID) -> None:
    annotation_task_obj = db.session.query(AnnotationTaskModel).get(annotation_task_id)
    annotation_task_obj.finished = True
    db.session.commit()


def update_annotation_task_data(annotation_task_id: UUID, data: dict) -> None:
    annotation_task_obj = db.session.query(AnnotationTaskModel).get(annotation_task_id)
    annotation_task_obj.data = data
    db.session.commit()

