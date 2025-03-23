from pydantic import BaseModel


class PydanticModel:
    def __init__(self, model: type[BaseModel]):
        self.model = model
