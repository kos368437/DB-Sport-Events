from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from .forms import SignUpForm, SignInForm
from .models import SportEvent


class MainView(View):
    def get(self, request, *args, **kwargs):
        all_events = SportEvent.objects.all()
        upcoming_events = SportEvent.objects.filter(event_date__gte = timezone.now()).order_by("event_date")
        paginator = Paginator(upcoming_events, 3)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'sport_event_app/home.html', context={
            'page_obj': page_obj
        })

class EventDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        event = get_object_or_404(SportEvent, url=slug)
        return render(request, 'sport_event_app/event_detail.html', context={
            'sport_event': event
    })

class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, 'sport_event_app/signup.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'sport_event_app/signup.html', context={
            'form': form,
        })


class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        return render(request, 'sport_event_app/signin.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                pass
        #     TODO: Raise exception
        return render(request, 'sport_event_app/signin.html', context={
            'form': form,
        })