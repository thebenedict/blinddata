import csv
from quality.models import *
from django.template.defaultfilters import slugify

csvfile = open('/home/michael/src/wb_data/WDI_GDF_Country.csv')
try:
    data = csv.DictReader(csvfile)
    print "CSV opened..."
except:
    print "---------->Error opening CSV"

#Object counter for sanity checking
elements_created = 0

while data:
    line = data.next()
    try: 
        c=Country(
            code=unicode(line['Country Code'], 'iso-8859-1'), \
            alpha2_code=unicode(line['WB-2 code'], 'iso-8859-1'), \
            short_name=unicode(line['Short Name'], 'iso-8859-1'), \
            long_name=unicode(line['Long Name'], 'iso-8859-1'), \
            region=unicode(line['Region'], 'iso-8859-1'), \
            income_group=unicode(line['Income Group'], 'iso-8859-1') 
        )
    except:
        print "---------->Error importing with %s elements created." % \
            (elements_created)
    c.region_slug=slugify(c.region)
    c.income_group_slug=slugify(c.income_group)
    c.save()
    elements_created += 1
    print "%s saved, %s elements created." % (c.short_name, elements_created)
