"""
API views for jobs (list, create, detail, search, apply).
"""
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from authentication.permissions import IsStaffUser

from .models import Job, JobApplication, Skill
from .serializers import JobListSerializer, JobDetailSerializer, JobApplicationSerializer


class JobViewSet(ModelViewSet):
    """
    Jobs API: list, create, retrieve, update, destroy.
    - List/search: GET /api/jobs/ (public, supports ?search=, ?location=, ?job_type=, ?salary_min=, ?my_jobs=1)
    - Create: POST /api/jobs/ (authenticated)
    - Detail: GET /api/jobs/{id}/
    - Update: PUT/PATCH /api/jobs/{id}/ (owner only)
    - Delete: DELETE /api/jobs/{id}/ (owner only)
    """
    queryset = Job.objects.all().select_related('created_by').prefetch_related('skills')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return JobListSerializer
        return JobDetailSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        # My jobs (job creator's own listings, including drafts)
        if self.request.user.is_authenticated and self.request.query_params.get('my_jobs'):
            qs = qs.filter(created_by=self.request.user)
        elif self.action == 'list':
            qs = qs.filter(status='active')
        elif self.action == 'retrieve':
            # Allow owner to view their draft; others only see active
            if self.request.user.is_authenticated:
                qs = qs.filter(Q(status='active') | Q(created_by=self.request.user))
            else:
                qs = qs.filter(status='active')
        # Search
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(job_title__icontains=search) |
                Q(company_name__icontains=search) |
                Q(location__icontains=search) |
                Q(job_description__icontains=search) |
                Q(skills__name__icontains=search)
            ).distinct()
        # Location filter
        location = self.request.query_params.get('location', '').strip()
        if location:
            qs = qs.filter(
                Q(location__icontains=location) | Q(is_remote=True)
            )
        # Job type filter
        job_type = self.request.query_params.get('job_type', '').strip()
        if job_type:
            qs = qs.filter(employment_type=job_type)
        # Salary range (simplified: min salary >= value)
        salary_min = self.request.query_params.get('salary_min')
        if salary_min:
            try:
                qs = qs.filter(salary_min__gte=float(salary_min))
            except ValueError:
                pass
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
        })


class JobApplicationViewSet(ModelViewSet):
    """
    Job applications: list (my applications), create (apply).
    - My applications: GET /api/jobs/applications/
    - Apply: POST /api/jobs/applications/
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user).select_related('job', 'applicant')

    def create(self, request, *args, **kwargs):
        job_id = request.data.get('job_id') or request.data.get('job')
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            job = Job.objects.get(id=job_id, status='active')
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found or closed'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response(
                {'error': 'You have already applied for this job'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data={
            'job': job.id,
            'cover_letter': request.data.get('cover_letter', ''),
            'resume_url': request.data.get('resume_url'),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(applicant=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminJobViewSet(ModelViewSet):
    """
    Staff-only: full CRUD on all jobs (any status, any owner).
    GET/POST /api/jobs/manage/  |  GET/PATCH/DELETE /api/jobs/manage/{id}/
    """
    queryset = Job.objects.all().select_related('created_by').prefetch_related('skills')
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return JobListSerializer
        return JobDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
        })

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
