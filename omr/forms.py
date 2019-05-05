from django import forms

from omr.models import Author, Theme


class FileFilterForm(forms.Form):
    boolean_choices = (
        ('', 'All'),
        (True, 'Yes'),
        (False, 'No')
    )

    search = forms.CharField(
        label='Search',
        required=False
    )

    themes = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'select2-widget'}),
        queryset=Theme.objects.all(),
        label='Themes',
        required=False,
    )

    authors = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'select2-widget'}),
        queryset=Author.objects.all(),
        label='Authors',
        required=False,
    )

    is_main_model = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'select'}),
        choices=boolean_choices,
        label='Is main model',
        required=False,
    )

    missing_parts = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'select'}),
        choices=boolean_choices,
        label='Missing parts',
        required=False,
    )

    missing_patterns = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'select'}),
        choices=boolean_choices,
        label='Missing patterns',
        required=False,
    )

    missing_stickers = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'select'}),
        choices=boolean_choices,
        label='Missing stickers',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(FileFilterForm, self).__init__(*args, **kwargs)

        # This adds classes that add Bootstrap styling to the forms
        for field in iter(self.fields):
            # widget already has classes
            if 'class' in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({
                    'class': self.fields[field].widget.attrs['class'] + ' form-control'
                })
            # widget doesn't have any classes yet
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
