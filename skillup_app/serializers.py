from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import serializers

from .models import (Profile, UploadMarkdownFile, ModifiedMarkdownFile, TaskTemplate, Assignment)
from .utils import render_markdown
