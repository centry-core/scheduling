from typing import List

from ..models.schedule import Schedule

from pylon.core.tools import web


class RPC:
    @web.rpc('scheduling_delete_schedules')
    def delete_schedules(self, delete_ids: List[int]) -> List[int]:
        Schedule.query.filter(Schedule.id.in_(delete_ids)).delete()
        Schedule.commit()
        return delete_ids

    @web.rpc('get_schedules')
    def get_schedules(self) -> List[int]:
        schedules = Schedule.query.all()
        return schedules
