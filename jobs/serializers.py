"""
Serializers for jobs API.
"""
from rest_framework import serializers
from .models import Job, JobApplication, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/search views."""
    skills = SkillSerializer(many=True, read_only=True)
    salary_range_display = serializers.ReadOnlyField()
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'company_name', 'location', 'employment_type',
            'salary_min', 'salary_max', 'salary_range_display', 'is_remote',
            'job_description', 'skills', 'application_deadline', 'created_at',
            'status', 'application_count',
        ]

    def get_application_count(self, obj):
        return obj.applications.count()


class JobDetailSerializer(serializers.ModelSerializer):
    """Full serializer for create/update/detail views."""
    skills = SkillSerializer(many=True, read_only=True)
    skills_list = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )
    # Also accept comma-separated string from frontend
    required_skills = serializers.CharField(write_only=True, required=False)
    salary_range_display = serializers.ReadOnlyField()

    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'company_name', 'location', 'employment_type',
            'salary_min', 'salary_max', 'salary_range_display', 'is_remote',
            'job_description', 'key_responsibilities', 'requirements',
            'preferred_qualifications', 'years_of_experience', 'benefits_perks',
            'application_deadline', 'contact_email', 'skills', 'skills_list', 'required_skills',
            'status', 'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        skills_list = validated_data.pop('skills_list', [])
        required_skills = validated_data.pop('required_skills', '')
        if required_skills:
            skills_list.extend(s.strip() for s in required_skills.split(',') if s.strip())
        job = Job.objects.create(**validated_data)
        for name in skills_list:
            skill, _ = Skill.objects.get_or_create(name=name.strip())
            job.skills.add(skill)
        return job

    def update(self, instance, validated_data):
        skills_list = validated_data.pop('skills_list', None)
        required_skills = validated_data.pop('required_skills', None)
        if required_skills:
            skills_list = skills_list or []
            skills_list.extend(s.strip() for s in required_skills.split(',') if s.strip())
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skills_list is not None:
            instance.skills.clear()
            for name in skills_list:
                skill, _ = Skill.objects.get_or_create(name=name.strip())
                instance.skills.add(skill)
        return instance


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.job_title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'company_name', 'applicant', 'applicant_email',
            'cover_letter', 'resume_url', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
