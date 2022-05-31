#!/usr/bin/python3
# coding=utf-8

#   Copyright 2021 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" Module """
import time
from functools import partial
from threading import Thread

from pylon.core.tools import log, web  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

# from .components import render_security_test_create
from .init_db import init_db
# from .rpc import security_test_create, security_create_schedule, security_load_from_db_by_ids, delete_schedules


class Module(module.ModuleModel):
    """ Task module """

    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    def init(self):
        """ Init module """
        log.info("Initializing module")

        init_db()

        self.descriptor.init_blueprint()

        self.descriptor.init_rpcs()

        # self.context.slot_manager.register_callback('security_scheduling_test_create', render_security_test_create)
        self.descriptor.init_slots()

        self.thread = Thread(
            target=partial(
                self.execute_schedules,
                self.descriptor.config['task_poll_period']
            )
        )
        self.thread.daemon = True
        self.thread.start()

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing")

    @staticmethod
    def execute_schedules(poll_period: int = 60):
        from .models.schedule import Schedule

        while True:
            time.sleep(poll_period)
            log.info(f'Running schedules... with poll_period {poll_period}')
            for sc in Schedule.query.filter(Schedule.active == True).all():
                try:
                    sc.run()
                except Exception as e:
                    log.critical(e)
