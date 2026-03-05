from django.contrib import admin
from .models import Job, JobApplication, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'employment_type', 'location', 'status', 'created_at']
    list_filter = ['employment_type', 'status', 'is_remote']
    search_fields = ['job_title', 'company_name', 'location']
    filter_horizontal = ['skills']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'status', 'created_at']
    list_filter = ['status']
