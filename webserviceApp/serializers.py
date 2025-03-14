from rest_framework import serializers
from webserviceApp.models import ProviderService
from . models import User


# Provider Data Serializers -
class ProviderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProviderService
        fields = '__all__'



# For the Users Data Serializers(Included=> Admin, Provider and Clients)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'first_name', 'last_name']

    
    def create(self, validated_data):
        # Hash the password before saving
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user