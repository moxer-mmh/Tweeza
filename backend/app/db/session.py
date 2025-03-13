# backend/app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import platform
from .models import Base

Base = Base


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        system = platform.system()
        if system == "Windows":
            appdata_path = os.path.join(os.getenv("APPDATA"), "Tweeza")
        else:
            appdata_path = os.path.expanduser("~/.config/Tweeza")

        if not os.path.exists(appdata_path):
            os.makedirs(appdata_path)

        self.db_path = os.path.join(appdata_path, "Tweeza.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)

        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close_session(self):
        self.Session.remove()


def get_db() -> Generator:
    db_instance = DatabaseConnection()
    session = db_instance.get_session()
    try:
        yield session
    finally:
        db_instance.close_session()
