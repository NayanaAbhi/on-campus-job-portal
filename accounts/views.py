from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.contrib import messages
from .models import StudentProfile
from .models import User
from .serializers import RegisterSerializer, LoginSerializer

# API Views (Token Based)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "role": user.role
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# HTML Views (Login/Register)

def login_page(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            if user.role == 'student':
                return redirect('/dashboard/student/')
            elif user.role == 'manager':
                return redirect('/dashboard/manager/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def register_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)
        if role == 'student':
            return redirect('/dashboard/student/')
        elif role == 'manager':
            return redirect('/dashboard/manager/')
    return render(request, 'register.html')

# Dashboard Redirect Handler
@login_required
def dashboard_redirect(request):
    if request.user.role == 'manager':
        return redirect('/dashboard/manager/')
    else:
        return redirect('/dashboard/student/')

def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def update_canvas_url(request):
    if request.method == 'POST':
        url = request.POST.get('calendar_url')
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile.canvas_ics_url = url
        profile.save()
        messages.success(request, 'Canvas calendar URL updated successfully!')
    return redirect('student-dashboard-html')