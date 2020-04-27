# required to upload zip files(compressed indicators)
import os
from zipfile import ZipFile
import json
import shutil
import os.path
# requiered to list files in directory
import glob
# required to use partitions in postgresql
#import architect
from django.conf import settings
from django.contrib.gis.db import models
from django.dispatch import receiver
from django.db.models import Max
from django.db import connection

# Create your models here.


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class scenario(models.Model):
    scenario_id = models.IntegerField(null=False, primary_key=True)
    name = models.CharField(max_length=45, null=False)
    description = models.CharField(max_length=45, null=False)
    is_base = models.IntegerField(null=True)
    owner_id = models.CharField(max_length=45, null=False)
    study_area = models.IntegerField(null=False)

    class Meta:
        db_table = "scenario"
        unique_together = (("name", "owner_id"),)
        indexes = [
            models.Index(fields=['scenario_id', ]),
            models.Index(fields=['name', ]),
            models.Index(fields=['owner_id', ]),
        ]


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class risk(models.Model):
    risk_id = models.AutoField(null=False, primary_key=True)
    oskari_code = models.BigIntegerField(null=False)
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    fclass = models.CharField(max_length=100, null=False)
    location = models.GeometryField(srid=4326, null =False)
    buffer = models.GeometryField(srid=4326,null=True)

    class Meta:
        db_table = "risk"
        unique_together=(("scenario","oskari_code",),)
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['fclass', ]),
        ]

    @property
    def risk_info(self):
        return self.risk_info_set.all()


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='risk_id')
class risk_info(models.Model):
    
    risk = models.ForeignKey(risk, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "risk_info"
        unique_together=(("risk","name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]



# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class roads(models.Model):
    roads_id = models.AutoField(null=False, primary_key=True)
    oskari_code = models.BigIntegerField(null=False)
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    fclass = models.CharField(max_length=100, null=False)
    location = models.GeometryField(srid=4326)
    buffer = models.GeometryField(srid=4326, null=True)

    class Meta:
        db_table = "roads"
        unique_together=(("scenario","oskari_code"),)
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['fclass', ]),
        ]

    @property
    def roads_info(self):
        return self.roads_info_set.all()


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='roads_id')
class roads_info(models.Model):
    
    roads = models.ForeignKey(roads, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "roads_info"
        unique_together=(("roads","name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]



# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class Amenities(models.Model):
    amenities_id = models.AutoField(null=False, primary_key=True)
    oskari_code = models.BigIntegerField(null=False)
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    fclass = models.CharField(max_length=100, null=False)
    location = models.GeometryField(srid=4326, null=False)
    buffer = models.GeometryField(srid=4326, null=True)

    class Meta:
        db_table = "amenities"
        unique_together = (("scenario", "oskari_code"),)
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['fclass', ]),
        ]

    @property
    def amenities_info(self):
        return self.amenities_info_set.all()


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='amenities_id')
class Amenities_info(models.Model):
    
    amenities = models.ForeignKey(Amenities, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "amenities_info"
        unique_together=(("amenities","name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class transit(models.Model):
    transit_id = models.AutoField(null=False, primary_key=True)
    oskari_code = models.BigIntegerField(null=False)
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    fclass = models.CharField(max_length=100, null=False)
    location = models.GeometryField(srid=4326)
    buffer = models.GeometryField(srid=4326,null=True)

    class Meta:
        db_table = "transit"
        unique_together=(("scenario","oskari_code"),)
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['fclass', ]),
        ]

    @property
    def transit_info(self):
        return self.transit_info_set.all()


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='transit_id')
class transit_info(models.Model):
    
    transit = models.ForeignKey(transit, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "transit_info"
        unique_together=(("transit","name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]



# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class mmu(models.Model):
    mmu_id = models.AutoField(null=False, primary_key=True)
    oskari_code = models.BigIntegerField(null=False)
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE, null=False)
    location = models.GeometryField(srid=4326)

    class Meta:
        unique_together = (("scenario", "oskari_code"),)
        db_table = "mmu"

    @property
    def mmu_info(self):
        return self.mmu_info_set.all()



# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='mmu_id')
class mmu_info(models.Model):
    
    mmu = models.ForeignKey(mmu, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "mmu_info"
        unique_together = (("mmu", "name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]



# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class jobs(models.Model):
    jobs_id = models.AutoField(null=False, primary_key=True)
    oskari_code = models.BigIntegerField(null=False)
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    location = models.GeometryField(srid=4326,null=False)
    buffer = models.GeometryField(srid=4326,null=True)

    class Meta:
        db_table = "jobs"
        unique_together=(("scenario","oskari_code"),)
        indexes = [
            models.Index(fields=['scenario', ]),
        ]

    @property
    def jobs_info(self):
        return self.jobs_info.all()


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='jobs_id')
class jobs_info(models.Model):
    
    jobs = models.ForeignKey(jobs, on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "jobs_info"
        unique_together=(("jobs","name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]



# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class footprint(models.Model):
    footprint_id = models.AutoField(null=False, primary_key=True)
    
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False)
    value = models.FloatField(null=True)
    location = models.GeometryField(srid=4326)

    class Meta:
        db_table = "footprint"
        unique_together=(("scenario","name"),)
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
        ]


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class assumptions(models.Model):
    assumptions_id = models.AutoField(null=False, primary_key=True)
    
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    category = models.CharField(max_length=45, null=False)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "assumptions"
        unique_together=(("scenario","category","name"),)
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['category', ]),
            models.Index(fields=['name', ]),
        ]


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class Results(models.Model):
    results_id = models.AutoField(null=False, primary_key=True)
    
    scenario = models.ForeignKey(
        scenario, related_name='results', on_delete=models.CASCADE)
    name = models.CharField(max_length=45, null=False)
    value = models.FloatField(null=False)

    class Meta:
        db_table = "results"
        unique_together = (("scenario", "name"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['value', ]),
            models.Index(fields=['scenario', ]),
        ]

class classification(models.Model):
    classification_id = models.AutoField(null=False, primary_key=True)
    category = models.CharField(max_length=45, null=False)
    name = models.CharField(max_length=100, null=False)
    fclass = fclass = models.CharField(max_length=45, null=True)

    class Meta:
        db_table = "classification"
        unique_together = (("category", "name","fclass"),)
        indexes = [
            models.Index(fields=['name', ]),
            models.Index(fields=['fclass', ]),
            models.Index(fields=['category', ]),
        ]


# @architect.install('partition', type='range', subtype='integer', constraint='500000', column='scenario_id')
class execution_progress(models.Model):
    scenario = models.ForeignKey(scenario, on_delete=models.CASCADE)
    event = models.CharField(max_length=150, null=False)
    value = models.TextField()
    created_on = models.TimeField(
        (u"Conversation Time"), auto_now_add=True, blank=True)

    class Meta:
        db_table = "execution_progress"
        indexes = [
            models.Index(fields=['scenario', ]),
            models.Index(fields=['created_on', ]),
        ]


class Modules(models.Model):
    file = models.FileField(blank=False, null=False, unique=True)
    module = models.TextField(blank=True, null=False, unique=True)
    name = models.TextField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    developer = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    dependencies = models.TextField(blank=True, null=True)
    data_dependencies = models.TextField(blank=True, null=True)
    data_generated = models.TextField(blank=True, null=True)
    submodules = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, default=-1)

    class Meta:
        db_table = "modules"

    def save(self, *args, **kwargs):
        name = str(self.file.name)[:-4]
        self.module = name
        super(Modules, self).save(*args, **kwargs)


@receiver(models.signals.post_delete, sender=Modules)
def delete(sender, instance, **kwargs):
    if instance.file:
        path_to_file = os.path.realpath(os.path.join(
            os.path.dirname(__file__), "..", "media", str(instance.file)))
        path_to_extracted = os.path.realpath(os.path.join(
            os.path.dirname(__file__), "..", "plup", "indicators", str(instance.file)[:-4]))
        #print(path_to_file, path_to_extracted)
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)
        if os.path.isdir(path_to_extracted):
            shutil.rmtree(path_to_extracted, ignore_errors=False, onerror=None)


@receiver(models.signals.post_save, sender=Modules)
def save(sender, instance, **kwargs):
    
    path_to_extrat = __unzip(instance.file)
    data = __register_module(path_to_extrat)
    
    
    Modules.objects.filter(id=instance.id).update(
        module=data["module"],
        name=data["name"],
        version=data["version"],
        developer=data["developer"],
        date=data["date"],
        contact=data["contact"],
        description=data["description"],
        category=data["category"],
        dependencies=json.dumps(data["dependencies"]),
        data_dependencies=json.dumps(data["data_dependencies"]),
        data_generated=json.dumps(data["data_generated"]),
        submodules=json.dumps(data["submodules"])
    )
    __reorganize_modules()
    create_stored_procedures(path_to_extrat)


def __unzip(file_name):
        # Create a ZipFile Object and load sample.zip in it
    with ZipFile(os.path.join(settings.MEDIA_ROOT, str(file_name)), 'r') as zipObj:
            # Extract all the contents of zip file in indicators directory
        __path_to_extract = os.path.realpath(os.path.join(
            os.path.dirname(__file__), "..", "plup", "indicators", str(file_name)[:-4]))
        #delete directory if exists
        if os.path.isdir(__path_to_extract):
            shutil.rmtree(__path_to_extract)
        zipObj.extractall(__path_to_extract)
    return __path_to_extract


def __register_module(path):
    with open(os.path.join(path, "config.json")) as json_file:
        data = json.load(json_file)
        return data


def __reorganize_modules():
    result = list(Modules.objects.values('module', 'dependencies'))
    end_elems = list()
    for i in range(0, len(result)):
        result[i]["dependencies"] = json.loads(result[i]["dependencies"])
        if result[i]["module"] == "ModuleVoronoi" or result[i]["module"] == "ModuleDataOrigin":
            end_elems.append(i)
    for i in end_elems:
        result.append(result.pop(result.index(i)))
    install_plugins(result)


def install_plugins(dep_modules):
    processed = []
    # Reset all modules order to -1
    Modules.objects.all().update(order=-1)
    for module in dep_modules:
        for dependency in module["dependencies"]:
            insert_module(module["module"], dependency, dep_modules, processed)
        insert_module(module["module"], 'None', dep_modules, processed)


def insert_module(module, dependency, dependencies, processed):
    if(dependency == 'None') and module not in processed:
        processed.append(module)
        results = list(Modules.objects.filter(
            order__gte=0).aggregate(Max('order')).values())
        if results[0] == None:
            Modules.objects.filter(module=module).update(
                order=0)
        else:
            Modules.objects.filter(module=module).update(
                order=results[0]+1)
        return
    else:
        for i in dependencies:
            if i["module"] == dependency:
                for j in i["dependencies"]:
                    insert_module(i["module"], j, dependencies, processed)
                insert_module(i["module"], 'None', dependencies, processed)


def create_stored_procedures(path_to_extrat):
    stored_proc = glob.glob(os.path.join(path_to_extrat, "*.sql"))
    for s_file in stored_proc:
        #print("stored_proc",stored_proc)
        sql_statement = open(s_file).read()
        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
