from .main_pd import BaseScheduleModel


class PerformanceScheduleModel(BaseScheduleModel):
    _rpc_func = 'performance_run_scheduled_test'
