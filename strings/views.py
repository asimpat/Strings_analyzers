from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AnalyzedString
from .serializers import (
    AnalyzedStringSerializer,
    StringCreateSerializer,
    StringListSerializer
)
import re
import hashlib



class StringListCreateView(generics.ListCreateAPIView):
   
    # GET /strings - List all strings with optional filtering
    # POST /strings - Create and analyze a new string
   
    serializer_class = AnalyzedStringSerializer

    def get_queryset(self):
        """Apply filters to queryset"""
        queryset = AnalyzedString.objects.all()

        # Get query parameters
        is_palindrome = self.request.query_params.get('is_palindrome')
        min_length = self.request.query_params.get('min_length')
        max_length = self.request.query_params.get('max_length')
        word_count = self.request.query_params.get('word_count')
        contains_character = self.request.query_params.get(
            'contains_character')

        # Apply filters
        if is_palindrome is not None:
            if is_palindrome.lower() == 'true':
                queryset = queryset.filter(is_palindrome=True)
            elif is_palindrome.lower() == 'false':
                queryset = queryset.filter(is_palindrome=False)

        if min_length:
            try:
                queryset = queryset.filter(length__gte=int(min_length))
            except ValueError:
                pass

        if max_length:
            try:
                queryset = queryset.filter(length__lte=int(max_length))
            except ValueError:
                pass

        if word_count:
            try:
                queryset = queryset.filter(word_count=int(word_count))
            except ValueError:
                pass

        if contains_character and len(contains_character) == 1:
            queryset = queryset.filter(value__icontains=contains_character)

        return queryset

    def get_serializer_class(self):
        """Use different serializers for list vs create"""
        if self.request.method == 'POST':
            return StringCreateSerializer
        return StringListSerializer

    def list(self, request, *args, **kwargs):
        """Override list to add custom response format"""
        queryset = self.get_queryset()

        # Collect applied filters
        filters_applied = {}
        params = request.query_params

        if params.get('is_palindrome'):
            filters_applied['is_palindrome'] = params.get(
                'is_palindrome').lower() == 'true'
        if params.get('min_length'):
            try:
                filters_applied['min_length'] = int(params.get('min_length'))
            except ValueError:
                pass
        if params.get('max_length'):
            try:
                filters_applied['max_length'] = int(params.get('max_length'))
            except ValueError:
                pass
        if params.get('word_count'):
            try:
                filters_applied['word_count'] = int(params.get('word_count'))
            except ValueError:
                pass
        if params.get('contains_character'):
            char = params.get('contains_character')
            if len(char) == 1:
                filters_applied['contains_character'] = char

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'data': serializer.data,
            'count': queryset.count(),
            'filters_applied': filters_applied
        })

    def create(self, request, *args, **kwargs):
        value = request.data.get("value")

    # 1️⃣ Missing value
        if value is None:
            return Response(
                {"error": "'value' field is required."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # 2️⃣ Invalid data type
        if not isinstance(value, str):
            return Response(
                {"error": "Invalid data type. 'value' must be a string."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # 3️⃣ Clean up extra whitespace
        value = value.strip()
        if not value:
            return Response(
                {"error": "'value' cannot be empty."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # 4️⃣ Duplicate check
        sha256_hash = hashlib.sha256(value.encode()).hexdigest()
        if AnalyzedString.objects.filter(id=sha256_hash).exists():
            return Response(
                {"error": "String already exists in the system."},
                status=status.HTTP_409_CONFLICT
            )

        try:
            # Calculate all properties first
            props = AnalyzedString.calculate_properties(value)

            # Create and save object
            analyzed_string = AnalyzedString.objects.create(value=value, **props)

            response_serializer = AnalyzedStringSerializer(analyzed_string)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Safer catch block
            return Response(
                {"error": f"Internal Server Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class StringRetrieveDestroyView(generics.RetrieveDestroyAPIView):
   
    # GET /strings/{string_value} - Retrieve a specific string
    # DELETE /strings/{string_value} - Delete a string
  
    serializer_class = AnalyzedStringSerializer
    lookup_field = 'value'
    lookup_url_kwarg = 'string_value'

    def get_queryset(self):
        return AnalyzedString.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to handle 404 properly"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except AnalyzedString.DoesNotExist:
            return Response(
                {'error': 'String does not exist in the system'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        string_value = kwargs.get('string_value')
        obj = AnalyzedString.objects.filter(value=string_value).first()

        if not obj:
            return Response(
                {'error': 'String does not exist in the system'},
                status=status.HTTP_404_NOT_FOUND
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class NaturalLanguageFilterView(APIView):
    """GET /strings/filter-by-natural-language?query=... - Natural language filtering"""

    def parse_natural_language(self, query):
        """Parse natural language query into filters"""
        query_lower = query.lower()
        filters = {}

        # Check for palindrome
        if 'palindrome' in query_lower or 'palindromic' in query_lower:
            filters['is_palindrome'] = True

        # Check for word count
        if 'single word' in query_lower or 'one word' in query_lower:
            filters['word_count'] = 1
        elif 'two word' in query_lower or '2 word' in query_lower:
            filters['word_count'] = 2
        elif 'three word' in query_lower or '3 word' in query_lower:
            filters['word_count'] = 3

        # Extract numeric word count: "X word strings"
        word_count_match = re.search(r'(\d+)\s+word', query_lower)
        if word_count_match:
            filters['word_count'] = int(word_count_match.group(1))

        # Check for length conditions
        # "longer than X characters"
        longer_match = re.search(
            r'(?:longer than|more than)\s+(\d+)', query_lower)
        if longer_match:
            filters['min_length'] = int(longer_match.group(1)) + 1

        # "shorter than X characters"
        shorter_match = re.search(
            r'(?:shorter than|less than)\s+(\d+)', query_lower)
        if shorter_match:
            filters['max_length'] = int(shorter_match.group(1)) - 1

        # "at least X characters"
        at_least_match = re.search(r'at least\s+(\d+)', query_lower)
        if at_least_match:
            filters['min_length'] = int(at_least_match.group(1))

        # "at most X characters"
        at_most_match = re.search(r'at most\s+(\d+)', query_lower)
        if at_most_match:
            filters['max_length'] = int(at_most_match.group(1))

        # Check for "contains letter/character X"
        contains_match = re.search(
            r'contain(?:s|ing)?\s+(?:the\s+)?(?:letter|character)\s+([a-z])', query_lower, re.IGNORECASE)
        if contains_match:
            filters['contains_character'] = contains_match.group(1)

        # Check for "first vowel" (a)
        if 'first vowel' in query_lower:
            filters['contains_character'] = 'a'

        # Check for last vowel (u)
        if 'last vowel' in query_lower:
            filters['contains_character'] = 'u'

        return filters

    def get(self, request):
        query = request.query_params.get('query', '')

        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Parse the natural language query
            parsed_filters = self.parse_natural_language(query)

            if not parsed_filters:
                return Response(
                    {'error': 'Unable to parse natural language query'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # Apply filters to queryset
            queryset = AnalyzedString.objects.all()

            if 'is_palindrome' in parsed_filters:
                queryset = queryset.filter(
                    is_palindrome=parsed_filters['is_palindrome'])

            if 'word_count' in parsed_filters:
                queryset = queryset.filter(
                    word_count=parsed_filters['word_count'])

            if 'min_length' in parsed_filters:
                queryset = queryset.filter(
                    length__gte=parsed_filters['min_length'])

            if 'max_length' in parsed_filters:
                queryset = queryset.filter(
                    length__lte=parsed_filters['max_length'])

            if 'contains_character' in parsed_filters:
                queryset = queryset.filter(
                    value__icontains=parsed_filters['contains_character'])

            # Serialize results
            serializer = StringListSerializer(queryset, many=True)

            return Response({
                'data': serializer.data,
                'count': queryset.count(),
                'interpreted_query': {
                    'original': query,
                    'parsed_filters': parsed_filters
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Unable to process query'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
