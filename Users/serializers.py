from rest_framework import serializers
from .models import MyUser, AcademicProfile, PersonalProfile

class PersonalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalProfile
        fields = '__all__'

class AcademicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProfile
        fields = '__all__'

class MyUserSerializer(serializers.ModelSerializer):
    academic_profile = AcademicProfileSerializer(read_only=True)
    personal_profile = PersonalProfileSerializer(read_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'role','password', 'academic_profile', 'personal_profile')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(**validated_data)
        return user
