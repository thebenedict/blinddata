import csv
from quality.models import *
csvfile = open('/home/michael/src/wb_data/WDI_GDF_Data.csv')

data = csv.DictReader(csvfile)
ln = 1
elements_created = 0
elements_confirmed = 0
while data:
    line=data.next()
    if ln % 2500 == 0:
        print "At line %s, %s elements created, %s elements confirmed" % (ln, elements_created, elements_confirmed)
    try:
        #amazingly, at least one country code (ven) is lowercase in the raw data
        #see 'ven' line 14363
        c = Country.objects.get(code=line['Country Code'].upper())
    except:
        print "***Error in line %s, country code %s not found.***" % (ln, line['Country Code'])
    try:    
        #For some reason there is white space after a small number of series codes
        #in the raw data -- strip it!
        #There are also a few with lowercase characters
        s = Series.objects.get(code=line['Series Code'].strip().upper())
    except:
        print "***Error in line %s, series code %s not found.***" % (ln, line['Series Code'])
    
    if s is not None and c is not None:
        for y in range (1960, 2010):
            v = line[str(y)]
            if v:
                e = Element(country=c, series=s, year=y, value=v)
                e.save()
                elements_created += 1
                #modification if script fails the first time
                #try:
                #    e = Element.objects.get(country=c, series=s, year=y, value =v)
                #    elements_confirmed += 1
                #except:
                #    e = Element(country=c, series=s, year=y, value=v)
                #    print "creating element with c: %s, s: %s, y: %s, v: %s" % (c,s,y,v)
                #    e.save()
                #    elements_created += 1
    else:
        print "Skipping elements due to error! Series is %s, Country is %s" % \
            (s, c) 
    ln += 1
    s = None
    c = None
    
