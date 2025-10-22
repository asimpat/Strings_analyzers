from rest_framework import serializers
from .models import AnalyzedString


class AnalyzedStringSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_properties(self, obj):
        """Return properties in the required format"""
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_characters,
            'word_count': obj.word_count,
            'sha256_hash': obj.sha256_hash,
            'character_frequency_map': obj.character_frequency_map,
        }


# class StringCreateSerializer(serializers.Serializer):
#     value = serializers.CharField(required=True, allow_blank=False)

#     def validate_value(self, value):
#         """Ensure value is a string"""
#         if not isinstance(value, str):
#             raise serializers.ValidationError("Value must be a string")
#         return value


class StringListSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'properties', 'created_at']

    def get_properties(self, obj):
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_characters,
            'word_count': obj.word_count,
            'sha256_hash': obj.sha256_hash,
            'character_frequency_map': obj.character_frequency_map,
        }

class StringCreateSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, allow_blank=False)

    def validate_value(self, value):
        """Ensure value is a valid alphabetic string"""
        if not value.isalpha():
            raise serializers.ValidationError("Only alphabetic strings are allowed.")
        return value

    def create(self, validated_data):
        """Handle creation and property analysis"""
        value = validated_data["value"]

        # Compute properties manually (this assumes your model has these fields)
        from hashlib import sha256
        from collections import Counter
        import json

        properties = {
            "length": len(value),
            "is_palindrome": value.lower() == value[::-1].lower(),
            "unique_characters": len(set(value)),
            "word_count": len(value.split()),
            "sha256_hash": sha256(value.encode()).hexdigest(),
            "character_frequency_map": dict(Counter(value)),
        }

        # Save to DB
        analyzed_string = AnalyzedString.objects.create(
            value=value,
            length=properties["length"],
            is_palindrome=properties["is_palindrome"],
            unique_characters=properties["unique_characters"],
            word_count=properties["word_count"],
            sha256_hash=properties["sha256_hash"],
            character_frequency_map=json.dumps(properties["character_frequency_map"]),
        )

        return analyzed_string

