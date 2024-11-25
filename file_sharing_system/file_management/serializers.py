from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'user_type')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'file', 'upload_date')