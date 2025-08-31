from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (UploadMarkdownFile, ModifiedMarkdownFile, TaskTemplate, Assignment)
from .serializers import (RegistrationSerializer, UserSerializer, UploadMarkdownFile, ModifiedMarkdownFile,
                          TaskTemplateSerializer, AssignmentSerializer, MyAssignmentSerializer)
from .permissions import IsAssignee

# Create your views here.
