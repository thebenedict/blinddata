from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.db.models import Count, Max, Min, Q
from blinddata.forms import SessionSettingsForm
from quality.models import Country, Series, Element
import operator


ONE_YEAR = 31536000 #seconds
#total number of years the data set covers
#TODO cache this
endpoints = Element.objects.aggregate(Max('year'), Min('year'))
NUM_YEARS = endpoints['year__max']-endpoints['year__min']+1
NUM_COUNTRIES = Country.objects.exclude(region_slug='aggregates').count()

def index(request):
    if request.method == 'POST':
        form = SessionSettingsForm(request.POST)
        if form.is_valid():
            request.session['start_year'] = form.cleaned_data['start_year']
            request.session['end_year'] = form.cleaned_data['end_year']
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        form = SessionSettingsForm()

    query = get_query(request)

    print "cache key is %s" % query['cache_key']


    print "Calling get_overview_table"
    overview_table = get_overview_table(query)
    map_data = cache.get(query['cache_key'] + '_' + query['start_year'] + '_' + query['end_year'] + '_map')
    if map_data is None:
        print "Calling get_map_data"
        map_data = get_map_data(query)
    
    return render_to_response('quality/index.html', {"table": overview_table, "map_data": map_data, "session_settings_form": form})

def topic_detail(request, topic_slug):
    if request.method == 'POST':
        form = SessionSettingsForm(request.POST)
        if form.is_valid():
            request.session['start_year'] = form.cleaned_data['start_year']
            request.session['end_year'] = form.cleaned_data['end_year']
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        form = SessionSettingsForm()

    query = get_query(request, topic_slug)

    print "cache key is %s" % query['cache_key']

    #topic_table = cache.get(query['cache_key'] + "_table")
    #if topic_table is None:
    print "Calling get_topic_table"
    topic_table = get_topic_table(query)
    map_data = cache.get(query['cache_key'] + '_' + query['start_year'] + '_' + query['end_year'] + '_map')
    if map_data is None:
        print "Calling get_map_data"
        map_data = get_map_data(query)
    
    return render_to_response('quality/topic_detail.html', {"table": topic_table, "map_data": map_data, "session_settings_form": form})

def subtopic_detail(request, topic_slug, subtopic_slug):
    if request.method == 'POST':
        form = SessionSettingsForm(request.POST)
        if form.is_valid():
            request.session['start_year'] = form.cleaned_data['start_year']
            request.session['end_year'] = form.cleaned_data['end_year']
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        form = SessionSettingsForm()

    query = get_query(request, topic_slug, subtopic_slug)

    print "cache key is %s" % query['cache_key']

    print "Calling get_subtopic_table"
    subtopic_table = get_subtopic_table(query)
    map_data = cache.get(query['cache_key'] + '_' + query['start_year'] + '_' + query['end_year'] + '_map')
    if map_data is None:
        print "Calling get_map_data"
        map_data = get_map_data(query)
    
    return render_to_response('quality/subtopic_detail.html', {"table": subtopic_table, "map_data": map_data, "session_settings_form": form})

def series_detail(request, topic_slug, subtopic_slug, series_code_slug):
    if request.method == 'POST':
        form = SessionSettingsForm(request.POST)
        if form.is_valid():
            request.session['start_year'] = form.cleaned_data['start_year']
            request.session['end_year'] = form.cleaned_data['end_year']
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        form = SessionSettingsForm()

    query = get_query(request, topic_slug, subtopic_slug, series_code_slug)

    print "cache key is %s" % query['cache_key']

    print "Calling get_series_row_table"
    series_row = get_series_row(query)
    map_data = cache.get(query['cache_key'] + '_' + query['start_year'] + '_' + query['end_year'] + '_map')
    if map_data is None:
        print "Calling get_map_data"
        map_data = get_map_data(query)
    
    return render_to_response('quality/series_detail.html', {"series_row": series_row, "map_data": map_data, "session_settings_form": form})

def get_map_data(query):
    map_data=[]

    country_dict = dict((c.alpha2_code, c.short_name) for c in query['countries'] if c.alpha2_code)

    for e in query['elements_by_country']:
        for elem in e['elements'].values('country__alpha2_code').annotate(count = Count('pk')).filter(country__alpha2_code__in = country_dict.keys()):
            map_data.append((country_dict[elem['country__alpha2_code']], elem['country__alpha2_code'], elem['count']))

    cache.set(query['cache_key'] + '_' + query['start_year'] + '_' + query['end_year'] + '_map', map_data, ONE_YEAR)
    return map_data

def get_overview_table(query):
    table_data = []
    topics = Series.objects.values('topic', 'topic_slug').distinct()
    for t in topics:
        num_series = Series.objects.filter(topic_slug = t['topic_slug']).count()
        country_topic_data = []
        for e in query['elements_by_country']:
            country_topic_elements = e['elements'].filter(series__topic_slug = t['topic_slug'])
            num_datapoints = country_topic_elements.count()
            if e['code'] == '':
                num_countries = query['countries'].count()
            else:
                num_countries = 1

            ###DEBUGGING###
            print "------------>Topic: %s for %s" % (t['topic'], e['code'])
            print "num_series: %s" % num_series
            print "num_datapoints: %s" % num_datapoints
            print "num_countries: %s" % num_countries
            print "query['num_years']: %s" % query['num_years']

            percent_complete = int(round(float(num_datapoints) / float(num_series * num_countries * query['num_years']) * 100))

            
            country_topic_dict = {"country_code": e['code'], \
                                  "elements": country_topic_elements, \
                                  "num_datapoints": num_datapoints, \
                                  "percent_complete": percent_complete, \
                                  "plot_series": get_plot_series(country_topic_elements, query['start_year'], query['end_year'], e['code'], t['topic_slug'])}

            country_topic_data.append(country_topic_dict)
        plot_parameters = get_plot_parameters(country_topic_data, query['start_year'], query['end_year'])
        row_dict = {"country_topic_data": country_topic_data, \
                     "topic_name": t['topic'], \
                     "topic_slug": t['topic_slug'], \
                     "num_series": num_series, \
                     "plot_parameters": plot_parameters}
        table_data.append(row_dict)
    overview_table = {'start_year': query['start_year'],
                      'end_year': query['end_year'],
                      'table_data': table_data}
    return overview_table

def get_topic_table(query):
    table_data = []
    subtopic_list = []
    print "starting ones twos threes"
    ones = query['elements'].values_list('series__sub1_name', 'series__sub1_slug').distinct()
    twos = query['elements'].values_list('series__sub2_name', 'series__sub2_slug').distinct()
    threes = query['elements'].values_list('series__sub3_name', 'series__sub3_slug').distinct()
    for num in [ones, twos, threes]:
        for name, slug in num:
            if name != '':
                subtopic_list.append({'name': name, 'slug': slug})
    print "ending ones twos threes"
 
    print "subtopic_list is %s" % subtopic_list
    print "%s rows to calculate" % len(subtopic_list)
    for s in subtopic_list:
        print "point x" 
        num_series = (Series.objects.filter(Q(sub1_slug = s['slug']) | \
                                            Q(sub2_slug = s['slug']) | \
                                            Q(sub3_slug = s['slug']))).count()
        print "point y"
        print "Calculating table data for subtopic %s" % s['name']
        country_subtopic_data = []
        for e in query['elements_by_country']:
            country_subtopic_elements = e['elements'].filter(series__sub1_slug = s['slug']) | \
                                        e['elements'].filter(series__sub2_slug = s['slug']) | \
                                        e['elements'].filter(series__sub3_slug = s['slug'])
            
            plot_series = get_plot_series(country_subtopic_elements, query['start_year'], query['end_year'], e['code'],s['slug'])
            print "-->e['code'] is: %s" % e['code']
            num_datapoints = sum(s['count'] for s in plot_series)
            print "-->num_datapoints is: %s" % num_datapoints
            if e['code'] == '': #all countries
                num_countries = query['countries'].count()
            else:
                num_countries = 1

            percent_complete = int(round(float(num_datapoints) / float(num_series * num_countries * query['num_years']) * 100))
            print "|--->point a"
            country_subtopic_dict = {"country_code": e['code'], \
                                     "elements": country_subtopic_elements, \
                                     "num_datapoints": num_datapoints, \
                                     "percent_complete": percent_complete, \
                                     "plot_series": plot_series}
            country_subtopic_data.append(country_subtopic_dict)
            print "|--->point b"
            plot_parameters = get_plot_parameters(country_subtopic_data, query['start_year'], query['end_year'])
            print "|--->point c"
        row_dict = {"country_subtopic_data": country_subtopic_data, \
                    "subtopic_name": s['name'], \
                    "subtopic_slug": s['slug'], \
                    "num_series": num_series, \
                    "plot_parameters": plot_parameters}
        table_data.append(row_dict)
        print "|--->point d"
    topic_table = {'start_year': query['start_year'],
                   'end_year': query['end_year'],
                   'topic': query['topic'],
                   'topic_slug': query['topic_slug'],
                   'table_data': table_data}
    return topic_table

def get_subtopic_table(query):
    table_data = []
    subtopic_series = Series.objects.filter(sub1_name = query['subtopic']) | \
                      Series.objects.filter(sub2_name = query['subtopic']) | \
                      Series.objects.filter(sub3_name = query['subtopic'])
    
    for s in subtopic_series:
        print "Calculating table data for series %s" % s.name
        country_series_data = []
        for e in query['elements_by_country']:
            country_series_elements = e['elements'].filter(series__code = s.code)
            num_datapoints = country_series_elements.count()
            if e['code'] == '':
                num_countries = query['countries'].count()
            else:
                num_countries = 1

            percent_complete = int(round(float(num_datapoints) / float(num_countries * query['num_years']) * 100))

             ###DEBUGGING###
            print "------------>series: %s" % s.name
            print "num_datapoints: %s" % num_datapoints
            print "num_countries: %s" % num_countries
            print "query['num_years']: %s" % query['num_years']

            country_series_dict = {"country_code": e['code'], \
                                   "elements": country_series_elements, \
                                   "num_datapoints": num_datapoints, \
                                   "percent_complete": percent_complete, \
                                   "plot_series": get_plot_series(country_series_elements, query['start_year'], query['end_year'], e['code'], s.code_slug)}
            country_series_data.append(country_series_dict)

        plot_parameters = get_plot_parameters(country_series_data, query['start_year'], query['end_year'])
        row_dict = {"country_series_data": country_series_data, \
                    "series_name": s.name, \
                    "code_slug": s.code_slug, \
                    "plot_parameters": plot_parameters}

        table_data.append(row_dict)

    subtopic_table = {'start_year': query['start_year'],
                      'end_year': query['end_year'],
                      'topic': query['topic'],
                      'topic_slug': query['topic_slug'],
                      'subtopic': query['subtopic'],
                      'subtopic_slug': query['subtopic_slug'],
                      'table_data': table_data}
    return subtopic_table

def get_series_row(query):
    row_data = []
    series = Series.objects.get(code_slug = query['series_code_slug'])
    print "Calculating row data for series %s" % series.name
    country_data = []
    for e in query ['elements_by_country']:
        country_elements = e['elements']
        num_datapoints = country_elements.count()
        if e['code'] == '':
            num_countries = query['countries'].count()
        else:
            num_countries = 1
        percent_complete = int(round(float(num_datapoints) / float(num_countries * query['num_years']) * 100))

        country_dict = {"country_code": e['code'], \
                        "elements": country_elements, \
                        "num_datapoints": num_datapoints, \
                        "percent_complete": percent_complete, \
                        "plot_series": get_plot_series(country_elements, query['start_year'], query['end_year'], e['code'], series.code_slug)}
        country_data.append(country_dict)

    plot_parameters = get_plot_parameters(country_data, query['start_year'], query['end_year'])
    
                       
    ###DEBUGGING###
    print "------------>series: %s" % series.name
    print "num_datapoints: %s" % num_datapoints
    print "num_countries: %s" % num_countries
    print "query['num_years']: %s" % query['num_years']

    series_row = {'start_year': query['start_year'],
                  'end_year': query['end_year'],
                  'topic': query['topic'],
                  'topic_slug': query['topic_slug'],
                  'subtopic': query['subtopic'],
                  'subtopic_slug': query['subtopic_slug'],
                  'series_name': query['series_name'],
                  'series_code': query['series_code'],
                  'series_code_slug': query['series_code_slug'],
                  'plot_parameters': plot_parameters,                
                  'row_data': country_data}
    return series_row

def get_plot_series(elements, start_year, end_year, country_code, slug):
    plot_series = []
    start_year
    end_year
    for y in range(start_year, end_year + 1):
        p = cache.get(slug + '_' + country_code + '_' + str(y))
        if p is not None:
            print "p is %s" % p
            plot_series.append(p)
        else:
            print "p not cached for %s" % y
            p = {'count': elements.filter(year=y).count(), 'year': y}
            plot_series.append(p)
            cache.set(slug + '_' + country_code + '_' + str(y), p, ONE_YEAR)
                
    #plot_series = list(elements.values('year').annotate(count = Count('pk')).order_by('year'))
    #print "|-->point a.1"
    #for y in range(start_year,end_year + 1):
    #    try:
    #        plot_series.get(year=y)
    #    except:
    #        plot_series.append({'count': 0, 'year': y})
    return plot_series

def get_plot_parameters(data_list, start_year, end_year):
    print "In get_plot_parameters"
    #find the max value in all plot_series
    if data_list != []:
        max_value = max(max(data_list, key=operator.itemgetter('plot_series'))['plot_series'], key=operator.itemgetter('count'))['count']
    else:
        max_value = 0
      
   #make the plot labels
    labels=[]
    label_positions=[]
    for y in range(start_year, end_year + 1):
        if y % 10 == 0:
            labels.append(y)
            label_positions.append(y + 0.5)
    if labels == []:
        labels.append(start_year)
        labels.append(end_year)
        label_positions.append(start_year + 0.5)
        label_positions.append(end_year + 0.5)
    print "labels are %s" % labels

    return {'max_value': max_value,
            'labels': labels,
            'label_positions': label_positions,
            'plot_start_year': start_year,
            'plot_end_year': end_year + 1}

'''Returns a cache key that is unique for a query;
an underscore delimited string of session variable values'''
def get_cache_key(request, topic_slug='', subtopic_slug='', series_slug=''):
    print "In get_cache_key, topic_slug is %s" % topic_slug
    #cache_key = slugify('_'.join(str(v) for v in request.session.values()))
    cache_key = slugify(request.session.get('geo_slections', ""))
    if topic_slug != '':
        cache_key = cache_key + '_' + topic_slug
    if subtopic_slug != '':
        cache_key = cache_key + '_' + subtopic_slug
    if series_slug != '':
        cache_key = cache_key + '_' + series_slug
    return cache_key

'''Filters all Elements in the DB based on session varibles, returns a dict 
with the following keys:
    elements: a queryset containing elements needed for the table and map
    start_year and end_year: the year range for the queryset
    num_years: the number of years covered by the query (i.e. start_year - end_year + 1)
    countries: a queryset of selected countries, default is all countries
    cache_key: unique cache key for the query, from get_cache_key()'''
def get_query(request, topic_slug='', subtopic_slug='', series_code_slug=''):
    elements = Element.objects.exclude(value=0) \
                              .exclude(country__region_slug='aggregates') \
                              .filter(year__range=(request.session['start_year'], request.session['end_year']))
    topic = subtopic = series_name = series_code = None

    if topic_slug != '':
        print "about to filter by topic %s" % topic_slug
        elements = elements.filter(series__topic_slug = topic_slug)
        #cache the result of the expensive query to get topic_name
        #with another DB design this wouldn't be necessary
        topic = cache.get(topic_slug + '_name')
        if not topic:
            topic = elements.values('series__topic').distinct()[0]['series__topic']
            cache.set(topic_slug + '_name', topic, ONE_YEAR)

    if subtopic_slug != '':
        elements = elements.filter(series__sub1_slug = subtopic_slug) | \
                   elements.filter(series__sub2_slug = subtopic_slug) | \
                   elements.filter(series__sub3_slug = subtopic_slug)
        #this is a hack to get the subtopic name. assumes that all elements already are filtered to have the same subtopic
        subtopic = cache.get(subtopic_slug + '_name')
        if not subtopic:
            subtopic = max(elements[0].series.sub1_name, elements[0].series.sub2_name, elements[0].series.sub3_name)
            cache.set(subtopic_slug + '_name', subtopic, ONE_YEAR)

    if series_code_slug != '':
        elements = elements.filter(series__code_slug = series_code_slug)
        s = Series.objects.get(code_slug = series_code_slug)
        series_name = s.name
        series_code = s.code

    geo_selections = request.session.get('geo_selections')
    elements_by_country = []
    if geo_selections is not None:
        countries = Country.objects.filter(code__in=geo_selections)
        for c in countries:
            country_elements = elements.filter(country=c)
            elements_by_country.append({'code': c.code, 'elements': country_elements})
    else:
        countries = Country.objects.exclude(region_slug='aggregates')
        elements_by_country.append({'code': '', 'elements': elements})
    num_years = request.session['end_year'] - request.session['start_year'] + 1
    
    return {'elements_by_country': elements_by_country,
            'elements': elements, #redundant, but needed for the subtopic name hack
            'topic': topic,
            'topic_slug': topic_slug,
            'subtopic': subtopic,
            'subtopic_slug': subtopic_slug,
            'series_name': series_name,
            'series_code': series_code,
            'series_code_slug': series_code_slug,
            'start_year': request.session['start_year'],
            'end_year': request.session['end_year'],
            'num_years': num_years,
            'countries': countries,
            'cache_key': get_cache_key(request, topic_slug, subtopic_slug, series_code_slug)}
