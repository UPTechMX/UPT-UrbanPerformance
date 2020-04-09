from django.contrib import admin
from plup.models import scenario, risk, risk_info, roads, roads_info
from plup.models import Amenities, Amenities_info, transit, transit_info, mmu
from plup.models import mmu_info, jobs, jobs_info, footprint, assumptions, Results
from plup.models import Modules
# Register your models here.

admin.site.register(scenario)
admin.site.register(risk)
admin.site.register(risk_info)
admin.site.register(roads)
admin.site.register(roads_info)
admin.site.register(Amenities)
admin.site.register(Amenities_info)
admin.site.register(transit)
admin.site.register(transit_info)
admin.site.register(mmu)
admin.site.register(mmu_info)
admin.site.register(jobs)
admin.site.register(jobs_info)
admin.site.register(footprint)
admin.site.register(assumptions)
admin.site.register(Results)
admin.site.register(Modules)
