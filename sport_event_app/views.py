import datetime

import django.db.models
import django_filters
import django_tables2 as tables
from django import forms
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.db import connection, ProgrammingError
from django.db.models import QuerySet, Sum, F, When, Value, Case, PositiveIntegerField, Q
from django.db.models.query import RawQuerySet
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from .forms import SignUpForm, SignInForm, QueryForm, EventSearchForm
from .models import SportEvent, Reservation


class MainView(View):
    def get(self, request, *args, **kwargs):
        all_events = SportEvent.objects.all()
        upcoming_events = SportEvent.objects.filter(event_date__gte=timezone.now()).order_by("event_date")
        paginator = Paginator(upcoming_events, 3)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'sport_event_app/home.html', context={
            'page_obj': page_obj,
        })


class EventDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        event = get_object_or_404(SportEvent, url=slug)
        # u_id = event.id
        # event = SportEvent.get_events().get(id=u_id)
        # event = SportEvent.objects.get(id=u_id)
        total_seats = event.get_total_seats_count()
        print(event)
        upcoming_events = SportEvent.get_upcoming_events().exclude(id=event.id)[:5]
        return render(request, 'sport_event_app/event_detail.html', context={
            'sport_event': event,
            'upcoming_events': upcoming_events,
            'total_seats': total_seats
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
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            print('INVALID')
        return render(request, 'sport_event_app/signup.html', context={
            'form': form,
        })


class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        return render(request, 'sport_event_app/signin.html', context={
            'form': form,
            'from': request.META.get('HTTP_REFERER')
        })

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        from_ = request.GET['from']
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(from_)
            else:
                form.add_error(error=forms.ValidationError(message='Неверный email или пароль'), field=None)
        return render(request, 'sport_event_app/signin.html', context={
            'form': form,
            'from': from_
        })


class QueryView(View):
    def get(self, request, *args, **kwargs):
        form = QueryForm()
        return render(request, 'sport_event_app/query.html', context={
            'form': form,
            'has_qs': False
        })

    def post(self, request, *args, **kwargs):
        form = QueryForm(request.POST)
        if form.is_valid():
            query = request.POST['query']
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]

        return render(request, 'sport_event_app/query.html', context={
            'form': form,
            'has_qs': True,
            'columns': columns,
            'rows': rows
        })


class QueryTableView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden()

        form = QueryForm(request.GET)
        table = None
        message = None
        has_qs = False
        if form.is_valid():
            query = request.GET['query']
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    try:
                        qs = cursor.fetchall()
                    except ProgrammingError:
                        qs = None
                        table = tables.Table(data=[])
                        message = f'Query {query} executed successfully'
                        has_qs = False
                    if qs:
                        has_qs = True
                        message = f'Query {query} executed successfully'
                        sequence = [col[0] for col in cursor.description]
                        columns = [(col, tables.Column()) for col in sequence]
                        list_of_dicts = [dict(zip(sequence, row)) for row in qs]
                        table = tables.Table(data=list_of_dicts, sequence=sequence,
                                             extra_columns=columns, template_name="sport_event_app/table.html",
                                             per_page_field='10')
                        table.paginate(page=request.GET.get("page", 1), per_page=5)

                except ProgrammingError as e:
                    form.add_error(error=e, field=None)
                    has_qs = False

        return render(request, 'sport_event_app/query.html', context={
            'form': form,
            'has_qs': has_qs,
            'table': table,
            'message': message
        })

    def post(self, request, *args, **kwargs):
        form = QueryForm(request.POST)
        table = None
        message = None
        if form.is_valid():
            query = request.POST['query']
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    try:
                        qs = cursor.fetchall()
                    except ProgrammingError:
                        qs = None
                        table = tables.Table(data=[])
                        message = f'Query {query} executed successfully'
                    if qs:
                        message = f'Query {query} executed successfully'
                        sequence = [col[0] for col in cursor.description]
                        columns = [(col, tables.Column()) for col in sequence]
                        list_of_dicts = [dict(zip(sequence, row)) for row in qs]
                        table = tables.Table(data=list_of_dicts, sequence=sequence,
                                             extra_columns=columns, template_name="sport_event_app/table.html", per_page_field='10')
                        table.paginate(page=request.GET.get("page", 1), per_page=5)
                except ProgrammingError as e:
                    form.add_error(error=e, field=None)

        return render(request, "sport_event_app/table_page.html", context={
            'form': form,
            'has_qs': True,
            'table': table,
            'message': message,
        })


class EventSearchView(View):
    def get(self, request, *args, **kwargs):
        form = EventSearchForm(request.GET)
        # events = SportEvent.objects.select_related('location').prefetch_related('reservation')

        events = SportEvent.get_upcoming_events()

        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        location = request.GET.get('location')
        have_seats = request.GET.get('have_seats')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        search_field = request.GET.get('search_field')

        # events = events.values('title').order_by('title') \
        #     .annotate(total_seats=Sum('reservation__seats_count')) \
        #     .annotate(total_seats=F('ticket_number') - F('total_seats')) \
        #     .annotate(total_seats=Case(
        #     When(total_seats=None, then=F('ticket_number')),
        #     default=F('total_seats'), output_field=PositiveIntegerField()
        # )).values('title', 'price', 'location__name', 'announce_text', 'total_seats', 'event_date', 'ticket_number')\
        #     .filter(event_date__gte=timezone.now())

        if from_date and from_date != '':
            events = events.filter(event_date__gte=datetime.datetime.strptime(from_date, "%d-%m-%Y").date())
        if to_date and to_date != '':
            events = events.filter(event_date__lte=datetime.datetime.strptime(to_date, "%d-%m-%Y").date())
        if location and location != '':
            events = events.filter(location__id=location)
        if have_seats and have_seats == 'on':
            events = events.filter(total_seats__gt=Value(0))
        if min_price and min_price != '':
            events = events.filter(price__gte=int(min_price))
        if max_price and max_price != '':
            events = events.filter(price__lte=int(max_price))
        if search_field and search_field != '':
            events = events.filter(Q(title__icontains=search_field) | Q(announce_text__icontains=search_field))

        # print(SportEvent.objects.all().values('id', 'title'))
        # form.fields['location'].choices = upcoming_events.values('location__name')
        # print(upcoming_events.order_by().values('location__name').distinct())

        paginator = Paginator(events, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'sport_event_app/event_search.html', context={
            'form': form,
            'page_obj': page_obj,
        })
