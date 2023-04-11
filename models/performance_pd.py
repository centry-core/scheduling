from .main_pd import BaseScheduleModel


class PerformanceScheduleModel(BaseScheduleModel):
    _rpc_func = 'backend_performance_run_scheduled_test'
