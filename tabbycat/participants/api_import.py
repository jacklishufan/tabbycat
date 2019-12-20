import json

from rest_framework.views import APIView

import logging

from django.http import HttpResponse,HttpResponseBadRequest
from django.contrib.auth import authenticate

from tournaments.models import Tournament

from .models import Institution, Speaker, Team, Adjudicator

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
                return HttpResponseBadRequest("Repetitive Entry:{}".format(this_team_name))
    def check_validity_adjudicators(self,data):
        if not data:
            return
        for i in data:
            this_adj_inst = i.get('institution','')
            if this_adj_inst and not Institution.objects.filter(code=this_adj_inst).exists():
                return HttpResponseBadRequest("No Such Institution:{}".format(this_adj_inst))

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

    def create_adjudicator(self,data):
        new_adjudicator_name = data.get('name', '')
        new_adjudicator_gender = data.get('gender', '')
        new_adjudicator_email = data.get('email', '')
        new_adjudicator_institution = data.get('institution', '')
        new_adjudicator = Adjudicator()
        new_adjudicator.name = new_adjudicator_name
        if new_adjudicator_gender:
            new_adjudicator.gender = new_adjudicator_gender
        if new_adjudicator_email:
            new_adjudicator.email = new_adjudicator_email
        if new_adjudicator_institution:
            new_adjudicator.institution = Institution.objects.get(code=new_adjudicator_institution)
        new_adjudicator.save()

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
        adjudicators = received.get('adjudicators', '')
        instcheck = self.check_validity_institutions(institutions)
        teamcheck = self.check_validity_teams(teams)
        adjcheck = self.check_validity_adjudicators(adjudicators)
        if instcheck or teamcheck or adjcheck:
            return instcheck or teamcheck or adjcheck
        for i in institutions:
            self.create_institution(i)
        for j in teams:
            self.create_team(j,tournament_ref)
        for k in adjudicators:
            self.create_adjudicator(k)
        return HttpResponse("DATA SUBMITTED")
