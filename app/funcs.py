from sqlalchemy.orm import Session

from model import models, schemas

def get_count(db: Session):
    obj = db.query(models.data_set).order_by(models.data_set.sr.desc()).first()
    #temp = db.query(models.data_set).first()
    print(obj.sr)
    return obj.sr

def get_messages(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.data_set).offset(skip).limit(limit).all()

def create_message(db:Session, data_mess: schemas.data_set):
    db_message = models.data_set(sr=data_mess.sr, message=data_mess.message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    print(db_message)
    return db_message
