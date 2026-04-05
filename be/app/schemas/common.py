from pydantic import BaseModel, ConfigDict


class APIMessage(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
