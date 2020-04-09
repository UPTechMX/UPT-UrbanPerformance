import json
import copy
from rest_framework import serializers
from plup.models import scenario, Results, Amenities, transit, risk, roads, mmu
from plup.models import jobs, footprint, assumptions, risk_info, roads_info
from plup.models import Amenities_info, transit_info, mmu_info, jobs_info
# Needed to install indicators
from plup.models import Modules,classification
from .functions import getIdIndex
from django.contrib.gis.db import models


class resultsSerializer(serializers.ModelSerializer):
    scenario = serializers.PrimaryKeyRelatedField(
        queryset=scenario.objects.all())

    class Meta:
        model = Results
        fields = [
            "results_id",
            "scenario",
            "name",
            "value",
        ]


class amenities_infoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Amenities_info
        fields = [
            "id",
            "amenities_id",
            "name",
            "value",
        ]
        read_only_fields = ("amenities_id",)


class amenitiesSerializer(serializers.ModelSerializer):
    amenities_info = amenities_infoSerializer(many=True, required=False)

    class Meta:
        model = Amenities
        fields = [
            "amenities_id",
            "scenario",
            "fclass",
            "location",
            "buffer",
            "amenities_info"
        ]
    
    def create(self, validated_data):
        amenitiy_infos = validated_data.pop('amenities_info')
        amenities_inserted = Amenities.objects.create(**validated_data)
        info = []
        
        for amenity_info in amenitiy_infos:
            info.append(Amenities_info(amenities=amenities_inserted, name=amenity_info['name'], value=amenity_info['value']))
        Amenities_info.objects.bulk_create(info)
        return amenities_inserted

    def update(self, instance, validated_data):
        amenity_info = validated_data.pop('amenities_info')
        infos = (instance.amenities_info).all()
        infos = list(infos)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.fclass = validated_data.get('fclass', instance.fclass)
        instance.location = validated_data.get('location', instance.location)
        instance.buffer = validated_data.get('buffer', instance.buffer)
        instance.save()

        info_create = []
        info_update = []
        for amenity_inf in amenity_info:
            if 'id' in amenity_inf:
                index = getIdIndex(infos, amenity_inf['id'])
                if index >= 0:
                    inf = infos.pop(index)
                    inf.name = amenity_inf['name']
                    inf.value = amenity_inf['value']
                    info_update.append(inf)
            else:
                info_create.append(Amenities_info(amenities=instance, name=amenity_inf['name'], value=amenity_inf['value']))
        #Bulk create for the new info
        Amenities_info.objects.bulk_create(info_create)
        #Bulk update for the info changes
        Amenities_info.objects.bulk_update(info_update, ['name', 'value'])
        #Delete information without mention
        for info in infos:
            info.delete()
        return instance

class transit_infoSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(required=False)

    class Meta:
        model = transit_info
        fields = [
            "id",
            "transit_id",
            "name",
            "value",
        ]
        read_only_fields = ("transit_id",)


class transitSerializer(serializers.ModelSerializer):
    transit_info = transit_infoSerializer(many=True, required=False)

    class Meta:
        model = transit
        fields = [
            "transit_id",
            "scenario",
            "fclass",
            "location",
            "buffer",
            "transit_info",
        ]

    def create(self, validated_data):
        transit_infos = validated_data.pop('transit_info')
        transit_inserted = transit.objects.create(**validated_data)
        info = []
        for transit_inf in transit_infos:
            info.append(transit_info(transit=transit_inserted, name=transit_inf['name'], value=transit_inf['value']))
        transit_info.objects.bulk_create(info)
        return transit_inserted

    def update(self, instance, validated_data):
        transit_info_data = validated_data.pop('transit_info')
        infos = (instance.transit_info).all()
        infos = list(infos)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.fclass = validated_data.get('fclass', instance.fclass)
        instance.location = validated_data.get('location', instance.location)
        instance.buffer = validated_data.get('buffer', instance.buffer)
        instance.save()

        info_create = []
        info_update = []
        for transit_inf in transit_info_data:
            if 'id' in transit_inf:
                index = getIdIndex(infos, transit_inf['id'])
                if index >= 0:
                    inf = infos.pop(index)
                    inf.name = transit_inf['name']
                    inf.value = transit_inf['value']
                    info_update.append(inf)
            else:
                info_create.append(transit_info(transit=instance, name=transit_inf['name'], value=transit_inf['value']))
        #Bulk create for the new info
        transit_info.objects.bulk_create(info_create)
        #Bulk update for the info changes
        transit_info.objects.bulk_update(info_update, ['name', 'value'])
        #Delete information without mention
        for info in infos:
            info.delete()
        return instance


class risk_infoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = risk_info
        fields = [
            "id",
            "risk_id",
            "name",
            "value",
        ]
        read_only_fields = ("risk_id",)


class riskSerializer(serializers.ModelSerializer):
    risk_info = risk_infoSerializer(many=True, required=False)
    class Meta:
        model = risk
        fields = [
            "risk_id",
            "scenario",
            "fclass",
            "location",
            "buffer",
            "risk_info",
        ]

    def create(self, validated_data):
        risk_info_data = validated_data.pop('risk_info')
        risk_inserted = risk.objects.create(**validated_data)
        info = []
        for risk_info in risk_info_data:
            info.append(risk_info(risk=risk_inserted, name=risk_info['name'], value=risk_info['value']))
        risk_info.objects.bulk_create(info)
        return risk_inserted

    def update(self, instance, validated_data):
        risk_info_data = validated_data.pop('risk_info')
        infos = (instance.risk_info).all()
        infos = list(infos)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.fclass = validated_data.get('fclass', instance.fclass)
        instance.location = validated_data.get('location', instance.location)
        instance.buffer = validated_data.get('buffer', instance.buffer)
        instance.save()

        info_create = []
        info_update = []
        for risk_info in risk_info_data:
            if 'id' in risk_info:
                index = getIdIndex(infos, risk_info['id'])
                if index >= 0:
                    inf = infos.pop(index)
                    inf.name = risk_info['name']
                    inf.value = risk_info['value']
                    info_update.append(inf)
            else:
                info_create.append(risk_info(risk=instance, name=risk_info['name'], value=risk_info['value']))
        #Bulk create for the new info
        risk_info.objects.bulk_create(info_create)
        #Bulk update for the info changes
        risk_info.objects.bulk_update(info_update, ['name', 'value'])
        #Delete information without mention
        for info in infos:
            info.delete()
        return instance


class roads_infoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = roads_info
        fields = [
            "id",
            "roads_id",
            "name",
            "value",
        ]
        read_only_fields = ("roads_id",)


class roadsSerializer(serializers.ModelSerializer):
    roads_info = roads_infoSerializer(many=True, required=False)
    class Meta:
        model = roads
        fields = [
            "roads_id",
            "scenario",
            "fclass",
            "location",
            "buffer",
            "roads_info",
        ]

    def create(self, validated_data):
        roads_info_data = validated_data.pop('roads_info')
        roads_inserted = roads.objects.bulk_create(**validated_data)
        roads_info.objects.bulk_create([ roads_info(roads=roads_inserted, name=road_inf['name'], value=road_inf['value']) for road_inf in roads_info_data])
        
        return roads_inserted

    def update(self, instance, validated_data):
        roads_info_data = validated_data.pop('roads_info')
        infos = (instance.roads_info).all()
        infos = list(infos)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.fclass = validated_data.get('fclass', instance.fclass)
        instance.location = validated_data.get('location', instance.location)
        instance.buffer = validated_data.get('buffer', instance.buffer)
        instance.save()

        info_create = []
        info_update = []
        for roads_inf in roads_info_data:
            if 'id' in roads_inf:
                index = getIdIndex(infos, roads_inf['id'])
                if index >= 0:
                    inf = infos.pop(index)
                    inf.name = roads_inf['name']
                    inf.value = roads_inf['value']
                    info_update.append(inf)
            else:
                info_create.append(roads_info(roads=instance, name=roads_inf['name'], value=roads_inf['value']))
        #Bulk create for the new info
        roads_info.objects.bulk_create(info_create)
        #Bulk update for the info changes
        roads_info.objects.bulk_update(info_update, ['name', 'value'])
        #Delete information without mention
        for info in infos:
            info.delete()
        return instance


class mmu_infoSerializer(serializers.ModelSerializer):
    class Meta:
        model = mmu_info
        fields = [
            "id",
            "mmu_id",
            "name",
            "value",
        ]
        read_only_fields = ("mmu_id",)


class mmuSerializer(serializers.ModelSerializer):
    mmu_info = mmu_infoSerializer(many=True, required=False)

    class Meta:
        model = mmu
        fields = [
            "mmu_id",
            "oskari_code",
            "scenario",
            "location",
            "mmu_info",
        ]

    def create(self, validated_data):
        mmu_infos = validated_data.pop('mmu_info')
        mmu_inserted = mmu.objects.create(**validated_data)
        info = []
        for mmu_inf in mmu_infos:
            info.append(mmu_info(mmu_id=mmu_inserted.mmu_id, name=mmu_inf['name'], value=mmu_inf['value']))
        mmu_info.objects.bulk_create(info,ignore_conflicts=True)
        return mmu_inserted

    def update(self, instance, validated_data):
        mmu_infos = validated_data.pop('mmu_info')
        infos = (instance.mmu_info).all()
        infos = list(infos)
        instance.mmu_code = validated_data.get('mmu_code', instance.mmu_code)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.location = validated_data.get('location', instance.location)
        instance.save()

        info_create = []
        info_update = []
        for mmu_inf in mmu_infos:
            if 'id' in mmu_inf:
                index = getIdIndex(infos, mmu_infos['id'])
                if index >= 0:
                    inf = infos.pop(index)
                    inf.name = mmu_inf['name']
                    inf.value = mmu_inf['value']
                    info_update.append(inf)
            else:
                info_create.append(mmu_info(mmu_id=instance.mmu_id, name=mmu_inf['name'], value=mmu_inf['value']))
        #Bulk create for the new info
        mmu_info.objects.bulk_create(info_create,ignore_conflicts=True)
        #Bulk update for the info changes
        mmu_info.objects.bulk_update(info_update, ['name', 'value'])
        #Delete information without mention
        for info in infos:
            info.delete()
        return instance

class jobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobs
        fields = [
            "jobs_id",
            "scenario",
            "location",
            "buffer",
        ]


class jobs_infoSerializer(serializers.ModelSerializer):
    class Meta:
        model = jobs_info
        fields = [
            "id",
            "jobs_id",
            "name",
            "value",
        ]


class footprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = footprint
        fields = [
            "footprint_id",
            "scenario",
            "name",
            "value",
            "location",
        ]


class assumptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = assumptions
        fields = [
            "assumptions_id",
            "scenario",
            "name",
            "value",
            "category",
        ]

class ResultScenarioSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('get_sdg_name')
    
    def get_sdg_name(self, obj):
        result = list(Modules.objects.filter(data_generated__contains=obj.name).values('data_generated'))
        
        for i in range(0, len(result)):
            row_json = json.loads(result[i]["data_generated"])
            for row in row_json:
                if "field" in row and obj.name== row["field"] :
                    return row["goal"]
        return ""
    class Meta:
        model = Results
        fields = ["name", "value", 'category']
    

class ScenarioResultsSerializer(serializers.ModelSerializer):
    results = ResultScenarioSerializer(many=True)
    class Meta:
        model = scenario
        fields = ['scenario_id', 'name', 'results']


class TransitSerializer(serializers.ModelSerializer):
    class Meta:
        model = transit
        fields = ['transit_id', 'scenario_id', 'fclass',
                  'location', 'buffer', ]

class TransitInfoSerializer(serializers.ModelSerializer):
    transit_id = TransitSerializer(many=True)

    class Meta:
        model = transit_info
        fields = ["name", "value", "transit_id"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = "__all__"
    
    def is_valid(self,*args, **kwargs):
        file_copy= copy.deepcopy(self.initial_data.get("file"))
        name=str(file_copy)[:-4]
        results=Modules.objects.filter(module=name).values_list('id',flat=True)
        if len(results)>0:
            identifier = results[:1][0]
            Modules.objects.filter(id=identifier).delete()
        return super(ModuleSerializer,self).is_valid()

class ModuleListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='module')

    class Meta:
        model=Modules
        fields=[
            "module",
            "name",
            "description",
            "dependencies",
        ]

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = classification
        fields = [
            "classification_id",
            "category",
            "name",
            "fclass"
        ]

class ModulesTablesListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='module')

    class Meta:
        model=Modules
        fields=[
            "dependencies",
        ]
class scenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = scenario
        fields = [
            "scenario_id",
            "name",
            "description",
            "owner_id",
            "study_area",
            "is_base",
        ]

    