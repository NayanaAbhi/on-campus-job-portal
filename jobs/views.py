from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from accounts.utils.calendar_parser import fetch_canvas_events
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .forms import AvailabilityForm
from .models import Job, Application, Shift, Availability
from django.urls import reverse
from .serializers import (
    JobSerializer,
    ApplicationSerializer,
    ShiftSerializer,
    AvailabilitySerializer
)

from accounts.permissions import IsManager, IsStudent

def home_view(request):
    return render(request, 'home.html')

class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager()]
        return [] 

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

@method_decorator(csrf_exempt, name='dispatch')
class ApplyToJobView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        if request.content_type == "application/x-www-form-urlencoded":
            job_id = request.POST.get("job_id")
            if job_id:
                Application.objects.create(student=request.user, job_id=job_id)
                return HttpResponseRedirect("/dashboard/student/")
        return super().post(request, *args, **kwargs)

class StudentApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)

# Shifts & Availability APIs

class ShiftListCreateView(generics.ListCreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager()]
        return [permissions.IsAuthenticated()]

class AvailabilityListCreateView(generics.ListCreateAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [IsStudent]
# Dashboard API Views (JSON)

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user
        shifts = Shift.objects.filter(student=student).order_by('start_time')
        total_hours = sum((s.end_time - s.start_time).total_seconds() for s in shifts) / 3600
        estimated_pay = total_hours * 15

        shift_data = [
            {
                "job": shift.job.title,
                "start": shift.start_time,
                "end": shift.end_time,
                "approved": shift.approved
            }
            for shift in shifts
        ]

        return Response({
            "total_hours_worked": round(total_hours, 2),
            "estimated_total_pay": round(estimated_pay, 2),
            "shifts": shift_data
        })

class ManagerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        manager = request.user
        jobs = Job.objects.filter(posted_by=manager)

        job_data = []
        for job in jobs:
            applications = Application.objects.filter(job=job)
            shifts = Shift.objects.filter(job=job)

            job_data.append({
                "job_id": job.id,
                "title": job.title,
                "department": job.department,
                "applications": [
                    {
                        "student": app.student.username,
                        "status": app.status,
                        "applied_at": app.applied_at
                    }
                    for app in applications
                ],
                "shifts": [
                    {
                        "student": shift.student.username,
                        "start": shift.start_time,
                        "end": shift.end_time,
                        "approved": shift.approved
                    }
                    for shift in shifts
                ]
            })

        return Response({
            "jobs_posted": len(jobs),
            "jobs": job_data
        })

# HTML Views 

@login_required
def student_dashboard_html(request):
    user = request.user
    
    # Use AvailabilityForm
    form = AvailabilityForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            availability = form.save(commit=False)
            availability.student = user
            availability.save()
            messages.success(request, "Availability added successfully!")
            return redirect(reverse('student-dashboard-html') + '?show=availability')
        else:
            print("Form Errors:", form.errors)  # Debug


    now_date = now()
    current_month_start = now_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get shifts with related job info
    shifts = user.shift_set.select_related('job').filter(start_time__gte=current_month_start).order_by('start_time')
    total_hours = sum([(s.end_time - s.start_time).total_seconds() for s in shifts]) / 3600
    estimated_pay = total_hours * 16

    # Get job applications
    applications = Application.objects.select_related('job').filter(student=user)
    applied_job_ids = applications.values_list('job_id', flat=True)

    department = request.GET.get("department")
    hours = request.GET.get("hours")

    # Filter base queryset
    available_jobs = Job.objects.exclude(id__in=applied_job_ids)
    if department:
        available_jobs = available_jobs.filter(department__icontains=department)
    if hours:
        try:
            available_jobs = available_jobs.filter(hours_per_week__lte=int(hours))
        except ValueError:
            pass

    # For dropdown filter options
    all_departments = Job.objects.values_list('department', flat=True).distinct()

    applied_jobs_with_status = [
        {
            'title': app.job.title,
            'department': app.job.department,
            'status': app.status,
            'applied_at': app.applied_at
        }
        for app in applications
    ]

    # Canvas calendar integration
    profile = getattr(user, 'studentprofile', None)
    canvas_ics_url = profile.canvas_ics_url if profile else None
    canvas_events = []

    if canvas_ics_url:
        try:
            canvas_events = fetch_canvas_events(canvas_ics_url)
        except Exception as e:
            print("Error parsing Canvas .ics file:", e)

    # Merge work shifts + Canvas events
    calendar_events = []
    for s in shifts:
        calendar_events.append({
            "title": s.job.title,
            "start": s.start_time.isoformat(),
            "end": s.end_time.isoformat()
        })
    availability_entries = Availability.objects.filter(student=user).order_by('-date')


    if canvas_ics_url:
        canvas_events = fetch_canvas_events(canvas_ics_url)
        calendar_events.extend(canvas_events)

    return render(request, 'student_dashboard.html', {
        'total_hours': round(total_hours, 2),
        'estimated_pay': round(estimated_pay, 2),
        'available_jobs': available_jobs,
        'applied_jobs_with_status': applied_jobs_with_status,
        'shifts': shifts,
        'canvas_ics_url': canvas_ics_url,
        'calendar_events': calendar_events, 
        'departments': all_departments,
        'selected_department': department,
        'selected_hours': hours,
        'availability_entries': availability_entries, 
    })
@require_http_methods(["GET", "POST"])
def jobs_available_view(request):
    jobs = Job.objects.all()
    applied_jobs = []

    # Filtering logic
    department = request.GET.get('department')
    hours = request.GET.get('hours')
    role = request.GET.get('role')

    if department:
        jobs = jobs.filter(department__icontains=department)
    if hours:
        try:
            jobs = jobs.filter(hours_per_week__lte=int(hours))
        except ValueError:
            pass
    if role:
        jobs = jobs.filter(posted_by__role=role)

    if request.user.is_authenticated:
        applied_jobs = Application.objects.filter(student=request.user).values_list('job_id', flat=True)

        if request.method == 'POST':
            job_id = request.POST.get('job_id')
            if job_id and int(job_id) not in applied_jobs:
                Application.objects.create(job_id=job_id, student=request.user)
                return redirect('jobs-available')

    # Get distinct department values for filter dropdown
    departments = Job.objects.values_list('department', flat=True).distinct()

    return render(request, 'jobs_available.html', {
        'jobs': jobs,
        'applied_job_ids': list(applied_jobs),
        'logged_in': request.user.is_authenticated,
        'departments': departments,
        'selected_department': department,
        'selected_hours': hours,
        'selected_role': role,
    })

@login_required
def manager_dashboard_html(request):
    manager = request.user
    jobs = Job.objects.filter(posted_by=manager).prefetch_related('application_set__student', 'shift_set__student')

    job_data = []
    all_shifts = [] 

    for job in jobs:
        job_applications = job.application_set.all()
        all_applications = Application.objects.select_related("student").all()
        shifts = job.shift_set.all()
        all_shifts.extend(shifts)  # Add to total shift list

        job_data.append({
            'job': job,
            'applications': job_applications,
            'shifts': shifts
        })
    all_availability = Availability.objects.select_related('student').all()

    return render(request, 'manager_dashboard.html', {
        'manager_name': manager.first_name or manager.username,
        'job_data': job_data,
        'shifts': all_shifts, 
        'availabilities': all_availability,
        'jobs': jobs,
        'applications': all_applications,

    })

@login_required
def manager_jobs_view(request):
    my_jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'job_listings.html', {'jobs': my_jobs})
    return redirect('my-jobs')

@login_required
def post_job_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        department = request.POST.get('department')
        description = request.POST.get('description')
        hours_per_week = request.POST.get("hours_per_week")

        if title and department and hours_per_week:
            Job.objects.create(
                title=title,
                department=department,
                hours_per_week=hours_per_week,
                description=description,
                posted_by=request.user
            )
            messages.success(request, "Job posted successfully!")
            return redirect(reverse('manager-dashboard-html') + '?show=postjob')
        else:
            return render(request, 'post_job_form.html', {'error': 'All fields are required.'})

    return render(request, 'post_job_form.html')

@login_required
def manager_applications_view(request):
    if request.method == "POST":
        app_id = request.POST.get("application_id")
        action = request.POST.get("action")  # accept or reject

        try:
            application = Application.objects.get(id=app_id)
            if action == "accept":
                application.status = "accepted"
            elif action == "reject":
                application.status = "rejected"
            application.save()
            messages.success(request, f"Application {action}ed successfully!")
        except Application.DoesNotExist:
            messages.error(request, "Application not found.")

        return redirect(reverse("manager-dashboard-html") + '?show=applications')

    jobs = Job.objects.filter(posted_by=request.user).prefetch_related("application_set__student")
    job_applications = []

    for job in jobs:
        applications = job.application_set.all()
        job_applications.append({
            'job': job,
            'applications': applications
        })

    return render(request, "manager_applications.html", {
        "job_applications": job_applications
    })

@login_required
def assign_shift_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        job_id = request.POST.get("job_id")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # Debug log
        print("Assigning shift to student:", student_id, "for job:", job_id)

        if student_id and job_id and start_time and end_time:
            Shift.objects.create(
                student_id=student_id,
                job_id=job_id,
                start_time=start_time,
                end_time=end_time,
                approved=False
            )
            return redirect(reverse("manager-dashboard-html") + '?show=shifts')

    applications = Application.objects.select_related("student").all()
    jobs = Job.objects.all()
    shifts = Shift.objects.select_related("student", "job").all()

    return render(request, "assign_shift.html", {
        "applications": applications,
        "jobs": jobs,
        "shifts": shifts,
    })


@login_required
def manager_availability_view(request):
    all_availability = Availability.objects.select_related("student").all()
    return render(request, "manager_availability.html", {
        "availabilities": all_availability,
    })


@login_required
def delete_availability(request, availability_id):
    availability = get_object_or_404(Availability, id=availability_id, student=request.user)
    availability.delete()
    return redirect(reverse('student-dashboard-html') + '?show=availability')


@login_required
def edit_shift_view(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)

    if request.method == "POST":
        shift.start_time = request.POST.get("start_time")
        shift.end_time = request.POST.get("end_time")
        shift.save()
        messages.success(request, "Shift updated.")
        return redirect('assign-shift')

    return render(request, 'edit_shift.html', {"shift": shift})


@login_required
@require_http_methods(["POST"])
def delete_shift_view(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    shift.delete()
    messages.success(request, "Shift deleted.")
    return redirect('assign-shift')