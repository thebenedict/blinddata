from django.db import models
from django.conf import settings

class Country(models.Model):
#    REGION_CHOICES = (
#        ('aggregates', "Aggregates"),
#        ('east_asia_pac', "East Asia & Pacific"),
#        ('eur_central_asia', "Europe & Central Asia"),
#        ('latin_am_car', "Latin America & Caribbean"),
#        ('mena', "Middle East & North Africa"),
#        ('n_amer', "North America"),
#        ('s_asia', "South Asia"),
#        ('ssa', "Sub-Saharan Africa"),
#    )
#    
#    INCOME_CHOICES = (
#        ('aggregates', "Aggregates"),
#        ('high_non_oecd', "High income: nonOECD"),
#        ('high_oecd', "High income: OECD"),
#        ('upper_middle', "Upper middle income"),
#        ('lower_middle', "Lower middle income"),
#        ('low', "Low income"),
#    )
#    
#    LENDING_CHOICES = (
#        ('aggregates', "Aggregates"),
#        ('blend', "Blend"),
#        ('ibrd', "IBRD"),
#        ('ida', "IDA"),
#        ('not_classified', "Not classified"),
#    )
    
    code = models.CharField(max_length=3, unique=True)
    alpha2_code = models.CharField(max_length=3, blank=True, null=True)
    name = models.CharField(max_length=100)
    #region = models.CharField(max_length=20, choices=REGION_CHOICES)
    #income_group = models.CharField(max_length=15, choices=INCOME_CHOICES)
    #lending_category = models.CharField(max_length=10, choices=INCOME_CHOICES)
    region = models.CharField(max_length=30)
    income_group = models.CharField(max_length=25)
    lending_category = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.code
        
class Series(models.Model):
    code = models.CharField(max_length=25, unique = True)
    name = models.CharField(max_length=150)
    topic = models.CharField(max_length=50)
    sub1 = models.CharField(max_length=50)
    sub2 = models.CharField(max_length=50, blank=True, null=True)
    sub3 = models.CharField(max_length=50, blank=True, null=True)
    
    def __unicode__(self):
        return self.code
        
class Element(models.Model):
    country = models.ForeignKey(Country, related_name='countries')
    series = models.ForeignKey(Series, related_name='series')
    year = models.IntegerField(max_length=4)
    value = models.FloatField()
    
    def __unicode__(self):
        return "%s:%s:%s" % (self.country.code, self.series.code, self.year)