from pydantic import BaseModel

class data_set(BaseModel):
    sr: int
    message: str
    
    #user: str | None = None

    class Config:
        orm_mode = True




