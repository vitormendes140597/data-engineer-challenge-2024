from pydantic import BaseModel


class Event(BaseModel):

    region: str
    origin_coord: str
    destination_coord: str
    datetime: str
    datasource: str
