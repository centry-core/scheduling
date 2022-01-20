from typing import Optional, List

from pydantic import BaseModel, AnyUrl
from pydantic.class_validators import validator
from pydantic.fields import ModelField
from pylon.core.tools import log

from croniter import croniter

from .schedule import Schedule
from ...shared.utils.rpc import RpcMixin


class SecurityScheduleModel(BaseModel):
    _rpc_func = 'security_run_scheduled_test'

    name: str
    cron: str
    test_params: List[RpcMixin().rpc.call.test_param_model_factory()]
    active: bool
    test_id: Optional[int] = None
    id: Optional[int] = None

    @validator('cron')
    def validate_cron(cls, value: list, field: ModelField):
        assert croniter.is_valid(value), 'Cron expression is invalid'
        return value

    @validator('name')
    def validate_empty(cls, value):
        assert bool(value), 'Cannot be empty'
        return value

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
            # db_obj = Schedule.query.get(self.id)
            db_obj = Schedule.query.filter(Schedule.id == self.id)
            db_obj.update(self._db_schedule.to_json(exclude_fields=('id', 'last_run', )))
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









# id = Column(Integer, primary_key=True)
#     # project_id = Column(Integer, nullable=False)
#     name = Column(String(64), unique=False)
#     cron = Column(String(64), unique=False)
#     # test_parameters = Column(ARRAY(JSON), nullable=True)
#     active = Column(Boolean)
#     rpc_func = Column(String(64), unique=False, nullable=False)
#     rpc_kwargs = Column(JSON, nullable=False, default={})
#     last_run = Column(DateTime, nullable=True)