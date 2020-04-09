#!/user/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import multiprocessing
import threading
import _thread as thread
import time
import gc
from random import randint
import json
import math
import importlib

from plup.indicators.Indicator import Indicator
from plup.Helpers.Vacuum import vacuum
from plup.Helpers.LogEvents import LogEvents
import plup.Helpers.config as config
from UP.celery import app
from celery import task

from plup.models import Modules

running_processes_limiter = 0
lock = threading.Lock()


class EvaluateScenario:
    """
    Urban Performance scenario evaluation
    Attributes:
        user: user id.
        scenarios: List of scenarios to be evaluated.
        indicators: List of indicators to be evaluated.
    """

    def __init__(self, user, scenarios, indicators):
        LogEvents(
                "Start scenario", 
                "Starting all scenarios proccesing", 
                -1,
                1
            )
        
        self.user = user
        self.indicator = Indicator(self.user)
        if scenarios != "":
            self.scenarios = [int(scenario.strip())
                              for scenario in scenarios.split('_')]
        self.base_scenario = self.__get_base_scenario(self.scenarios[0])
        if self.base_scenario in self.scenarios:
            if len(self.scenarios)>1:
                self.scenarios.append(self.scenarios.pop(self.scenarios.index(self.scenarios.index(self.base_scenario))))
        if indicators != "":
            self.indicators = indicators.split('_')
        indicator_param=[]
        for indicator_set in self.indicators:
            indicator_param.append(indicator_set.strip())
        
        order = Modules.objects.filter(module__in=indicator_param).values("module").order_by('order')
        
        self.indicators=[]
        for module_in in order:
            self.indicators.append(module_in["module"])
        self.copiados = dict(
            buffers=True,
            policies=True,
            amenities=[],
            transit=[],
            cycle=[],
            footprint=[],
            roads=[]
        )
        
    """
    run_scenarios method executes all the modules that the user's role
    has access to.
    """

    def run_scenarios(self):
        try:
            LogEvents(
                "Start scenario", 
                "Starting all scenarios proccesing", 
                self.base_scenario, 
                self.user
            )
            last = 0
            # Evaluate the scenario(s)
            for scenario in self.scenarios:
                last = scenario
                LogEvents(
                    "Start scenario", 
                    "The modules to be use are: " +str(",".join(self.indicators)),
                    scenario, 
                    self.user
                )

                ##########################################
                for module in self.indicators:
                    module_r = "plup.indicators."+module+"."+module
                    
                    try:
                        plugin=importlib.import_module(module_r,".")
                        module=plugin.Module(self.user,scenario,dict(base_scenario=self.base_scenario))
                        module.run()
                    except Exception as e:
                        print("E", e)
                LogEvents(
                    "Finish scenario",
                    "The scenario have been processed",
                    scenario,
                    self.user
                )
                db = config.get_db()
                vacuum(self.indicator.get_uri(),"mmu")
                db.close()
            db = config.get_db()
            vacuum(self.indicator.get_uri(),True)
            db.close()
            LogEvents(
                "All scenarios Finished", 
                "All scenarios have been processed", 
                last,
                self.user
            )
        except Exception as e:
            LogEvents(
                "Unknown error", 
                str(e), 
                self.base_scenario, 
                self.user
            )
    """
    __get_base_scenario method finds the base scenario that were created
    for the provided city and country
    """

    def __get_base_scenario(self,scenario):
        scenario_id = -1
        try:
            db = config.get_db()
            
            try:
                query = """
                    select scenario_id 
                    from scenario 
                    ,(
                        select location 
                        from scenario
                        inner join footprint
                        using (scenario_id)
                        where footprint.name='study_area'
                        and scenario_id={scenario}
                    ) pb
                    where is_base=1 and st_equals(pb.location, location)
                """.format(scenario=scenario)
                
                db.execute(query)
                scenarios = db.fetchall()
                scenario_id = scenarios[0][0]
                db.close()
                return scenario_id
            except Exception as e:
                LogEvents(
                    "An error happend while getting the base scenario",
                    str(e),
                    -1,
                    sys.argv[1]
                )
                db.close()
        except Exception as e:
            LogEvents(
                "Unknown error",
                str(e),
                -1,
                sys.argv[1]
            )
        
        return scenario_id
    """
    __get_all_scenarios method finds all the scenarios that were created
    ofr the provided city and country
    """

    def get_base_scenario(self):
        return self.__get_base_scenario()


@app.task
def run(user,scenario,indicators):
    import os
    
    import time
    my_pid = os.getpid()
    
    print("received: ",user,scenario,indicators)
    try:
        # evaluate the scenarios
            LogEvents(
                "All scenarios are ready to be evaluated",
                "This may take a while",
                -1,
                user
            )
            evaluate = EvaluateScenario(
                user,scenario,indicators
                )
            LogEvents(
                "All scenarios are ready to be evaluated",
                "This may take a while",
                -1,
                user
            )
            evaluate.run_scenarios()
            LogEvents(
                "All scenarios have been evaluated",
                "You must provide arguments",
                -1,
                user
            )
    except Exception as e:
        LogEvents(
                "There was an error during scenario evaluation",
                str(e),
                -1,
                user
            )

if __name__ == '__main__':
    # sys.argv[1] user_id
    # sys.argv[2] list of scenarios,
    # sys.argv[3] list of modules
    if len(sys.argv) < 4:
        print("Wrong arguments\nExample")
        print("\tEvaluateScenario user_id[1] scenarios[1_2_3_...] indicators[GeneralCalculus_AmenityProximity]")
    elif len(sys.argv) <= 2:
        LogEvents(
            "Evaluate scenarios",
            "You must provide arguments",
            -1,
            sys.argv[1]
        )
    elif len(sys.argv) == 4:
        print("Running")
        run(sys.argv[1], sys.argv[2], sys.argv[3])
