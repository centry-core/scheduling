from .main_pd import BaseScheduleModel


class UiPerformanceScheduleModel(BaseScheduleModel):
    _rpc_func = 'ui_performance_run_scheduled_test'
