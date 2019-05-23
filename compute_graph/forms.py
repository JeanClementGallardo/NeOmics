from django import forms
from import_raw.models import RawData


class OrganismChoice(forms.Form):
    organisms = forms.MultipleChoiceField(choices=[rd.organism for rd in RawData.objects.order_by("organism")])