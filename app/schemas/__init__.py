from fastapi_camelcase import CamelModel


class PaginationModel(CamelModel):
    page: int = 1
    size: int = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size
