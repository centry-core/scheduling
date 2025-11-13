from datetime import datetime
from typing import List, Union

from ..models.schedule import Schedule
from ..models.main_pd import ScheduleModelPD

from pylon.core.tools import web, log

from croniter import croniter

from tools import db


class RPC:
    @web.rpc('scheduling_delete_schedules')
    def delete_schedules(self, delete_ids: List[int]) -> List[int]:
        with db.with_project_schema_session(None) as session:
            session.query(Schedule).where(Schedule.id.in_(delete_ids)).delete()
        return delete_ids

    @web.rpc('get_schedules')
    def get_schedules(self, session=db.session) -> List[Schedule]:
        return session.query(Schedule).all()

    @web.rpc('scheduling_create_schedule', 'create_schedule')
    def create_schedule(self, schedule_data: Union[dict, ScheduleModelPD]) -> ScheduleModelPD:
        if isinstance(schedule_data, dict):
            pd = ScheduleModelPD.parse_obj(schedule_data)
        else:
            pd = schedule_data
        pd.save()
        return pd

    @web.rpc('scheduling_create_if_not_exists', 'create_if_not_exists')
    def create_if_not_exists(self, schedule_data: dict) -> ScheduleModelPD:
        with db.with_project_schema_session(None) as session:
            pd = ScheduleModelPD.parse_obj(schedule_data)
            bd_schedule = session.query(Schedule).where(Schedule.name == pd.name).first()
            if bd_schedule:
                pd = ScheduleModelPD.from_orm(bd_schedule)
                log.info('Schedule already exists: name=%s id=%s', pd.name, pd.id)
            else:
                pd = self.create_schedule(pd)
                log.info('Schedule created: name=%s id=%s', pd.name, pd.id)
            return pd

    @web.rpc()
    def make_active(self, schedule_name, value=True):
        with db.with_project_schema_session(None) as session:
            schedule = session.query(Schedule).where(Schedule.name == schedule_name).first()
            if schedule and schedule.active != value:
                schedule.active = value
                session.commit()

    @web.rpc('scheduling_time_to_run', 'time_to_run')
    def time_to_run(self, cron: str, last_run: datetime | str, utc: bool = True):
        if not last_run:
            return True
        if isinstance(last_run, str):
            if utc:
                last_run = last_run.replace('Z', '+00:00')
            last_run = datetime.fromisoformat(last_run)
        now = datetime.now(last_run.tzinfo) if last_run.tzinfo else datetime.now()
        return croniter(cron, last_run, datetime).get_next() <= now
