from typing import Annotated, Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from api_service.config import Settings
from api_service.database import get_session_factory


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_db(settings: SettingsDep) -> Generator[Session, None, None]:
    factory = get_session_factory(settings.database_url)
    db = factory()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]
