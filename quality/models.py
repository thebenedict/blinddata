from django.db import models
from django.conf import settings

class Country(models.Model):
    REGION_CHOICES = (
        ('aggregates', "Aggregates"),
        ('east_asia_pac', "East Asia & Pacific"),
        ('eur_central_asia', "Europe & Central Asia"),
        ('lac', "Latin America & Caribbean"),
        ('mena', "Middle East & North Africa"),
        ('n_amer', "North America"),
        ('s_asia', "South Asia"),
        ('ssa', "Sub-Saharan Africa"),
    )
    
    INCOME_CHOICES = (
        ('aggregates', "Aggregates"),
        ('high_non_oecd', "High income: nonOECD"),
        ('high_oecd', "High income: OECD"),
        ('upper_middle', "Upper middle income"),
        ('lower_middle', "Lower middle income"),
        ('low', "Low income"),
    )
    
    prepopulated_fields = {"region_slug": ("region",),
                           "income_group_slug": ("income_group",)}
    
    code = models.CharField(max_length=3, unique=True)
    alpha2_code = models.CharField(max_length=2, blank=True, null=True)
    short_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=100)
    region = models.CharField(max_length=26)
    region_slug = models.SlugField()
    income_group = models.CharField(max_length=20)
    income_group_slug = models.SlugField()

    def __unicode__(self):
        return self.code
        
class Series(models.Model):
    code = models.CharField(max_length=25, unique = True)
    code_slug = models.SlugField()
    name = models.CharField(max_length=150)
    topic = models.CharField(max_length=50)
    topic_slug = models.SlugField()
    short_def = models.TextField()
    source = models.TextField()
    WDI = models.BooleanField()
    GDF = models.BooleanField()
    sub1_name = models.CharField(max_length=50)
    sub1_slug = models.SlugField()
    sub2_name = models.CharField(max_length=50, blank=True, null=True)
    sub2_slug = models.SlugField()
    sub3_name = models.CharField(max_length=50, blank=True, null=True)
    sub3_slug = models.SlugField()
    
    def __unicode__(self):
        return self.code

    @staticmethod
    def name_from_code_slug(self, code_slug):
        return Series.objects.get(code_slug = code_slug).name
        
class Element(models.Model):
    country = models.ForeignKey(Country, related_name='countries')
    series = models.ForeignKey(Series, related_name='series')
    year = models.IntegerField(max_length=4)
    value = models.FloatField()
    
    def __unicode__(self):
        return "%s:%s:%s" % (self.country.code, self.series.code, self.year)
