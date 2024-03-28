from langchain_core.pydantic_v1 import BaseModel, Field
from enum import Enum


class LawText(BaseModel):
    text: str = Field(default="", description="the text of the law")


class RequirementsForCompliance(BaseModel):
    excerpts: list[LawText] = Field(default=list(),
                                    description="excerpts from the document that contains information about the requirements for compliance with the law")


class Penalties(BaseModel):
    excerpts: list[LawText] = Field(default=list(),
                                    description="excerpts from the document that contains information about the penalties for non-compliance")


class RequirementsAndPenaltiesData(BaseModel):
    requirements_for_compliance: RequirementsForCompliance = Field(default=RequirementsForCompliance(),
                                                                   description="requirements for compliance with the law")
    penalties: Penalties = Field(default=Penalties(), description="penalties for non-compliance with the law")


class RequirementsAndPenalties(BaseModel):
    data: RequirementsAndPenaltiesData = Field(default=RequirementsAndPenaltiesData(),
                                               description="requirements for compliance with the law and penalties for non-compliance with the law")


class RegulationKeyParameterData(BaseModel):
    key_parameter: str = Field(default="", description="the key parameter name")
    excerpts: list[LawText] = Field(default=list(),
                                    description="excerpts from the document that supports the applicability of the key parameter")


class RegulationKeyParameterDataList(BaseModel):
    data: list[RegulationKeyParameterData] = Field(default=list(),
                                                   description="list of key parameters and their relevant excerpts from the document that supports the applicability of the key parameter")


class EvaluationAnswer(Enum):
    YES = "yes"
    NO = "no"
    UNCLEAR = "unclear"


class KeyParameterEvaluation(BaseModel):
    relevant_excerpts: list[LawText] = Field(default=list(),
                                             description="relevant excerpts from the document that supports the applicability of the key parameter")
    reasoning: str = Field(default="", description="reasoning to arrive at the answer")
    answer: EvaluationAnswer = Field(default="", description="the answer to the question")
