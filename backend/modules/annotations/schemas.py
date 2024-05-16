from uuid import UUID

from pydantic import BaseModel


class AnnotationTaskBase(BaseModel):
    annotator_number: int
    task_number: int
    data: dict
    finished: bool

    class Config:
        from_attributes = True


class AnnotationTaskCreate(AnnotationTaskBase):
    pass


class AnnotationTask(AnnotationTaskBase):
    id: UUID


class AnnotatorBase(BaseModel):
    annotator_number: int
    password: str

    class Config:
        from_attributes = True


class AnnotatorCreate(AnnotatorBase):
    pass


class Annotator(AnnotatorBase):
    id: UUID
    tasks: list[AnnotationTask]
