from datetime import datetime
from queue import Empty

from pylon.core.tools import log

from ...shared.db_manager import Base
from ...shared.models.abstract_base import AbstractBaseMixin
from ...shared.utils.rpc import RpcMixin

from sqlalchemy import Integer, Column, String, Boolean, UniqueConstraint, Index, ARRAY, JSON, DateTime
from croniter import croniter


class Schedule(AbstractBaseMixin, RpcMixin, Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=False, nullable=False)
    cron = Column(String(64), unique=False, nullable=False)
    active = Column(Boolean, default=True)
    rpc_func = Column(String(64), unique=False, nullable=False)
    rpc_kwargs = Column(JSON, nullable=False, default={})
    last_run = Column(DateTime, nullable=True)

    @property
    def time_to_run(self) -> bool:
        if not self.last_run:
            return True
        return croniter(self.cron, self.last_run, datetime).get_next() <= datetime.now()

    def run(self):
        log.info(f'Trying to run schedule {self.id}')
        log.info(f'is it time_to_run? {self.time_to_run}')
        if self.time_to_run:
            self.last_run = datetime.now()
            self.commit()
            try:
                self.rpc.call_function_with_timeout(
                    func=self.rpc_func,
                    timeout=5,
                    **self.rpc_kwargs
                )
            except Empty:
                log.critical(f'Schedule func failed to run {self.rpc_func}')

