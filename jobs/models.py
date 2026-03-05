"""
Jobs models for freelancer and job creator platform.
"""
import uuid
from django.db import models
from django.conf import settings


class Skill(models.Model):
    """Skills that can be associated with jobs (e.g., React, Node.js, Python)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skills'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    """Job posting created by job creators."""
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('closed', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        null=True,
        blank=True,
    )

    # Required fields
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPES)
    job_description = models.TextField()
    application_deadline = models.DateField()
    contact_email = models.EmailField()

    # Optional fields
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    key_responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    preferred_qualifications = models.TextField(blank=True)
    years_of_experience = models.CharField(max_length=50, blank=True)  # e.g., "3-5 years"
    benefits_perks = models.TextField(blank=True)

    # Skills (many-to-many for filtering)
    skills = models.ManyToManyField(Skill, related_name='jobs', blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    @property
    def salary_range_display(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        if self.salary_min:
            return f"${self.salary_min:,.0f}+"
        return None


class JobApplication(models.Model):
    """Application submitted by a freelancer for a job."""
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications',
    )

    cover_letter = models.TextField(blank=True)
    resume_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_applications'
        ordering = ['-created_at']
        unique_together = [['job', 'applicant']]

    def __str__(self):
        return f"{self.applicant.email} → {self.job.job_title}"
