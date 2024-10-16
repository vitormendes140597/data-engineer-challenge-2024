from pydantic import BaseModel


class Square(BaseModel):

    upper_left: str
    upper_right: str
    bottom_left: str
    bottom_right: str
