from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=500
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty")

        return value