from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./pavimentos.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Calculo(Base):
    __tablename__ = "calculos"

    id = Column(Integer, primary_key=True, index=True)
    trafico = Column(Float)
    resistencia = Column(Float)
    espesor = Column(Float)

# crear tabla
Base.metadata.create_all(bind=engine)
