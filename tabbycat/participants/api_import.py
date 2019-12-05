import json
from rest_framework.views import APIView

import logging

from django.http import HttpResponse,HttpResponseBadRequest
from django.contrib.auth import authenticate

from tournaments.models import Tournament

from .models import Institution, Speaker, Team

logger = logging.getLogger(__name__)
# API TO ADD INSTITUTIONS, SPEAKERS, AND TEAMS THROUGH POST METHOD


class DataImportApi(APIView):
    def check_validity_institutions(self,data):
        if not data:
            return
        for i in data:
            this_institution_code = i.get('code','')
            this_institution_name = i.get('name','')
            if not (this_institution_code and this_institution_name):
                return HttpResponseBadRequest("Malformed JSON INSTITUTION DATA:Lacking Values")
            if Institution.objects.filter(code=this_institution_code).exists():
                return HttpResponseBadRequest("Repetitive Entry:{}".format(this_institution_code))

    def check_validity_teams(self,data):
        if not data:
            return
        for i in data:
            this_team_name = i.get('name','')
            if not this_team_name:
                return HttpResponseBadRequest("Malformed JSON TEAM DATA:Lacking Values")
            if Team.objects.filter(reference=this_team_name).exists():
                return HttpResponseBadRequest("Repetitive Entry:{}".format(this_team_code))

    def create_institution(self,data):
        new_institution_name = data.get('name', '')
        new_institution_code = data.get('code', '')
        new_institution = Institution()
        new_institution.name = new_institution_name
        new_institution.code = new_institution_code
        new_institution.save()

    def create_team(self, data,tournament):
        new_team_name = data.get('name', '')
        new_team_code = data.get('code', '')
        new_team = Team()
        new_team.reference = new_team_name
        new_team.code_name = new_team_code
        if data.get('nuse_institution_prefixame', '') == "FALSE":
            new_team.use_institution_prefix = False
        new_team.tournament = tournament
        new_team.save()
        speakers = data.get('speakers', '')
        if speakers:
            for i in speakers:
                self.create_speaker(i,new_team)


    def create_speaker(self,data,team):
        new_speaker_name = data.get('name', '')
        new_speaker_gender = data.get('gender', '')
        new_speaker_email = data.get('email', '')
        new_speaker = Speaker()
        new_speaker.name = new_speaker_name
        if new_speaker_gender:
            new_speaker.gender = new_speaker_gender
        if new_speaker_email:
            new_speaker.email = new_speaker_email
        new_speaker.team = team
        new_speaker.save()

    def post(self,request,**kwargs):
        tournament_ref = Tournament.objects.get(slug=kwargs['tournament_slug'])
        username = request.META.get("HTTP_APIUSERNAME")
        password = request.META.get("HTTP_PASSWORD")
        print(username)
        print(password)
        user = authenticate(username=username, password=password)
        if not user:
            return HttpResponseBadRequest("BAD REQUEST:AUTHENTICATION FAILED")
        if not user.is_staff:
            return HttpResponseBadRequest("BAD REQUEST:NO PERMIT")
        data = request.body.decode('utf-8')
        received = json.loads(data)
        institutions = received.get('institutions','')
        teams = received.get('teams', '')
        instcheck = self.check_validity_institutions(institutions)
        teamcheck = self.check_validity_teams(teams)
        if instcheck or teamcheck:
            return instcheck or teamcheck
        for i in institutions:
            self.create_institution(i)
        for j in teams:
            self.create_team(j,tournament_ref)
        return HttpResponse("DATA SUBMITTED")

