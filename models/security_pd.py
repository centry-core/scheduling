from typing import List

from pydantic import BaseModel, AnyUrl

from .main_pd import BaseScheduleModel
from ...shared.models.pd.test_parameters import TestParameter


class SecurityScheduleTestParam(TestParameter):
    _type_mapping_by_name = {'url to scan': List[AnyUrl]}


class SecurityScheduleModel(BaseScheduleModel):
    _rpc_func = 'security_run_scheduled_test'
    test_params: List[SecurityScheduleTestParam]

