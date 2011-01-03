import csv
from quality.models import *
from django.template.defaultfilters import slugify

csvfile = open('/home/michael/src/wb_data/WDI_GDF_Series.csv')
try:
    data = csv.DictReader(csvfile)
    print "CSV opened..."
except:
    print "---------->Error opening CSV"

#Object counter for sanity checking
elements_created = 0
error_count = 0

while data:
    line = data.next()
    try: 
        s=Series(
            code=unicode(line['Series Code'], 'iso-8859-1'), \
            name=unicode(line['Series Name'], 'iso-8859-1'), \
            topic=unicode(line['Topic'], 'iso-8859-1'), \
            short_def=unicode(line['Short definition'], 'iso-8859-1'), \
            source=unicode(line['Source'], 'iso-8859-1'), \
            WDI=unicode(line['WDI'], 'iso-8859-1'), \
            GDF=unicode(line['GDF'], 'iso-8859-1'), \
            sub1_name=unicode(line['SubTopic1'], 'iso-8859-1'), \
            sub2_name=unicode(line['SubTopic2'], 'iso-8859-1'), \
            sub3_name=unicode(line['SubTopic3'], 'iso-8859-1'), \
        )
    except:
        print "---------->Error importing with %s elements created." % \
            (elements_created)
        eror_count += 1
    s.code_slug=slugify(s.code)
    s.topic_slug=slugify(s.topic)
    s.sub1_slug=slugify(s.sub1_name)
    s.sub2_slug=slugify(s.sub2_name)
    s.sub3_slug=slugify(s.sub3_name)
    s.save()
    elements_created += 1
    print "%s saved, %s elements created." % (s.name, elements_created)
    print "% errors so far" % error_count
