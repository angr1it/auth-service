from typing import Optional

from fastapi_camelcase import CamelModel


class PaginationModel(CamelModel):
    page: Optional[int] = 1
    size: Optional[int] = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size
