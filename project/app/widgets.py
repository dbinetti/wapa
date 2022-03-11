import json
import re

from django import forms
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe


class AddressWidget(forms.TextInput):
    class Media:
        """Media defined as a dynamic property instead of an inner class."""
        # Requred JS for widget
        js = [
            "https://code.jquery.com/jquery-3.5.1.slim.min.js",
            f"https://maps.googleapis.com/maps/api/js?libraries=places&key={settings.GOOGLE_API_KEY}",
            "app/js/jquery.geocomplete.min.js",
            "app/js/address.js",
        ]

    def __init__(self, *args, **kwargs):
        # Not sure what this is doing, but looks harmless
        attrs = kwargs.get("attrs", {})
        classes = attrs.get("class", "")
        classes += (" " if classes else "") + "address"
        attrs["class"] = classes
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, **kwargs):
        # Can accept None, a dictionary of values, or a str
        p = re.compile('(?<!\\\\)\'')
        try:
            value = p.sub('\"', value)
        except TypeError:
            value = None
        if value in (None, ""):
            ad = {}
        else:
            try:
                ad = json.loads(value)
            except json.decoder.JSONDecodeError:
                ad = {'formatted': value}

        # Render the formatted address
        element = super().render(name, escape(ad.get("formatted", "")), attrs, **kwargs)
        return mark_safe(element)

    def value_from_datadict(self, data, files, name):
        raw = data.get(name, "")
        return raw
