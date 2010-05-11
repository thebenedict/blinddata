from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.core.cache import cache
from django.db.models import Count
from quality.models import *


ONE_YEAR = 31536000

def index(request, safe_topic = None, safe_subtopic = None, safe_series = None):
    print ("In index")
    #generate URL safe names - it would probably be better to store these in the database
    topic = lookup_safe_name(safe_topic, 'topic')
    subtopic = lookup_safe_name(safe_subtopic, 'subtopic')
    series = lookup_safe_name(safe_series, 'series')
    
    #generate the table or fetch from cache
    safe_name_list = [safe_topic, safe_subtopic, safe_series]
    table_cache_key = '_'.join(s for s in safe_name_list if s is not None) + '_table'
    table_data = cache.get(table_cache_key)
    if table_data is None:
        print("Generating cache for %s.") % table_cache_key
        table_data = get_table_data(topic, subtopic, series)
        cache.set(table_cache_key, table_data, ONE_YEAR)
    
    #generate the map or fetch from cache    
    map_cache_key = '_'.join(s for s in safe_name_list if s is not None) + '_map'
    map_data = cache.get(map_cache_key)
    if map_data is None:
        print("Generating cache for %s.") % map_cache_key
        map_data = get_map_data(topic, subtopic, series)
        cache.set(map_cache_key, map_data, ONE_YEAR)
    
    #return a page with the correct template
    if series is not None:
        return render_to_response('quality/series_detail.html', {"table_data": table_data, "map_data": map_data})
    elif subtopic is not None:
        return render_to_response('quality/subtopic_detail.html', {"table_data": table_data, "map_data": map_data})
    elif topic is not None:
        return render_to_response('quality/topic_detail.html', {"table_data": table_data, "map_data": map_data})
    else:
        return render_to_response('quality/index.html', {"table_data": table_data, "map_data": map_data})

def get_map_data(topic = None, subtopic = None, series = None):
    map_data=[]
    countries = Country.objects.all()
    if series is not None:
        elements = Element.objects.filter(series__name = series)
    elif subtopic is not None:
        elements = Element.objects.filter(series__sub1 = subtopic) \
        | Element.objects.filter(series__sub2 = subtopic) \
        | Element.objects.filter(series__sub3 = subtopic)
    elif topic is not None:
        elements = Element.objects.filter(series__topic = topic)
    else:
        elements = Element.objects.all()
    
    mycountries = dict((c.alpha2_code, c.name) for c in countries if c.alpha2_code)

    #this is fast
    for elem in elements.values('country__alpha2_code').annotate(count = Count('pk')).filter(country__alpha2_code__in = mycountries.keys()):
        map_data.append((mycountries[elem['country__alpha2_code']], elem['country__alpha2_code'], elem['count']))
    
    #a slow way to do the same thing:
    #for c in countries:
    #   if c.alpha2_code:
    #        print("Filtering %s elements for %s" % (elements.count(), c.name))
    #        count = elements.filter(country__alpha2_code = c.alpha2_code).count()
    #        map_data.append((c.name, c.alpha2_code, count))
    return map_data
    
def get_table_data(topic = None, subtopic = None, series = None):
    if series is not None:
        table_data = get_series_detail(topic, subtopic, series)
    elif subtopic is not None:
        table_data = get_subtopic_table(topic, subtopic)
    elif topic is not None:
        table_data = get_topic_table(topic)
    else:
        table_data = get_summary_table()
    return table_data

def get_summary_table():
    table_data = []
    topics = cache.get("distinct_topics")
    if topics is None:
        topics = Series.objects.values('topic').distinct()
        cache.set("distinct_topics", topics, ONE_YEAR)
        print "I'm hitting the DB for distinct topics"
    else:
        print "I used cache for distinct topics"
    for t in topics:
        topic_name = t['topic']
        # create a machine readable 'safe' name to use in the detail url
        safe_topic_name = make_safe_name(topic_name)
        elements = Element.objects.filter(series__topic = topic_name)
        num_series = Series.objects.filter(topic = topic_name).count()
        num_datapoints = elements.count()
        ave_datapoints = num_datapoints / num_series
        data_count = 0 # should end up the same as num_datapoints as a check?
        count_list = []
        for y in range (1960, 2010):
             e = cache.get("".join([topic_name, "_", str(y)]))
             if e is None:
                 #we don't have the query cached, so run and cache the result
                 print "I'm hitting the DB for year count: %s - %s" % (topic_name, y)
                 e = elements.filter(year = y)
                 cache.set("".join([topic_name, "_", str(y)]), e, ONE_YEAR)
             else:
                 print "I used cache for year count: %s - %s" % (topic_name, y)
             num = e.count()
             count_list.append(num)
             #data_count += num
        topic_dict = {"topic_name": topic_name, \
                      "safe_topic_name": safe_topic_name, \
                      "num_series": num_series, \
                      "num_datapoints": num_datapoints, \
                      "ave_datapoints": ave_datapoints, \
                      #"data_count": data_count, \
                      "count_list": count_list, \
                      "count_min": min(count_list), \
                      "count_max": max(count_list)}
        table_data.append(topic_dict)
    return table_data

def get_topic_table(topic):
    table_data = []
    safe_topic_name = make_safe_name(topic)
    topic_elements = Element.objects.filter(series__topic = topic)
    print "I'm hitting the DB for distinct subtopics"
    subtopics = list(topic_elements.values('series__sub1').distinct()) \
    + list(topic_elements.values('series__sub2').distinct()) \
    + list(topic_elements.values('series__sub3').distinct())
    
    for subtopic in subtopics:
        #ugh, I have no idea how to properly check for/remove blank values.
        if subtopic.values()[0] is not unicode(''):
            subtopic_name = subtopic.values()[0]
            safe_subtopic_name = make_safe_name(subtopic_name)
            elements = topic_elements.filter(series__sub1 = subtopic_name) \
            | topic_elements.filter (series__sub2 = subtopic_name) \
            | topic_elements.filter (series__sub3 = subtopic_name)
            
            series = Series.objects.filter(sub1 = subtopic_name) \
            | Series.objects.filter(sub2 = subtopic_name) \
            | Series.objects.filter(sub3 = subtopic_name)
            
            num_series = series.count()
            num_datapoints = elements.count()
            ave_datapoints = num_datapoints / num_series
            data_count = 0 # should end up the same as num_datapoints as a check?
            count_list = []
            for y in range (1960, 2010):
                 #we don't have the query cached, so run and cache the result
                 print "I'm hitting the DB for year count: %s - %s" % (subtopic_name, y)
                 e = elements.filter(year = y)
                 num = e.count()
                 count_list.append(num)
            subtopic_dict = {"topic_name": topic, \
                             "subtopic_name": subtopic_name, \
                             "safe_topic_name": safe_topic_name, \
                             "safe_subtopic_name": safe_subtopic_name, \
                             "num_series": num_series, \
                             "num_datapoints": num_datapoints, \
                             "ave_datapoints": ave_datapoints, \
                             "count_list": count_list, \
                             "count_min": min(count_list), \
                             "count_max": max(count_list)}
            table_data.append(subtopic_dict)
    return table_data
    
def get_subtopic_table(topic, subtopic):
    table_data = []
    safe_topic_name = make_safe_name(topic)
    safe_subtopic_name = make_safe_name(subtopic)
    subtopic_series = Series.objects.filter(sub1 = subtopic) \
    | Series.objects.filter (sub2 = subtopic) \
    | Series.objects.filter (sub3 = subtopic)
    print "I'm hitting the DB for distinct series for subtopic %s" % subtopic
    for series in subtopic_series:
        series_name = series.name
        safe_series_name = make_safe_name(series_name)
        series_elements = Element.objects.filter(series__name = series_name)
           
        num_datapoints = series_elements.count()
        data_count = 0 # should end up the same as num_datapoints as a check?
        count_list = []
        
        #for y in range (1960, 2010):
        #     #we don't have the query cached, so run and cache the result
        #     print "I'm hitting the DB for year count: %s - %s" % (series_name, y)
        #     e = series_elements.filter(year = y)
        #     num = e.count()
        #     count_list.append(num)
        
        counted_list = list(series_elements.values('year').annotate(count = Count('pk')).order_by('year'))		
        #years without data are missing from the list but we want them as zero in the spark line, so now add them back in.
        for c in counted_list:
            if counted_list.index(c) != len(counted_list) - 1 and c['year'] != 2009:                     
                if c['year'] + 1 != counted_list[counted_list.index(c) + 1]['year']:
                    counted_list.insert(counted_list.index(c) + 1, {'count': 0, 'year': c['year'] + 1})
            else:
                if  c['year'] != 2009:
                    for yr in range(c['year'] + 1, 2010):
                        counted_list.append({'count': 0, 'year': long(yr)})    
        for c in counted_list:
            count_list.append(c['count'])        
        
        topic_dict = {"topic_name": topic, \
                      "subtopic_name": subtopic, \
                      "series_name": series_name, \
                      "safe_topic_name": safe_topic_name, \
                      "safe_subtopic_name": safe_subtopic_name, \
                      "safe_series_name": safe_series_name, \
                      "num_datapoints": num_datapoints, \
                      "count_list": count_list, \
                      "count_min": min(count_list), \
                      "count_max": max(count_list)}
        table_data.append(topic_dict)
    return table_data

def get_series_detail(topic, subtopic, series):
    table_data = []
    safe_topic_name = make_safe_name(topic)
    safe_subtopic_name = make_safe_name(subtopic)
    safe_series_name = make_safe_name(series)
    print "I'm hitting the DB for distinct elements for series %s" % series    
    series_elements = Element.objects.filter(series__name = series)
    num_datapoints = series_elements.count()
    count_list = []
    
    #method 1 -- slow!
    #for y in range (1960, 2010):
        #print "doing year count: %s - %s" % (series, y)
        #e = series_elements.filter(year = y)
        #num = e.count()
        #count_list.append(num)
    
    #method 2 -- slightly faster if at all
    #counted = series_elements.values('year').annotate(count = Count('pk'))
    #for y in range (1960, 2010):
    #    print "doing year count for %s - %s" % (series, y)
    #    try:
    #        count_list.append(counted.values().get(year = y)['count'])
    #    except:
    #        count_list.append(0)
    
    #yes!
    counted_list = list(series_elements.values('year').annotate(count = Count('pk')).order_by('year'))		
    #years without data are missing from the list but we want them as zero in the spark line, so now add them back in.
    for c in counted_list:
        if counted_list.index(c) != len(counted_list) - 1 and c['year'] != 2009:                     
            if c['year'] + 1 != counted_list[counted_list.index(c) + 1]['year']:
                counted_list.insert(counted_list.index(c) + 1, {'count': 0, 'year': c['year'] + 1})
        else:
            if  c['year'] != 2009:
                for yr in range(c['year'] + 1, 2010):
                    counted_list.append({'count': 0, 'year': long(yr)})    
    for c in counted_list:
        count_list.append(c['count'])    
    
    series_dict = {"topic_name": topic, \
                  "subtopic_name": subtopic, \
                  "series_name": series, \
                  "safe_topic_name": safe_topic_name, \
                  "safe_subtopic_name": safe_subtopic_name, \
                  "safe_series_name": safe_series_name, \
                  "num_datapoints": num_datapoints, \
                  "count_list": count_list, \
                  "count_min": min(count_list), \
                  "count_max": max(count_list)}
    table_data.append(series_dict)
    return table_data
    
def lookup_safe_name(safe_name, lookup_type = None):
    if lookup_type is None:
        return None
    if lookup_type == 'topic':
        for series in Series.objects.all():
            sn = make_safe_name(series.topic)
            if sn == safe_name:
                return series.topic
    if lookup_type == 'subtopic':
        for series in Series.objects.all():
            sn1 = make_safe_name(series.sub1)
            if sn1 == safe_name:
                return series.sub1
            sn2 = make_safe_name(series.sub2)
            if sn2 == safe_name:
                return series.sub2
            sn3 = make_safe_name(series.sub3)
            if sn3 == safe_name:
                return series.sub3
    if lookup_type == 'series':
        for series in Series.objects.all():
            sn = make_safe_name(series.name)
            if sn == safe_name:
                return series.name
    else:
        return None
        
def make_safe_name(name):
    return ''.join(c.lower() for c in name if c.isalpha())

def crawl(request):
    #Crawl the whole site to generate cache. This is a 'run overnight' sort of thing.
    topics_list = []
    topics = Series.objects.values('topic').distinct()
    for t in topics:
        print("generating topics list")
        topics_list.append([t['topic'], make_safe_name(t['topic'])])
	for topic_name, topic_safe_name in topics_list:
		print("requesting page for %s" % topic_safe_name)
		page = index(request, topic_safe_name)
		print("filtering series for topic %s" % topic_safe_name)
		topic_series = Series.objects.filter(topic = topic_name)
		#would be much cleaner if subtopics were a many to many relationship
		subtopics = list (topic_series.values('sub1').distinct()) \
		+ list(topic_series.values('sub2').distinct()) \
		+ list(topic_series.values('sub3').distinct())
		subtopics_list = []
		for sub in subtopics:
			print("Generating subtopics list for %s") % sub
			if 'sub1' in sub and sub.values()[0] is not unicode(''):
				subtopics_list.append([sub['sub1'], make_safe_name(sub['sub1'])])
			if 'sub2' in sub and sub.values()[0] is not unicode(''):
				subtopics_list.append([sub['sub2'], make_safe_name(sub['sub2'])])
			if 'sub3' in sub and sub.values()[0] is not unicode(''):
				subtopics_list.append([sub['sub3'], make_safe_name(sub['sub3'])])
			subtopic_count = len(subtopics_list)
		for sub_name, sub_safe_name in subtopics_list:
			print("%s subtopics remaining for %s" % (subtopic_count, topic_safe_name))               
			print("requesting page for %s/%s" % (topic_safe_name, sub_safe_name))
			page = index(request, topic_safe_name, sub_safe_name)
			print("filtering series for subtopic %s" % sub_safe_name)
			subtopic_series = Series.objects.filter(sub1 = sub_name) \
			| Series.objects.filter(sub2 = sub_name) \
			| Series.objects.filter(sub3 = sub_name)
			#counter to monitor progress
			series_count = subtopic_series.count()
			for ss in subtopic_series:
				print("%s series remaining for %s/%s" % (series_count, topic_safe_name, sub_safe_name))
				print("requesting page for %s/%s/%s" % (topic_safe_name, sub_safe_name, make_safe_name(ss.name)))
				page = index(request, topic_safe_name, sub_safe_name, make_safe_name(ss.name))
				series_count -= 1
			subtopic_count -=1
    return HttpResponse("Generated Cache")

        


