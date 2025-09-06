from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, UploadedMarkdownFileUploadView,
    UploadedMarkdownFileViewSet, ModifiedMarkdownFileViewSet,
    TaskTemplateViewSet, AssignmentViewSet,
)

router = DefaultRouter()
router.register(r"uploaded-md", UploadedMarkdownFileViewSet, basename="uploaded-md")
router.register(r"modified-md", ModifiedMarkdownFileViewSet, basename="modified-md")
router.register(r"templates", TaskTemplateViewSet, basename="templates")
router.register(r"assignments", AssignmentViewSet, basename="assignments")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("uploaded-md/upload/", UploadedMarkdownFileUploadView.as_view(), name="uploaded-md-upload"),
    path("", include(router.urls)),
]
