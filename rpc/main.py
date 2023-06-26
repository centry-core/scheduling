from typing import List, Union

from pydantic import parse_obj_as
from ..models.schedule import Schedule
from ..models.main_pd import ScheduleModelPD

from pylon.core.tools import web, log


class RPC:
    @web.rpc('scheduling_delete_schedules')
    def delete_schedules(self, delete_ids: List[int]) -> List[int]:
        Schedule.query.filter(Schedule.id.in_(delete_ids)).delete()
        Schedule.commit()
        return delete_ids

    @web.rpc('get_schedules')
    def get_schedules(self) -> List[Schedule]:
        schedules = Schedule.query.all()
        return schedules

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
        pd = ScheduleModelPD.parse_obj(schedule_data)
        bd_schedule = Schedule.query.filter(
            Schedule.name == pd.name
        ).first()
        if bd_schedule:
            pd = ScheduleModelPD.from_orm(bd_schedule)
            log.info('Schedule already exists: name=%s id=%s', pd.name, pd.id)
        else:
            pd = self.create_schedule(pd)
            log.info('Schedule created: name=%s id=%s', pd.name, pd.id)
        return pd
