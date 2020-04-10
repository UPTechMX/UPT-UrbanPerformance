# Required to upload files
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.core import serializers
from django.db.models import TextField, Value
from rest_framework import generics
from .serializers import scenarioSerializer, resultsSerializer, amenitiesSerializer
from .serializers import ScenarioResultsSerializer, transitSerializer, riskSerializer
from .serializers import roadsSerializer, mmuSerializer, jobsSerializer, footprintSerializer
from .serializers import assumptionsSerializer, risk_infoSerializer, roads_infoSerializer
from .serializers import amenities_infoSerializer, transit_infoSerializer, mmu_infoSerializer
from .serializers import jobs_infoSerializer, TransitInfoSerializer, TransitSerializer,ClassificationSerializer
# require to upload files
from .serializers import ModuleSerializer, ModuleListSerializer, ModulesTablesListSerializer
from plup.models import scenario, Results, Amenities, transit, risk, roads, mmu, jobs
from plup.models import footprint, assumptions, risk_info, roads_info, Amenities_info
from plup.models import transit_info, mmu_info, jobs_info, Modules, execution_progress
from plup.models import assumptions, classification
from django.db import connection
from django.db.models import Q
# use scenario evaluation with celery
from plup.indicators.EvaluateScenario import run
import json
import shutil
import os
import urllib.parse



from django.contrib.gis.db.models import Union


class scenarioView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = scenario.objects.all()
    filter_fields = ('name', 'description',)
    serializer_class = scenarioSerializer

    def post(self, request, *args, **kwargs):
        file_serializer = scenarioSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        try:
            scenario_id =  kwargs["pk"]
            self.delete_subtables_data(scenario_id)
            scenario.objects.filter(scenario_id=scenario_id).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        try:
            scenario_id = request.data["scenario_id"]
            scenario.objects.filter(scenario_id=scenario_id).update(
                name = request.data["name"],
                description = request.data["description"],
                is_base = request.data["is_base"],
                owner_id = request.data["owner_id"],
                study_area = request.data["study_area"]
                )
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)
    
    def delete_subtables_data(self,scenario):
        Results.objects.filter(scenario=scenario).delete()

        obs_to_delete=transit.objects.filter(scenario=scenario).values_list('transit_id',flat=True)
        transit_info.objects.filter(
            transit_id__in=obs_to_delete
        ).delete()
        transit.objects.filter(scenario=scenario).delete()

        obs_to_delete=jobs.objects.filter(scenario=scenario).values_list('jobs_id',flat=True)
        jobs_info.objects.filter(
            jobs_id__in=obs_to_delete
        ).delete()
        jobs.objects.filter(scenario=scenario).delete()

        obs_to_delete=roads.objects.filter(scenario=scenario).values_list('roads_id',flat=True)
        roads_info.objects.filter(
            roads_id__in=obs_to_delete
        ).delete()
        roads.objects.filter(scenario=scenario).delete()

        obs_to_delete=risk.objects.filter(scenario=scenario).values_list('risk_id',flat=True)
        risk_info.objects.filter(
            risk_id__in=obs_to_delete
        ).delete()
        risk.objects.filter(scenario=scenario).delete()

        obs_to_delete=Amenities.objects.filter(scenario=scenario).values_list('amenities_id',flat=True)
        Amenities_info.objects.filter(
            amenities_id__in=obs_to_delete
        ).delete()
        Amenities.objects.filter(scenario=scenario).delete()

        obs_to_delete=mmu.objects.filter(scenario=scenario).values_list('mmu_id',flat=True)
        mmu_info.objects.filter(
            mmu_id__in=obs_to_delete
        ).delete()
        mmu.objects.filter(scenario=scenario).delete()
        
        footprint.objects.filter(scenario=scenario).delete()


class resultsView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = Results.objects.all()
    filter_fields = ('scenario', 'name',)
    serializer_class = resultsSerializer

    def delete(self, request, *args, **kwargs):
        try:
            Results.objects.filter(scenario=kwargs["pk"]).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)


class resultsDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = resultsSerializer

    def get_queryset(self):
        return Results.objects.all()


class transitView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = transit.objects.all()
    filter_fields = ('scenario', 'fclass',)
    serializer_class = transitSerializer
    def post(self, request, *args, **kwargs):
        try:
            transit.objects.bulk_create(
                [ transit(
                    oskari_code=data["oskari_code"]
                    ,scenario_id=data["scenario"]
                    ,fclass=data["fclass"]
                    ,location=data["location"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="",message="Error when inserting data"+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=transit.objects.exclude(
            fclass__in = classification.objects.filter(category="transit").values_list("name")
        ).extra(select={'category':'\'transit\''}).values('fclass','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["fclass"],fclass=val["fclass"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )

        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        try:
            obs_to_delete=transit.objects.filter(scenario=kwargs["pk"]).values_list('transit_id',flat=True)
            transit_info.objects.filter(
                transit_id__in=obs_to_delete
            ).delete()
            transit.objects.filter(scenario=kwargs["pk"]).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)


class transit_infoView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = transit_info.objects.all()
    filter_fields = ('value', 'name', 'transit_id')
    serializer_class = transit_infoSerializer
    def post(self, request, *args, **kwargs):
        try:
            transit_id=transit.objects.filter(scenario_id=request.data["data"][0]["scenario"]).values("transit_id","oskari_code").order_by('oskari_code')
            
            i=0
            for mu in request.data["data"]:
                for mi in transit_id:
                    if mu["oskari_code"]==mi["oskari_code"]:
                        request.data["data"][i]["transit_id"]=mi["transit_id"]
                i+=1
            
            transit_info.objects.bulk_create(
                [ transit_info(
                    transit_id=data["transit_id"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )

        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=transit_info.objects.exclude(
            name__in = classification.objects.filter(category="name").values_list("name")
        ).extra(select={'category':'\'transit_info\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)


class riskView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = risk.objects.all()
    filter_fields = ('scenario', 'fclass',)
    serializer_class = riskSerializer
    def post(self, request, *args, **kwargs):
        try:
            risk.objects.bulk_create(
                [ risk(
                    oskari_code=data["oskari_code"]
                    ,scenario_id=data["scenario"]
                    ,fclass=data["fclass"]
                    ,location=data["location"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="",message="Error when inserting data "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=risk.objects.exclude(
            fclass__in = classification.objects.filter(category="risk").values_list("name")
        ).extra(select={'category':'\'risk\''}).values('fclass','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["fclass"],fclass=val["fclass"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
            
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        try:
            obs_to_delete=risk.objects.filter(scenario=kwargs["pk"]).values_list('risk_id',flat=True)
            risk_info.objects.filter(
                risk_id__in=obs_to_delete
            ).delete()
            risk.objects.filter(scenario=kwargs["pk"]).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)

class risk_infoView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = risk_info.objects.all()
    filter_fields = ('name', 'value',)
    serializer_class = risk_infoSerializer
    def post(self, request, *args, **kwargs):
        try:
            risk_id=risk.objects.filter(scenario_id=request.data["data"][0]["scenario"]).values("risk_id","oskari_code").order_by('oskari_code')
            
            i=0
            for mu in request.data["data"]:
                for mi in risk_id:
                    if mu["oskari_code"]==mi["oskari_code"]:
                        request.data["data"][i]["risk_id"]=mi["risk_id"]
                i+=1
            
            risk_info.objects.bulk_create(
                [ risk_info(
                    risk_id=data["risk_id"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )

        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=risk_info.objects.exclude(
            name__in = classification.objects.filter(category="name").values_list("name")
        ).extra(select={'category':'\'risk_info\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)


class roadsView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = roads.objects.all()
    filter_fields = ('scenario', 'fclass',)
    serializer_class = roadsSerializer

    def post(self, request, *args, **kwargs):
        try:
            roads.objects.bulk_create(
                [ roads(
                    oskari_code=data["oskari_code"]
                    ,scenario_id=data["scenario"]
                    ,fclass=data["fclass"]
                    ,location=data["location"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when inserting data"+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        
        new_values=roads.objects.exclude(
            fclass__in = classification.objects.filter(category="roads").values_list("name")
        ).extra(select={'category':'\'roads\''}).values('fclass','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["fclass"],fclass=val["fclass"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )

        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        try:
            obs_to_delete=roads.objects.filter(scenario=kwargs["pk"]).values_list('roads_id',flat=True)
            roads_info.objects.filter(
                roads_id__in=obs_to_delete
            ).delete()
            roads.objects.filter(scenario=kwargs["pk"]).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)


class roads_infoView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = roads_info.objects.all()
    filter_fields = ('name', 'value',)
    serializer_class = roads_infoSerializer
    def post(self, request, *args, **kwargs):
        try:
            roads_id=roads.objects.filter(scenario_id=request.data["data"][0]["scenario"]).values("roads_id","oskari_code").order_by('oskari_code')
            
            i=0
            for mu in request.data["data"]:
                for mi in roads_id:
                    if mu["oskari_code"]==mi["oskari_code"]:
                        request.data["data"][i]["roads_id"]=mi["roads_id"]
                i+=1
            
            roads_info.objects.bulk_create(
                [ roads_info(
                    roads_id=data["roads_id"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )

        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=roads_info.objects.exclude(
            name__in = classification.objects.filter(category="name").values_list("name")
        ).extra(select={'category':'\'roads_info\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)


class mmuView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = mmu.objects.all()
    filter_fields = ('scenario', 'oskari_code')
    serializer_class = mmuSerializer

    def post(self, request, *args, **kwargs):
        try:
            mmu.objects.bulk_create(
                [ mmu(
                    oskari_code=data["oskari_code"]
                    ,scenario_id=data["scenario"]
                    ,location=data["location"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        
        return Response(dict(status="", message="All data imported"), status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        query_set = mmu.objects.filter(scenario=request.GET.get(
            "scenario")).values("mmu_id", "mmu_code")
        return Response(query_set)
    
    def delete(self, request, *args, **kwargs):
        try:
            obs_to_delete=mmu.objects.filter(scenario=kwargs["pk"]).values_list('mmu_id',flat=True)
            mmu_info.objects.filter(
                mmu_id__in=obs_to_delete
            ).delete()
            mmu.objects.filter(scenario=kwargs["pk"]).delete()
        except Exception as identifier:
            print(identifier)
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        return Response(status=status.HTTP_200_OK)


class mmu_infoView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = mmu_info.objects.all()
    filter_fields = ('name', 'value')
    serializer_class = mmu_infoSerializer()

    def post(self, request, *args, **kwargs):
        try:
            mmu_id=mmu.objects.filter(scenario_id=request.data["data"][0]["scenario"]).values("mmu_id","oskari_code").order_by('oskari_code')
            
            i=0
            for mu in request.data["data"]:
                for mi in mmu_id:
                    if mu["oskari_code"]==mi["oskari_code"]:
                        request.data["data"][i]["mmu_id"]=mi["mmu_id"]
                i+=1
            
            mmu_info.objects.bulk_create(
                [ mmu_info(
                    mmu_id=data["mmu_id"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )

        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=mmu_info.objects.exclude(
            name__in = classification.objects.filter(category="name").values_list("name")
        ).extra(select={'category':'\'mmu\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)



class jobsView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = jobs.objects.all()
    filter_fields = ('scenario',)
    serializer_class = jobsSerializer

    def post(self, request, *args, **kwargs):
        try:
            jobs.objects.bulk_create(
                [ jobs(
                    oskari_code=data["oskari_code"]
                    ,scenario_id=data["scenario"]
                    ,location=data["location"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="",message="Error when inserting data "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        return Response(dict(statsu="",message="All data created"), status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        try:
            obs_to_delete=jobs.objects.filter(scenario=kwargs["pk"]).values_list('jobs_id',flat=True)
            jobs_info.objects.filter(
                jobs_id__in=obs_to_delete
            ).delete()
            jobs.objects.filter(scenario=kwargs["pk"]).delete()
        except Exception as identifier:
            print(identifier)
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        return Response(status=status.HTTP_200_OK)


class jobs_infoView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = jobs_info.objects.all()
    filter_fields = ('name', 'value')
    serializer_class = jobs_infoSerializer()

    def post(self, request, *args, **kwargs):
        try:
            jobs_id=jobs.objects.filter(scenario_id=request.data["data"][0]["scenario"]).values("jobs_id","oskari_code").order_by('oskari_code')
            i=0
            for mu in request.data["data"]:
                for mi in jobs_id:
                    if mu["oskari_code"]==mi["oskari_code"]:
                        request.data["data"][i]["jobs_id"]=mi["jobs_id"]
                i+=1

            jobs_info.objects.bulk_create(
                [ jobs_info(
                    jobs_id=data["jobs_id"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )

        except Exception as identifier:
            print("Error:",identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=jobs_info.objects.exclude(
            name__in = classification.objects.filter(category="name").values_list("name")
        ).extra(select={'category':'\'jobs_info\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)



class footprintView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = footprint.objects.all()
    filter_fields = ('scenario',)
    serializer_class = footprintSerializer
    def post(self, request, *args, **kwargs):
        try:
            footprint.objects.bulk_create(
                [ footprint(
                    scenario_id=data["scenario"]
                    ,name=data["name"]
                    ,location=data["location"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="",message="Error when inserting data "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        
        new_values = footprint.objects.exclude(
        name__in = classification.objects.filter(category="footprint").values_list("name")
        ).extra(select={'category':'\'footprint\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)
    def delete(self, request, *args, **kwargs):
        try:
            scenario_id = kwargs["pk"]
            footprint.objects.filter(scenario=scenario_id).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(False, status=status.HTTP_400_BAD_REQUEST)


class amenitiesView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = Amenities.objects.all()
    filter_fields = ('scenario', 'fclass')
    serializer_class = amenitiesSerializer

    def post(self, request, *args, **kwargs):
        try:
            Amenities.objects.bulk_create(
                [ Amenities(
                    oskari_code=data["oskari_code"]
                    ,scenario_id=data["scenario"]
                    ,fclass=data["fclass"]
                    ,location=data["location"]
                ) for data in request.data["data"]
                ],ignore_conflicts=True
            )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="",message="Error when inserting data "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        new_values=Amenities.objects.exclude(
            fclass__in = classification.objects.filter(category="amenities").values_list("name")
        ).extra(select={'category':'\'amenities\''}).values('fclass','category').distinct()
        
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["fclass"],fclass=val["fclass"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        print(kwargs["pk"])
        try:
            scenario_id = kwargs["pk"]
            obs_to_delete=Amenities.objects.filter(scenario=scenario_id).values_list('amenities_id',flat=True)
            Amenities_info.objects.filter(
                amenities_id__in=obs_to_delete
            ).delete()
            Amenities.objects.filter(scenario=scenario_id).delete()
        except Exception as identifier:
            print(identifier)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)
        return Response(True, status=status.HTTP_201_CREATED)


class amenities_infoView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = Amenities_info.objects.all()
    filter_fields = ('value', 'name')
    serializer_class = amenities_infoSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            amenities_id=Amenities.objects.filter(scenario_id=request.data["data"][0]["scenario"]).values("amenities_id","oskari_code").order_by('oskari_code')
            
            i=0
            for mu in request.data["data"]:
                for mi in amenities_id:
                    if mu["oskari_code"]==mi["oskari_code"]:
                        request.data["data"][i]["amenities_id"]=mi["amenities_id"]
                i+=1
            
            Amenities_info.objects.bulk_create(
                [ Amenities_info(
                    amenities_id=data["amenities_id"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )

        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        new_values=Amenities_info.objects.exclude(
            name__in = classification.objects.filter(category="name").values_list("name")
        ).extra(select={'category':'\'amenities_info\''}).values('name','category').distinct()
        if len(new_values)>0:
            classification.objects.bulk_create(
                [classification(name=val["name"],fclass=val["name"], category=val["category"]) for val in 
                    new_values
                ]
                ,ignore_conflicts=True
            )
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)


class assumptionsView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = assumptions.objects.all()
    filter_fields = ('scenario', 'category', 'name',  'value')
    serializer_class = assumptionsSerializer
    def post(self, request, *args, **kwargs):
        try:
            assumptions.objects.bulk_create(
                [ assumptions(
                    scenario_id=data["scenario"]
                    ,category=data["category"]
                    ,name=data["name"]
                    ,value=data["value"]
                ) for data in request.data["data"]]
                ,ignore_conflicts=True
            )
            # update all scenarios in same study_are
            study_area=scenario.objects.filter(scenario_id=request.data["data"][0]["scenario"],owner_id=request.data["data"][0]["owner_id"]).values_list('study_area',flat=True)[:1][0]
            scenarios=scenario.objects.filter(~Q(scenario_id=request.data["data"][0]["scenario"]),study_area=study_area,owner_id=request.data["data"][0]["owner_id"]).values_list('scenario_id',flat=True)
            for scen in scenarios:
                assumptions.objects.bulk_create(
                    [ assumptions(
                        scenario_id=scen
                        ,category=data["category"]
                        ,name=data["name"]
                        ,value=data["value"]
                    ) for data in request.data["data"]]
                    ,ignore_conflicts=True
                )
        except Exception as identifier:
            print(identifier)
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        try:
            scenario_id = kwargs["pk"]
            assumptions.objects.filter(scenario_id=scenario_id).delete()
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(False, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        try:
            assumptions.objects.filter(scenario_id = request.data["scenario"],
                category = request.data["category"],
                name = request.data["name"]).update(
                value = request.data["value"]
                )
            return Response(True, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(False, status=status.HTTP_400_BAD_REQUEST)


class scenarioResultsView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    
    #queryset = scenario.objects.all()
    filter_fields = ('scenario_id', 'name',)
    serializer_class = ScenarioResultsSerializer
    def get_queryset(self):
        params = urllib.parse.unquote(self.kwargs["scenarios"])
        scenarios = [int(data) for data in params.replace(" ", "").split("_")]
        queryset = scenario.objects.filter(scenario_id__in=scenarios).order_by('name')
        return queryset


class scenarioResultsDetailView(generics.ListCreateAPIView):
    lookup_field = 'scenario_id'
    serializer_class = ScenarioResultsSerializer
    def get(self, request, *args, **kwargs):
        print(kwargs["scenarios"])
        params = urllib.parse.unquote(kwargs["scenarios"])
        print(params)
        scenarios = params[1:-1].replace(" ", "").split("_")

        output = ScenarioResultsSerializer.serialize('json',scenario.objects.filter(scenario_id__in=scenarios))
        return output
    def get_queryset(self):
        return scenario.objects.all()


class ExcecutionProgress(APIView):
    def get(self, request, *args, **kwargs):
        scenario=urllib.parse.unquote(request.query_params.get('scenario'))
        scenarios = [int(data) for data in scenario.replace(" ", "").split("_")]
        results = execution_progress.objects.filter(scenario__in=scenarios).values(
             "id","scenario_id", "event", "value", "created_on").order_by("-id")

        return Response(results,status=status.HTTP_200_OK)


class ModulesView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        try:
            file_serializer = ModuleSerializer(data=request.data)
            if file_serializer.is_valid():
                file_serializer.save()
                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(file_serializer.errors)
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        
        queryset = Modules.objects.order_by('name','module')
        modules = ModuleListSerializer(queryset, many=True)
        return Response(modules.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        try:
            pathname = os.path.dirname(os.path.realpath(__file__))
            __module_path = os.path.abspath(pathname+"/indicators/"+kwargs["module"]+"/")
            __module_path_zip=os.path.abspath(pathname+"../media/"+kwargs["module"]+".zip")
            Modules.objects.filter(module=kwargs["module"]).delete()
            
        except Exception as identifier:
            print(identifier)
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        return Response(status=status.HTTP_200_OK)

class ClassificationView(generics.ListCreateAPIView):
    serializer_class = ClassificationSerializer
    def post(self, request, *args, **kwargs):
        file_serializer = ClassificationSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        query_set = classification.objects.all()
        modules = ClassificationSerializer(query_set, many=True)
        return Response(modules.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        try:
            classifier = classification.objects.get(classification_id=kwargs["pk"])
        except Exception as identifier:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClassificationSerializer(classifier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            classification.objects.filter(classification_id=kwargs["pk"]).delete()
        except Exception as identifier:
            print(identifier)
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        return Response(status=status.HTTP_200_OK)

class ModulesTablesView(APIView):
    def get(self, request, *args, **kwargs):
        import urllib.parse
        import numpy as np

        params = urllib.parse.unquote(request.query_params.get('modules'))
        
        params_list = params[1:-1].replace(" ", "").split(",")
        first_query = Modules.objects.values(
            "data_dependencies").filter(module__in=params_list)
        
        data = []
        for row in first_query:
            
            data.append(json.loads(row["data_dependencies"]))
        tables = []
        
        for i in data:
            for j in i:
                for table in j["tables"]:
                    tables.append(table)
        temp = np.array(tables)
        return Response(np.unique(temp))

class ModulesAllTablesView(APIView):
    def get(self, request, *args, **kwargs):
        import urllib.parse
        import numpy as np

        first_query = Modules.objects.values("data_dependencies")
        
        data = []
        for row in first_query:
            data.append(json.loads(row["data_dependencies"]))

        tables = []
        for i in data:
            for j in i:
                for table in j["tables"]:
                    tables.append(table)
        temp = np.array(tables)
        return Response(np.unique(temp))


class TableColumnsView(APIView):
    def get(self, request, *args, **kwargs):
        import urllib.parse
        from django.apps import apps
        table = urllib.parse.unquote(request.query_params.get('table'))
        model = apps.get_model('plup', table)
        first_query = model._meta.fields

        columns = [f.name for f in first_query]
        if 'id' in columns:
            columns.remove('id')
        if 'buffer' in columns:
            columns.remove('buffer')
        if 'created' in columns:
            columns.remove('created')
        if 'updated' in columns:
            columns.remove('updated')
        if 'oskari_code' in columns:
            columns.remove('oskari_code')
        if table != 'scenario' and 'scenario' in columns:
            columns.remove('scenario')
        if table=="footprint" and ('value') in columns:
            columns.remove('value')
        if table.find("amenities_info") >= 0 and (table+'_id') in columns:
            columns.remove(table+'_id')
        if table.find("_info") > 0 and ('name') in columns:
            columns.remove(table.replace("_info",""))
            columns.remove('name')
        if table.find("_info") < 0 and (table+'_id') in columns:
            columns.remove(table+'_id')
        return Response(columns)


class ScenarioEvalView(APIView):
    def post(self, request, *args, **kwargs):
        scenarios=request.POST.get("scenario", "").split("_")
        for i in range(0, len(scenarios)):
            scenarios[i]=int(scenarios[i])
        execution_progress.objects.filter(scenario__in=scenarios).delete()
        resultado = run.delay(request.POST.get("user", ""), request.POST.get(
             "scenario", ""), request.POST.get("indicators", ""))
        
        return Response(dict(id=1, event="Evaluating", value="", created_on=None, scenario_id=1))
    
    def get(self, request, *args, **kwargs):
        self.__scenario = kwargs["scenario"]
        self.__user = kwargs["user"]
        self.__projection= kwargs["projection"]
        all_buffers = self.__getAmentityBuffers()
        all_buffers += self.__getRoadsBuffers()
        all_buffers += self.__getTransitBuffers()
        all_buffers += self.__getJobsBuffers()
        return Response(all_buffers)
    
    def __getAmentityBuffers(self):
        try:
            buffers=[]

            query="""
            with data_buff as(
                select fclass,st_union(buffer) as buffer from amenities where scenario_id={scenario}
                and buffer is not null
                group by fclass
            )
            select 
                {scenario} as scenario_id,
                {user} as user_id,
                concat('{name}', fclass,' buffer') as name,
                concat('EPSG:', {projection}::text) as projection,
                json_build_object(
                        'type',
                        'FeatureCollection',
                        'crs',
                        json_build_object(
                            'type', 
                            'name', 
                            'properties', 
                            json_build_object(
                                'name', 
                                concat('EPSG:', {projection}::text)
                            )
                        ), 
                        'features', 
                        json_agg(
                            json_build_object(
                                'type', 
                                'Feature',
                                'geometry', 
                                ST_AsGeoJSON (st_setsrid(st_transform(buffer,{projection}),0))::json, 
                                'properties', 
                                json_build_object(
                                    'type', 
                                    replace(st_geometrytype (buffer), 'ST_', '')
                                    , 'value', 
                                    st_area(buffer)/1e-6
                                )
                            )
                        )
                    )::text as geojson
            from data_buff group by fclass
            """.format(projection=self.__projection,name="amenities ",scenario=self.__scenario,user=self.__user)
            cursor = connection.cursor()
            cursor.execute(query)
            buffers = [dict(scenario_id=row[0], user_id=row[1], name=row[2], projection=row[3], buffer="{\"0\":"+row[4]+"}") for row in cursor.fetchall()]
            for elem in range(0,len(buffers)):
                if "null" in buffers[elem]["buffer"]:
                    buffers.pop(elem)
            return buffers
        except Exception as e:
            return buffers

    def __getRoadsBuffers(self):
        try:
            buffers=[]
            
            query="""
            with data_buff as(
                select fclass,st_union(buffer) as buffer from roads where scenario_id={scenario}
                and buffer is not null
                group by fclass
            )
            select 
                {scenario} as scenario_id,
                {user} as user_id,
                concat('{name}', fclass,' buffer') as name,
                concat('EPSG:', {projection}::text) as projection,
                json_build_object(
                        'type',
                        'FeatureCollection',
                        'crs',
                        json_build_object(
                            'type', 
                            'name', 
                            'properties', 
                            json_build_object(
                                'name', 
                                concat('EPSG:', {projection}::text)
                            )
                        ), 
                        'features', 
                        json_agg(
                            json_build_object(
                                'type', 
                                'Feature',
                                'geometry', 
                                ST_AsGeoJSON (st_setsrid(st_transform(buffer,{projection}),0))::json, 
                                'properties', 
                                json_build_object(
                                    'type', 
                                    replace(st_geometrytype (buffer), 'ST_', '')
                                    , 'value', 
                                    st_area(buffer)/1e-6
                                )
                            )
                        )
                    )::text as geojson
            from data_buff group by fclass
            """.format(projection=self.__projection,name="roads ",scenario=self.__scenario,user=self.__user)
            cursor = connection.cursor()
            cursor.execute(query)
            buffers = [dict(scenario_id=row[0], user_id=row[1], name=row[2], projection=row[3], buffer="{\"0\":"+row[4]+"}") for row in cursor.fetchall()]
            for elem in range(0,len(buffers)):
                if "null" in buffers[elem]["buffer"]:
                    buffers.pop(elem)
            return buffers
        except Exception as e:
            return buffers

    def __getTransitBuffers(self):
        try:
            buffers=[]
            query="""
            with data_buff as(
                select fclass,st_union(buffer) as buffer from transit where scenario_id={scenario} and buffer is not null group by fclass
            )
            select 
                {scenario} as scenario_id,
                {user} as user_id,
                concat('{name}', fclass,' buffer') as name,
                concat('EPSG:', {projection}::text) as projection,
                json_build_object(
                        'type',
                        'FeatureCollection',
                        'crs',
                        json_build_object(
                            'type', 
                            'name', 
                            'properties', 
                            json_build_object(
                                'name', 
                                concat('EPSG:', {projection}::text)
                            )
                        ), 
                        'features', 
                        json_agg(
                            json_build_object(
                                'type', 
                                'Feature',
                                'geometry', 
                                ST_AsGeoJSON (st_setsrid(st_transform(buffer,{projection}),0))::json, 
                                'properties', 
                                json_build_object(
                                    'type', 
                                    replace(st_geometrytype (buffer), 'ST_', '')
                                    , 'value', 
                                    st_area(buffer)/1e-6
                                )
                            )
                        )
                    )::text as geojson
            from data_buff group by fclass
            """.format(projection=self.__projection,name="transit ",scenario=self.__scenario,user=self.__user)
            cursor = connection.cursor()
            cursor.execute(query)
            buffers = [dict(scenario_id=row[0], user_id=row[1], name=row[2], projection=row[3], buffer="{\"0\":"+row[4]+"}") for row in cursor.fetchall()]
            for elem in range(0,len(buffers)):
                if "null" in buffers[elem]["buffer"]:
                    buffers.pop(elem)
            
            return buffers
        except Exception as e:
            return buffers
    
    def __getJobsBuffers(self):
        try:
            buffers=[]
            query="""
            with data_buff as(
                select st_union(buffer) as buffer from jobs where scenario_id={scenario}
                and buffer is not null
            )
            select 
                {scenario} as scenario_id,
                {user} as user_id,
                concat('{name}',' buffer') as name,
                concat('EPSG:', {projection}::text) as projection,
                json_build_object(
                        'type',
                        'FeatureCollection',
                        'crs',
                        json_build_object(
                            'type', 
                            'name', 
                            'properties', 
                            json_build_object(
                                'name', 
                                concat('EPSG:', {projection}::text)
                            )
                        ), 
                        'features', 
                        json_agg(
                            json_build_object(
                                'type', 
                                'Feature',
                                'geometry', 
                                ST_AsGeoJSON (st_setsrid(st_transform(buffer,{projection}),0))::json, 
                                'properties', 
                                json_build_object(
                                    'type', 
                                    replace(st_geometrytype (buffer), 'ST_', '')
                                    , 'value', 
                                    st_area(buffer)/1e-6
                                )
                            )
                        )
                    )::text as geojson
            from data_buff
            """.format(projection=self.__projection,name="jobs ",scenario=self.__scenario,user=self.__user)
            cursor = connection.cursor()
            cursor.execute(query)
            
            buffers = [dict(scenario_id=row[0], user_id=row[1], name=row[2], projection=row[3], buffer="{\"0\":"+row[4]+"}") for row in cursor.fetchall()]
            for elem in range(0,len(buffers)):
                if "null" in buffers[elem]["buffer"]:
                    buffers.pop(elem)
            
            return buffers
        except Exception as e:
            return buffers

