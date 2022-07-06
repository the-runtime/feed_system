from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base



class data_set(Base):
    __tablename__ ="data_set"
    sr = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    #user = Column(String)



