from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Profile, UploadedMarkdownFile, ModifiedMarkdownFile, TaskTemplate, Assignment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(UploadedMarkdownFile)
class UploadedMarkdownFileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'uploaded_by', 'uploaded_at', 'create_modified_link')
    readonly_fields = ('uploaded_at',)

    def create_modified_link(self, obj):
        url = reverse('admin:skillup_app_modifiedmarkdownfile_add')
        return format_html('<a class="button" href="{}?original={}">Create modified copy</a>', url, obj.id)


@admin.register(ModifiedMarkdownFile)
class ModifiedMarkdownFileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'original', 'created_by', 'created_at')
    readonly_fields = ('file', 'created_at')
    fields = ('original', 'title', 'content', 'file', 'created_by', 'created_at')

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        original_id = request.GET.get('original')
        if original_id:
            try:
                orig = UploadedMarkdownFile.objects.get(pk=original_id)
                initial['original'] = orig.id
                initial['title'] = f'Modified: {orig}'
                initial['content'] = orig.read_text()
            except UploadedMarkdownFile.DoesNotExist:
                pass
        return initial

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'modified', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('template', 'student', 'status', 'assigned_at', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('template__title', 'student__username')
    readonly_fields = ('assigned_at', 'started_at', 'completed_at')
