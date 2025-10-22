from django.urls import path
from .views import (
    StringListCreateView,
    StringRetrieveDestroyView,
    NaturalLanguageFilterView,
   
)

urlpatterns = [
    path('strings/', StringListCreateView.as_view(), name='string-create'),
    path('strings/filter-by-natural-language/',
         NaturalLanguageFilterView.as_view(), name='natural-language-filter'),
    path('strings/<path:string_value>/',
         StringRetrieveDestroyView.as_view(), name='string-detail'),
]


