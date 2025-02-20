from rest_framework import serializers

class GetMostRelevantAnswersSerializer(serializers.Serializer):
    user_input = serializers.CharField()
