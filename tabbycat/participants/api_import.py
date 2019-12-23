import json

from rest_framework.views import APIView

import logging

from django.http import HttpResponse,HttpResponseBadRequest
from django.contrib.auth import authenticate


from .models import Adjudicator, Institution, Speaker, Team
from.serializers import AdjudicatorSerializerImport, InstitutionSerializerImport, TeamSerializerImport

logger = logging.getLogger(__name__)
# API TO ADD INSTITUTIONS, SPEAKERS, AND TEAMS THROUGH POST METHOD


class DataImportApi(APIView):

    def post(self,request,**kwargs):
        username = request.META.get("HTTP_APIUSERNAME")
        password = request.META.get("HTTP_PASSWORD")
        user = authenticate(username=username, password=password)
        if not user:
            return HttpResponseBadRequest("BAD REQUEST:AUTHENTICATION FAILED")
        if not user.is_staff:
            return HttpResponseBadRequest("BAD REQUEST:NO PERMIT")
        data = request.body.decode('utf-8')
        received = json.loads(data)
        received['tournament'] = kwargs['tournament_slug']
        institutions_data = received.get("institutions",[])
        teams_data = received.get("teams",[])
        adjudicators_data = received.get("adjudicators",[])
        serializers = []
        for i in institutions_data:
            serializers.append(InstitutionSerializerImport(data=i))
        for i in serializers:
            i.is_valid(raise_exception=True)
            i.save()
            serializers.remove(i) # Institution need to be created first before validitation of teams
        for i in teams_data:
            i['tournament'] = kwargs['tournament_slug']
            serializers.append(TeamSerializerImport(data=i))
        for i in adjudicators_data:
            i['tournament'] = kwargs['tournament_slug']
            serializers.append(AdjudicatorSerializerImport(data=i))
        for i in serializers:
            i.is_valid(raise_exception=True)
            i.save()
            serializers.remove(i)
        return HttpResponse("DATA SENT")
