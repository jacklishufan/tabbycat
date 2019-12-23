from rest_framework import serializers

from .models import Adjudicator, Institution, Speaker, SpeakerCategory, Team


from tournaments.models import Tournament


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ('id', 'name', 'gender')


class SpeakerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakerCategory
        fields = ('name')


class InstitutionSerializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Institution
        fields = ('id', 'name', 'code', 'region')


class AdjudicatorSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Adjudicator
        fields = ('id', 'name', 'gender', 'institution',)


class TeamSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(read_only=True)
    speakers = SpeakerSerializer(read_only=True, many=True)
    points = serializers.SerializerMethodField(read_only=True)
    break_categories = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    def get_points(self, obj):
        return obj.points_count

    class Meta:
        model = Team
        fields = ('id', 'short_name', 'long_name', 'code_name', 'points',
                  'institution', 'speakers', 'break_categories')


class SpeakerSerializerImport(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ('name', 'gender','email')


class AdjudicatorSerializerImport(serializers.ModelSerializer):
    institution = serializers.SlugRelatedField(
        queryset=Institution.objects.all(),
        slug_field="code"
    )
    tournament = serializers.SlugRelatedField(
        queryset=Tournament.objects.all(),
        slug_field='slug'
    )
    class Meta:
        model = Adjudicator
        fields = ('name', 'gender', 'email', 'institution','tournament')


class TeamSerializerImport(serializers.ModelSerializer):
    institution = serializers.SlugRelatedField(
        queryset=Institution.objects.all(),
        slug_field='code'
    )
    tournament = serializers.SlugRelatedField(
        queryset=Tournament.objects.all(),
        slug_field='slug'
    )
    speakers = SpeakerSerializerImport(many=True)
    class Meta:
        model = Team
        fields = ('reference', 'code_name',
                  'institution', 'speakers','tournament')
    def create(self,validated_data):
        speaker_data = validated_data.pop('speakers')
        team = Team.objects.create(**validated_data)
        for i in speaker_data:
            Speaker.objects.create(team=team, **i)
        return team


class InstitutionSerializerImport(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ('name', 'code')