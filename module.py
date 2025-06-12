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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from traceback import format_exc

from pylon.core.tools import log, web  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from pylon.core.tools import db_support  # pylint: disable=E0611,E0401

from .init_db import init_db

from tools import VaultClient
from tools import config as c
from queue import Empty

from .models.schedule import Schedule


class Module(module.ModuleModel):
    """ Task module """

    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor
        self.scheduler = None

    def init(self):
        """ Init module """
        log.info("Initializing module")
        if c.DATABASE_VENDOR != 'postgres':
            raise Exception(f'Scheduling does not support db vendor: {c.DATABASE_VENDOR}. Supported are: ["postgres"]')

        init_db()

        self.descriptor.init_blueprint()

        self.descriptor.init_rpcs()

        self.descriptor.init_slots()

        # Configure the PostgreSQL connection
        db_url = f'postgresql://{c.POSTGRES_USER}:{c.POSTGRES_PASSWORD}@{c.POSTGRES_HOST}:{c.POSTGRES_PORT}/{c.POSTGRES_DB}'
        jobstores = {
            'default': SQLAlchemyJobStore(url=db_url)
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores)

        if c.ARBITER_RUNTIME == "rabbitmq":
            self.create_rabbit_schedule()

        self.create_retention_schedules()

        self.descriptor.init_api()
        self.init_ui()

        self.scheduler.start()

    def ready(self):
        """ Ready callback """
        log.info("Scheduler started")

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing")
        self.scheduler.shutdown()

    def execute_schedules(self, debug=False):
        from .models.schedule import Schedule
        from tools import db
        try:
            db_support.create_local_session()
            if debug:
                log.info('Running schedules...')
            with db.with_project_schema_session(None) as session:
                schedules = session.query(Schedule).filter(Schedule.active == True).all()
                for sc in schedules:
                    try:
                        sc.run(debug)
                        session.commit()
                    except Exception as e:
                        log.critical(e)
        except:  # pylint: disable=W0702
            log.exception("Error in scheduler loop")
        finally:
            db_support.close_local_session()

    def create_rabbit_schedule(self) -> dict:
        self.scheduler.add_job(
            self.execute_schedules,
            trigger=CronTrigger.from_crontab('*/10 * * * *'),
            kwargs={'debug': self.descriptor.config['debug']}
        )
        return {'name': 'rabbit_queue_schedule'}

    def init_ui(self):
        from tools import theme

        prefix = 'configuration_scheduling_'

        theme.register_subsection(
            'configuration', 'schedules',
            'Schedules',
            title="Schedules",
            kind="slot",
            permissions={
                "permissions": ["configuration.scheduling"],
                "recommended_roles": {
                    "administration": {"admin": True, "viewer": True, "editor": True},
                    "default": {"admin": True, "viewer": True, "editor": True},
                }},
            prefix=prefix,
        )

        theme.register_mode_subsection(
            "administration", "configuration",
            "schedules", "Schedules",
            title="Integrations",
            kind="slot",
            permissions={
                "permissions": ["configuration.scheduling"],
                "recommended_roles": {
                    "administration": {"admin": True, "viewer": True, "editor": True},
                    "default": {"admin": True, "viewer": True, "editor": True},
                }},
            prefix=prefix,
        )