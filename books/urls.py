from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, ChapterViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'chapters', ChapterViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]