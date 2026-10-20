from pydantic import BaseModel, Field, field_validator


class RegulatoryRequirement(BaseModel):
    legal_reference: str = Field(min_length=3)
    requirement_text: str = Field(min_length=10)
    source_document: str = Field(min_length=5)
    source_page: int = Field(ge=1)

    parent_obligation: str = Field(min_length=10)

    @field_validator("requirement_text")
    @classmethod
    def validate_requirement_text(cls, value):
        if not value.strip():
            raise ValueError("Requirement text cannot be empty")
        return value.strip()
    