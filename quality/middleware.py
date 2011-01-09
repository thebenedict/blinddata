'''Set session defaults to the full range of years for new sessions
#TODO get from the DB instead of hard coding?'''
class BD_SessionMiddleware(object):

    def process_request(self, request):
        exists = request.session.get('start_year')
        if not exists:
            request.session['start_year'] = 1960
        exists = request.session.get('end_year')
        if not exists:
            request.session['end_year'] = 2009
        exists = request.session.get('geo_selections')
        if not exists:
            request.session['geo_selections'] = [u'',u'']
        #request.session['geo_selections'] = ['TZA', 'MLI']
        #request.session['start_year'] = 2004
        #request.session['geo_selections'] = None
