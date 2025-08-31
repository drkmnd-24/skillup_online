from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.files.base import ContentFile

import os


class Profile(models.Model):
    POSITION_DEVOPS = 'DEVOPS'
    POSITION_DB = "DB_SOFTWARE_ENG"
    POSITION_SWE = "SOFTWARE_DEV"
    POSITION_OTHER = "OTHER"

    DEPARTMENT_CHOICES = [
        ('COT', 'COT'),
        ('CST', 'CST'),
        ('CIT', 'CIT'),
        ('NWT', 'NWT'),
    ]

    LAB_PART_CHOICES = [
        ('CO1', 'CO1'),
        ('CO2', 'CO2'),
        ('CO3', 'CO3'),
        ('CO4', 'CO4'),
        ('CML', 'CML'),
    ]

    POSITIONS = [
        (POSITION_DEVOPS, "DevOps"),
        (POSITION_DB, "Database Software Engineer"),
        (POSITION_SWE, "Software Developer"),
        (POSITION_OTHER, "Other"),
        (DEPARTMENT_CHOICES, "Department"),
        (LAB_PART_CHOICES, "Lab Part"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField(max_length=32, choices=POSITIONS)

    def __str__(self):
        return f'{self.user.username} · {self.get_position_display()}'


def upload_to_original(instance, filename):
    return os.path.join('md', 'originals', filename)


def upload_to_modified(instance, filename):
    stamp = timezone.now().strftime('%Y%m%d-%H%M%S')
    root, ext = os.path.splitext(filename)
    if not ext:
        ext = '.md'
    safe_root = slugify(root) or 'modified'
    return os.path.join('md', 'modified', f'{safe_root}-{stamp}{ext}')


class UploadMarkdownFile(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=upload_to_original)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or os.path.basename(self.file.name)

    def read_text(self) -> str:
        if not self.file:
            return ''
        self.file.open('rb')
        try:
            return self.file.read().decode('utf-8')
        finally:
            self.file.close()


class ModifiedMarkdownFile(models.Model):
    original = models.ForeignKey(UploadMarkdownFile, on_delete=models.CASCADE, related_name='modifications')
    title = models.CharField(max_length=255, blank=True, help_text='Optional title for easier lookup')
    content = models.TextField(help_text='Edited Markdown content. The original file remains unchanged.')
    file = models.FileField(upload_to=upload_to_modified, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f'Modified from {self.original}'

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating or not self.file:
            base_name = self.title or (self.original.title or os.path.basename(self.original.file.name))
            md_name = upload_to_modified(self, base_name)
            content_file = ContentFile(self.content.encode('utf-8'))
            self.file.save(md_name.split('/')[-1], content_file, save=True)


class TaskTemplate(models.Model):
    modified = models.OneToOneField(ModifiedMarkdownFile, on_delete=models.CASCADE, related_name='template')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Assignment(models.Model):
    STATUS_ASSIGNED = "ASSIGNED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_DONE = "DONE"
    STATUSES = [
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
    ]

    template = models.ForeignKey(TaskTemplate, on_delete=models.CASCADE, related_name='assignments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=16, choices=STATUSES, default=STATUS_ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('template', 'student')
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.template.title} → {self.student.username} [{self.status}]'

    def start(self):
        if self.status == self.STATUS_ASSIGNED:
            self.status = self.STATUS_IN_PROGRESS
            self.started_at = timezone.now()
            self.save(update_fields=['status', 'started_at'])

    def complete(self):
        if self.status in (self.STATUS_ASSIGNED, self.STATUS_IN_PROGRESS):
            self.status = self.STATUS_DONE
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'completed_at'])


