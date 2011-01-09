from blinddata.quality.models import Country, Series, Element, CachedCount
from django.contrib import admin

admin.site.register(Country)
admin.site.register(Series)
admin.site.register(Element)
admin.site.register(CachedCount)

class CountryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"region_slug": ("region",),
                           "income_group_slug": ("income_group",)}
