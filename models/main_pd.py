from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, constr
from pydantic.class_validators import validator
from pydantic.fields import ModelField

from croniter import croniter

from ...shared.models.pd.test_parameters import TestParameter  # todo: try to find workaround for this import
from .schedule import Schedule


from abc import ABC, abstractmethod


class BaseScheduleModel(BaseModel, ABC):
    id: Optional[int] = None
    name: constr(min_length=1)
    cron: str
    active: bool = True

    @validator('cron')
    def validate_cron(cls, value: str):
        assert croniter.is_valid(value), 'Cron expression is invalid'
        return value

    @abstractmethod
    def save(self) -> int:
        raise NotImplementedError


class ScheduleModelPD(BaseScheduleModel):
    rpc_func: str
    rpc_kwargs: dict = {}
    last_run: Optional[datetime] = None

    class Config:
        orm_mode = True

    def save(self) -> int:
        if self.id:
            db_obj = Schedule.query.filter(Schedule.id == self.id)
            db_obj.update(self.dict(exclude_unset=True, exclude={'id', 'last_run'}))
            Schedule.commit()
        else:
            db_obj = Schedule(**self.dict(exclude_unset=True, exclude={'id', 'last_run'}))
            db_obj.insert()
            self.id = db_obj.id
        return self.id


class BaseTestScheduleModel(BaseScheduleModel, ABC):
    test_id: Optional[int] = None
    test_params: List[TestParameter]

    @staticmethod
    @abstractmethod
    def _rpc_func():
        raise NotImplementedError

    @property
    def _db_schedule(self):
        return Schedule(
            name=self.name,
            cron=self.cron,
            active=self.active,
            rpc_func=self._rpc_func,
            rpc_kwargs={
                'test_id': self.test_id,
                'test_params': [i.dict() for i in self.test_params],
            }
        )

    def save(self) -> int:
        assert self.test_id, 'Test id is required'
        if self.id:
            db_obj = Schedule.query.filter(Schedule.id == self.id)
            db_obj.update(self._db_schedule.to_json(exclude_fields=('id', 'last_run',)))
            Schedule.commit()
            return self.id
        else:
            db_obj = self._db_schedule
            db_obj.insert()
            return db_obj.id

    @classmethod
    def from_orm(cls, db_obj: Schedule):
        return cls(
            name=db_obj.name,
            cron=db_obj.cron,
            active=db_obj.active,
            test_params=db_obj.rpc_kwargs.get('test_params', []),
            id=db_obj.id,
            test_id=db_obj.rpc_kwargs.get('test_id'),
        )
