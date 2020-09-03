from dynamic_preferences.api.viewsets import PerInstancePreferenceViewSet
from dynamic_preferences.api.serializers import PreferenceSerializer
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from options.models import TournamentPreferenceModel
from tournaments.models import Tournament
from tournaments.mixins import TournamentFromUrlMixin

from participants.models import Institution,Team,Speaker

from django.db.models import Prefetch

from . import serializers
import random


class TournamentAPIMixin(TournamentFromUrlMixin):
    tournament_field = 'tournament'

    def perform_create(self, serializer):
        serializer.save(**{self.tournament_field: self.tournament})

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(**{self.tournament_field: self.tournament})

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tournament'] = self.tournament
        return context


class AdministratorAPIMixin:
    permission_classes = [IsAdminUser]


class APIRootView(AdministratorAPIMixin, GenericAPIView):
    name = "API Root"
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'

    def get(self, request, format=None):
        tournaments_create_url = reverse('api-tournament-list', request=request, format=format)
        institution_create_url = reverse('api-global-institution-list', request=request, format=format)
        return Response({
            "_links": {
                "tournaments": tournaments_create_url,
                "institutions": institution_create_url
            }
        })


class TournamentViewSet(AdministratorAPIMixin, ModelViewSet):
    # Don't use TournamentAPIMixin here, it's not filtering objects by tournament.
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'tournament_slug'


class TournamentPreferenceViewSet(TournamentFromUrlMixin, AdministratorAPIMixin, PerInstancePreferenceViewSet):
    queryset = TournamentPreferenceModel.objects.all()
    serializer_class = PreferenceSerializer

    def get_related_instance(self):
        return self.tournament


class BreakCategoryViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.BreakCategorySerializer


class SpeakerCategoryViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerCategorySerializer


class BreakEligibilityView(TournamentAPIMixin, AdministratorAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.BreakEligibilitySerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('team_set')


class SpeakerEligibilityView(TournamentAPIMixin, AdministratorAPIMixin, RetrieveUpdateAPIView):
    serializer_class = serializers.SpeakerEligibilitySerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('speaker_set')


class InstitutionViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return Institution.objects.all().prefetch_related(Prefetch('team_set', queryset=self.tournament.team_set.all()))


class TeamViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.TeamSerializer


class AdjudicatorViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.AdjudicatorSerializer


class GlobalInstitutionViewSet(AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.InstitutionSerializer

    def get_queryset(self):
        return Institution.objects.all()


class SpeakerViewSet(TournamentAPIMixin, AdministratorAPIMixin, ModelViewSet):
    serializer_class = serializers.SpeakerSerializer
    tournament_field = "team__tournament"

    def perform_create(self, serializer):
        serializer.save()

class SetTeamAPIView(APIView):

    def get(self,request, *args, **kwargs):
        institutions = Institution.objects.all()
        institutions = list(institutions)
        past_set = set()
        code = self.generate_word(3)
        while code in past_set:
            code = self.generate_word(3)
        past_set.add(code)
        for team in Team.objects.all().prefetch_related("speakers"):
            team.code_name = code
            team.short_reference = team.reference
            try:
                inst = [x for x in institutions if x.name in team.reference][0]
                team.institution = inst
                for speaker in team.speakers.all():
                    speaker.institution = inst
                    speaker.save()
            except:
                pass
            team.save()
        return Response("Success")

    def generate_word(self,length):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        res = ''
        for _ in range(length):
            res += random.choice(alphabet)
        return res
