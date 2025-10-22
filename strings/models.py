from django.db import models
import hashlib
from collections import Counter
from django.utils import timezone


class AnalyzedString(models.Model):
    # Use SHA-256 hash as primary key
    id = models.CharField(max_length=64, primary_key=True)
    value = models.TextField()

    # Properties
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    sha256_hash = models.CharField(max_length=64, db_index=True)
    character_frequency_map = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analyzed_strings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.value[:50]}..."

    @staticmethod
    def calculate_properties(value):
        """Calculate all properties for a given string"""
        # Calculate SHA-256 hash
        sha256_hash = hashlib.sha256(value.encode()).hexdigest()

        # Calculate length
        length = len(value)

        # Check if palindrome (case-insensitive, ignore spaces)
        cleaned = value.replace(' ', '').lower()
        is_palindrome = cleaned == cleaned[::-1]

        # Count unique characters
        unique_characters = len(set(value))

        # Count words
        word_count = len(value.split())

        # Character frequency map
        character_frequency_map = dict(Counter(value))

        return {
            'id': sha256_hash,
            'sha256_hash': sha256_hash,
            'length': length,
            'is_palindrome': is_palindrome,
            'unique_characters': unique_characters,
            'word_count': word_count,
            'character_frequency_map': character_frequency_map,
        }

    def save(self, *args, **kwargs):
        """Override save to auto-calculate properties"""
        if not self.id:
            props = self.calculate_properties(self.value)
            self.id = props['id']
            self.sha256_hash = props['sha256_hash']
            self.length = props['length']
            self.is_palindrome = props['is_palindrome']
            self.unique_characters = props['unique_characters']
            self.word_count = props['word_count']
            self.character_frequency_map = props['character_frequency_map']
        super().save(*args, **kwargs)
