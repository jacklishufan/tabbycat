import logging

from django.http import HttpResponse,HttpResponseBadRequest
from django.contrib.auth import authenticate

from tournaments.models import Tournament

from .models import Institution, Speaker, Team

logger = logging.getLogger(__name__)
# API TO ADD INSTITUTIONS, SPEAKERS, AND TEAMS THROUGH POST METHOD


def api_auth(request):
    if not request.method == 'POST':
        return HttpResponseBadRequest("BAD REQUEST:WRONG METHOD")
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = authenticate(username=username, password=password)
    print(user)
    if not user:
        return HttpResponseBadRequest("BAD REQUEST:AUTHENTICATION FAILED")
    if not user.is_staff:
        return HttpResponseBadRequest("BAD REQUEST:NO PERMIT")


def api_create_institution(request,**kwargs):
    auth = api_auth(request)
    if auth:
        return auth
    postdata = request.POST
    new_institution_name = request.POST.get('inst_name','')
    new_institution_code = request.POST.get('inst_code','')
    print(postdata)
    if not (new_institution_name and new_institution_code):
        return HttpResponseBadRequest("BAD REQUEST:LACKING DATA")
    if Institution.objects.filter(code=new_institution_code).exists():
        return HttpResponseBadRequest("BAD REQUEST:REPETITIVE ENTRY")
    new_institution = Institution()
    new_institution.name = new_institution_name
    new_institution.code = new_institution_code
    new_institution.save()
    return HttpResponse("INSTITUTION CREATED")


def api_create_team(request,**kwargs):
    print(kwargs)
    auth = api_auth(request)
    if auth:
        return auth
    new_code_name = request.POST.get('code_name','')
    if Team.objects.filter(code_name=new_code_name).exists():
        return HttpResponseBadRequest("BAD REQUEST:REPETITIVE ENTRY")
    new_reference = request.POST.get('reference','')
    tournament_ref = Tournament.objects.get(slug=kwargs['tournament_slug'])
    new_team = Team()
    new_team.tournament = tournament_ref
    new_team.code_name = new_code_name
    new_team.reference = new_reference
    new_team.short_reference = request.POST.get('short_reference',new_reference)
    institution_name = request.POST.get('institution','')
    if institution_name:
        if not Institution.objects.filter(code=institution_name).exists():
            return HttpResponseBadRequest("BAD REQUEST:INSTITUTION NOT FOUND")
        institution_ref = Institution.objects.get(code=institution_name)
        new_team.institution = institution_ref
    if request.POST.get('prefix','') == "TRUE":
        new_team.use_institution_prefix = True
    new_team.type = 'N'
    if request.POST.get('type','') in ['N','S','C','B']:
        new_team.type = request.POST.get('type','')
    new_team.save()
    return HttpResponse("TEAM CREATED")


def api_create_speaker(request,**kwargs):
    print(kwargs)
    auth = api_auth(request)
    if auth:
        return auth
    speaker_name = request.POST.get('speaker_name','')
    speaker_email = request.POST.get('email', '')
    speaker_phone = request.POST.get('phone', '')
    speaker_gender = request.POST.get('gender', '')
    speaker_team = request.POST.get('team', '')
    if not (speaker_name and speaker_team):
        return HttpResponseBadRequest("BAD REQUEST:LACKING DATA")
    new_speaker = Speaker()
    new_speaker.name = speaker_name
    if speaker_email:
        new_speaker.email = speaker_email
    if speaker_phone:
        new_speaker.phone = speaker_phone
    if not Team.objects.filter(code_name=speaker_team).exists():
        return HttpResponseBadRequest("BAD REQUEST:TEAM NOT FOUND")
    new_speaker.team = Team.objects.get(code_name=speaker_team)
    if speaker_gender in ['M','F','O']:
        new_speaker.gender = speaker_gender
    new_speaker.save()
    return HttpResponse("Speaker Created")
