from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import UploadedMarkdownFile, ModifiedMarkdownFile, TaskTemplate, Assignment
from .serializers import (
    RegistrationSerializer,
    UploadedMarkdownFileSerializer, ModifiedMarkdownFileSerializer,
    TaskTemplateSerializer, AssignmentSerializer, MyAssignmentSerializer,
)
from .permissions import IsAssignee


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer


class UploadedMarkdownFileUploadView(generics.CreateAPIView):
    """Admin endpoint to upload one or multiple .md files."""
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        created = []
        for f in files:
            item = UploadedMarkdownFile.objects.create(
                title=request.data.get("title", f.name),
                file=f,
                uploaded_by=request.user,
            )
            created.append(UploadedMarkdownFileSerializer(item, context={"request": request}).data)
        return Response(created, status=status.HTTP_201_CREATED)


class UploadedMarkdownFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UploadedMarkdownFile.objects.all()
    serializer_class = UploadedMarkdownFileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"])
    def content(self, request, pk=None):
        obj = self.get_object()
        return Response({"id": obj.id, "title": obj.title, "content": obj.read_text()})


class ModifiedMarkdownFileViewSet(viewsets.ModelViewSet):
    queryset = ModifiedMarkdownFile.objects.select_related("original").all()
    serializer_class = ModifiedMarkdownFileSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "list", "retrieve"]:
            if self.action in ["create", "update", "partial_update", "destroy"]:
                return [IsAdminUser()]
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=["get"])
    def render(self, request, pk=None):
        obj = self.get_object()
        ser = self.get_serializer(obj)
        return Response({"id": obj.id, "html": ser.data.get("rendered_html")})


class TaskTemplateViewSet(viewsets.ModelViewSet):
    queryset = TaskTemplate.objects.select_related("modified").all()
    serializer_class = TaskTemplateSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["get"])
    def render(self, request, pk=None):
        obj = self.get_object()
        ser = self.get_serializer(obj)
        return Response({"id": obj.id, "html": ser.data.get("rendered_html")})


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related("template", "student", "template__modified").all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "list", "retrieve"]:
            if self.action in ["create", "update", "partial_update", "destroy"]:
                return [IsAdminUser()]
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="my")
    def my_assignments(self, request):
        qs = Assignment.objects.filter(student=request.user).select_related("template__modified")
        return Response(MyAssignmentSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAssignee])
    def start(self, request, pk=None):
        obj = self.get_object()
        obj.start()
        return Response({"id": obj.id, "status": obj.status})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAssignee])
    def done(self, request, pk=None):
        obj = self.get_object()
        obj.complete()
        return Response({"id": obj.id, "status": obj.status})