from datetime import datetime
from queue import Empty

from pylon.core.tools import log

from sqlalchemy import Integer, Column, String, Boolean, JSON, DateTime
from croniter import croniter

from tools import db, db_tools, rpc_tools


class Schedule(db_tools.AbstractBaseMixin, rpc_tools.RpcMixin, db.Base):
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
        log.info('')
        log.info(f'Trying to run schedule {self.id}')
        log.info(f'Is it time_to_run? {self.time_to_run}')
        if self.time_to_run:
            log.info('Running now: Schedule(id=%s, name=%s)', self.id, self.name)
            try:
                self.rpc.call_function_with_timeout(
                    func=self.rpc_func,
                    timeout=5,
                    **self.rpc_kwargs
                )
                self.last_run = datetime.now()
                self.commit()
            except Empty:
                log.critical(f'Schedule func failed to run {self.rpc_func}')

        if self.last_run:
            log.info(
                'Next run in: [%s]',
                croniter(self.cron, self.last_run, datetime).get_next() - datetime.now()
            )
        log.info('')
