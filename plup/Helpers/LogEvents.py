# -*- coding: utf-8 -*-
import sys
import os
import gc
import logging

import plup.Helpers.logging_config
import plup.Helpers.config 

from plup.models import execution_progress
from django.db import IntegrityError, transaction

class LogEvents:
    """
    Urban Performance log execution monitoring
    Attributes:
        event: actual process
        value: event raised
        scenario: Scenario under excecution.
    """

    def __init__(self, event, value, scenario, user, type=False):
        self.__logger = logging.getLogger(__name__)
        if type:
            self.__logger.error(dict(scenario=scenario,user=user,event=event,value=value))
        else:
            self.__logger.debug(dict(scenario=scenario,user=user,event=event,value=value))
        if scenario > 0:
            self.__log(event, value, scenario, user)
    
    @transaction.atomic
    def __log(self, event, value, scenario, user):
        try:
            p = execution_progress(event=event, value=value, scenario_id=scenario)
            with transaction.atomic():
                p.save()
        except IntegrityError as e:
            self.__logger.error(dict(scenario=scenario,user=user,event=event,value=value, error=e))
