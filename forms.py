from django import forms

COUNTRY_CHOICES = (
    ('Regions', (
             ('SMR', 'Some Region'),
             ('ANR', 'Another Region'),
        )
    ),
    ('Countries', (
            ('TZA', 'Tanzania'),
            ('MLI', 'Mali'),
        )
    ),
)

class SessionSettingsForm(forms.Form):
    start_year = forms.IntegerField(label='Start year', \
                                    required=False, \
                                    min_value=1960, \
                                    max_value=2008, \
                                    widget=forms.TextInput(attrs={'class':'year_entry'}))
    end_year = forms.IntegerField(label='End year', \
                                  required=False, \
                                  min_value=1961, \
                                  max_value=2009, \
                                  widget=forms.TextInput(attrs={'class':'year_entry'}))
    country_one = forms.CharField(label='Filter by country', \
                                  required='False', \
                                  max_length=50, \
                                  widget=forms.Select(choices=COUNTRY_CHOICES))
    country_two = forms.CharField(label='Compare wth', \
                                  required='False', \
                                  max_length=50, \
                                  widget=forms.Select(choices=COUNTRY_CHOICES))
                 
