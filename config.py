# config.py
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://user:1111@localhost:5432/management')