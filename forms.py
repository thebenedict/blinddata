from django import forms

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
