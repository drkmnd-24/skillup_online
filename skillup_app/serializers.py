from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import serializers

from .models import (Profile, UploadMarkdownFile, ModifiedMarkdownFile, TaskTemplate, Assignment)
from .utils import render_markdown


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, help_text='Use Knox ID as username')
    password = serializers.CharField(write_only=True)
    position = serializers.ChoiceField(choices=Profile.POSITIONS)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        Profile.objects.create(user=user, position=validated_data['position'])
        return user


class UserSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source='profile.get_position_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'position']


class UploadMarkdownFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadMarkdownFile
        fields = ['id', 'title', 'file', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']


class ModifiedMarkdownFileSerializer(serializers.ModelSerializer):
    original_title = serializers.CharField(source='original.__str__', read_only=True)
    render_html = serializers.SerializerMethodField()

    class Meta:
        model = ModifiedMarkdownFile
        fields = ["id", "title", "original", "original_title",
                  "content", "file", "created_by", "created_at", "rendered_html"]

    def get_rendered_html(self, obj):
        return render_markdown(obj.content)

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class TaskTemplateSerializer(serializers.ModelSerializer):
    modified_title = serializers.CharField(source='modified.__str__', read_only=True)
    rendered_html = serializers.SerializerMethodField()

    class Meta:
        model = TaskTemplate
        fields = ["id", "title", "description", "is_active",
                  "modified", "modified_title", "created_by", "created_at", "rendered_html"]
        read_only_fields = ['created_by', 'created_at', 'rendered_html']

    def get_rendered_html(self, obj):
        return render_markdown(obj.modified.content)

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class AssignmentSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source='template.title', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = Assignment
        fields = ["id", "template", "template_title", "student", "student_username",
                  "status", "assigned_at", "started_at", "completed_at"]
        read_only_fields = ['status', 'assignment_at', 'started_at', 'completed_at']


class MyAssignmentSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source='template.title', read_only=True)
    html = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ["id", "template", "template_title", "status", "assigned_at", "started_at", "completed_at", "html"]

    def get_html(self, obj):
        return render_markdown(obj.template.modified.content)
