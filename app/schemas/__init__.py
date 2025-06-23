from fastapi_camelcase import CamelModel
from pydantic import Field

class PaginationModel(CamelModel):
    page: int = Field(default=1, example=1)
    size: int = Field(default=10, example=10)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size
