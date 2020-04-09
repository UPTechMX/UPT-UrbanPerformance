from django.urls import path, include
from django.conf.urls.static import static

from .views import scenarioView, resultsView, resultsDetailView, amenitiesView
from .views import scenarioResultsView, scenarioResultsDetailView, transitView
from .views import  riskView,  mmuView
from .views import  jobsView,  footprintView
from .views import  assumptionsView
from .views import risk_infoView, roads_infoView
from .views import  amenities_infoView, transit_infoView
from .views import roadsView,ClassificationView
from .views import mmu_infoView, jobs_infoView
from .views import ModulesView,ScenarioEvalView,ModulesTablesView
from .views import TableColumnsView,ExcecutionProgress,ModulesAllTablesView

urlpatternss = ([
    path('scenario/', scenarioView.as_view()),
    path('scenario/<int:pk>', scenarioView.as_view()),
    path('results/', resultsView.as_view()),
    path('results/<slug:scenarios>', resultsDetailView.as_view()),
    
    path('amenities/', amenitiesView.as_view()),
    path('amenities/<int:pk>', amenitiesView.as_view()),
    path('scenario-results/<slug:scenarios>', scenarioResultsView.as_view()),
    
    path('transit/', transitView.as_view()),
    path('transit/<int:pk>', transitView.as_view()),
    path('risk/', riskView.as_view()),
    path('risk/<int:pk>', riskView.as_view()),
    path('risk_info/', risk_infoView.as_view()),
    
    path('roads/', roadsView.as_view()),
    path('roads/<int:pk>', roadsView.as_view()),
    path('roads_info/', roads_infoView.as_view()),
    
    path('mmu/', mmuView.as_view()),
    path('mmu/<int:pk>', mmuView.as_view()),
    path('mmu_info/', mmu_infoView.as_view()),
    
    path('jobs/', jobsView.as_view()),
    path('jobs/<int:pk>', jobsView.as_view()),
    path('jobs_info/', jobs_infoView.as_view()),
    
    path('footprint/', footprintView.as_view()),
    path('footprint/<int:pk>', footprintView.as_view()),
    path('assumptions/', assumptionsView.as_view()),
    path('assumptions/<int:pk>',  assumptionsView.as_view()),
    path('amenities_info/', amenities_infoView.as_view()),
    
    path('transit_info/', transit_infoView.as_view()),
    
    path('indicator/<slug:module>',  ModulesView.as_view()),
    path('indicator/',  ModulesView.as_view()),
    path('layers/',  ModulesTablesView.as_view()),
    path('layer_columns/',  TableColumnsView.as_view()),
    path('scenario_evaluation/', ScenarioEvalView.as_view()),
    path('scenario_evaluation/<int:scenario>/<int:user>/<int:projection>', ScenarioEvalView.as_view()),
    path('scenario_status/', ExcecutionProgress.as_view()), 
    path('all_layers/', ModulesAllTablesView.as_view()), 

    path('classification/', ClassificationView.as_view()),
    path('classification/<int:pk>',  ClassificationView.as_view()),
    
], 'plup')
