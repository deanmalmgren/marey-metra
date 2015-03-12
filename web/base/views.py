""" Views for the base application """
import json
import datetime

from django.shortcuts import render

from .models import Punchcard


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def marey(request):
    """ Default view for the root """

    punchcards = []
    for punchcard in Punchcard.objects.filter(trip_id="UP-W_UW11_V7"):
        punchcards.append(punchcard.to_json_dict())

    return render(request, 'base/marey.html', {
        "punchcards": json.dumps(punchcards, cls=JsonEncoder),

    })
