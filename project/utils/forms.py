from django.forms import forms


class CssForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CssForm, self).__init__(*args, **kwargs)
        for label, field in self.fields.items():
            if field.widget.attrs.get("class"):
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"
