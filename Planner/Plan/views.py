from django.shortcuts import render, redirect, get_object_or_404
import json
import os
import re
from .models import *
# from amadeus import Client, ResponseError, Location
from django.contrib import messages
# from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect , requires_csrf_token
# from .flight import Flight


# Create your views here.

# amadeus = Client(
#     client_id=os.environ.get("AMADEUS_CLIENT_KEY"),
#     client_secret=os.environ.get("AMADEUS_SECRET_KEY")
# )

# def plane_search(request):
#     origin = request.POST.get("Origin")
#     destination = request.POST.get("Destination")
#     departure_date = request.POST.get("Departuredate")
#     return_date = request.POST.get("Returndate")

#     kwargs = {
#         "originLocationCode": origin,
#         "destinationLocationCode": destination,
#         "departureDate": departure_date,
#         "adults": 1,
#     }

#     if origin and destination and departure_date:
#         try:
#             search_flights = amadeus.shopping.flight_offers_search.get(**kwargs)
#         except ResponseError as error:
#             messages.add_message(
#                 request, messages.ERROR, error.response.result["errors"][0]["detail"]
#             )
#             return render(request, "demo/home.html", {})
#         try:
#             country = search_flights.result['dictionaries'].get('locations').get(destination).get('countryCode')
#             travel_restrictions = amadeus.duty_of_care.diseases.covid19_report.get(countryCode=country)
#             documents = travel_restrictions.data['areaAccessRestriction']['declarationDocuments']['text']
#             covid_tests = ''
#             if 'text' in travel_restrictions.data['areaAccessRestriction']['travelTest']:
#                 covid_tests = travel_restrictions.data['areaAccessRestriction']['travelTest']['text']
#             else:
#                 covid_tests = travel_restrictions.data['areaAccessRestriction']['travelTest']['travelTestConditionsAndRules'][0]['scenarios'][0]['condition']['textualScenario']
#         except (ResponseError, KeyError, AttributeError) as error:
#             messages.add_message(
#                 request, messages.ERROR, 'No results found'
#             )
#             return render(request, "demo/home.html", {})
#         search_flights_returned = []
#         response = ""
#         for flight in search_flights.data:
#             offer = Flight(flight).construct_flights()
#             search_flights_returned.append(offer)
#             response = zip(search_flights_returned, search_flights.data)

#         return render(
#             request,
#             "results.html",
#             {
#                 "response": response,
#                 "origin": origin,
#                 "destination": destination,
#                 "departureDate": departure_date,
#                 "returnDate": return_date,
#                 "country": country,
#                 "documents": documents,
#                 "covid_tests": covid_tests
#             },
#         )
#     return render(request, "home.html", {})

def parse_email(email):
    pattern = r'^f(\d{4})(\d{2,4})@([a-zA-Z0-9.-]+)\.bits-pilani\.ac\.in$'

    match = re.match(pattern, email)

    if match:
        batch = match.group(1)
        student_id = match.group(2)
        campus = match.group(3)
        return {
            'batch': batch,
            'id': student_id,
            'campus': campus
        }
    else:
        return None

def error_page(request):
    return render(request, 'Error.html')

@requires_csrf_token
def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = User.objects.filter(username = username)

        if user.exists():
            messages.info(request, 'Username already taken')
            return redirect('/register/')
        
        if not email.endswith("bits-pilani.ac.in"):
            messages.error(request, 'Kindly use bits email to signup')
            return redirect('/register/')
        
        bits_info = parse_email(email)

        if bits_info is None:
            messages.error(request, 'Kindly use bits student email to signup')
            return redirect('/register/')
        

        user = User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
        )

        user.set_password(password)
        user.save()
        
        messages.info(request , 'Account created successfully')
        return redirect('/register/')
    else:
        messages.error(request , 'Kindly use bits email to signup')
    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('/login/')

@csrf_protect
def login_page(request):
    if request.method == "POST":
        password = request.POST.get('password')
        email = request.POST.get('email')

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        user = User.objects.filter(email=email).first()
        
        user = authenticate(email=email, password=password)

        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('/login/')                   
        else:
            login(request, user)
            return redirect('/home/')

    return render(request, 'login.html')

@login_required(login_url = "/login/")
def create_group(request):
    if request.method == "POST":
        group_name = request.POST.get('group_name')
        leader_id = request.user.id

        #id not used just for the reason as i cannot find full id's of people with branch code so confusion might occur

        try:
            leader = User.objects.get(id=leader_id)
        except User.DoesNotExist:
            messages.error(request, f'User not found.')
            return redirect('/create_group/')

        group = Group.objects.create(name=group_name, leader=leader)
        group.members.add(leader) 

        messages.success(request, 'Group created successfully!')
        return redirect('/search_members/')

    return render(request, 'create_group.html')

@login_required
def search_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    queryset = None
    
    if request.GET.get('email'):
        email = request.GET.get('email')
        queryset = User.objects.filter(email=email)

    if not queryset:
        messages.error(request, 'No users found for given email')


    searched_user = queryset.first() if queryset else None

    is_searched_user_member = False
    if searched_user:
        is_searched_user_member = group.members.filter(pk=searched_user.pk).exists()

    memberset = [{'group': group, 'searched_user': searched_user, 'is_searched_user_member': is_searched_user_member}]

    return render(request, 'search_members.html', {'memberset': memberset, 'queryset': queryset})

@login_required(login_url="/login/")
def add_member(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    leader_id = request.user.id

    if leader_id != group.leader.id:
        messages.error(request, f'Unauthorized Access. Please login through leader email')
        return redirect('/error/')

    try:
        member = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, f'User with ID {user_id} not found.')
        return redirect(f'.search_members/')

    group.members.add(member)
    messages.success(request, f'{member.username} added to the group!')
    return redirect(f'/search_members/')

@login_required(login_url = "/login/")
def home_page(request):
    
    queryset = None
    
    if request.GET.get('name'):
        queryset = Group.objects.all()        
        name = request.GET.get('name')

        queryset = Group.objects.filter(name__icontains=name)
        if not queryset:
            messages.error(request, 'No groups found with this name')
        memberset = []
        for group in queryset:
            is_member = group.members.filter(pk=request.user.pk).exists()
            members_count = group.members.count()
            memberset.append({'group': group, 'members_count': members_count, 'is_member' : is_member})

    return render(request, 'home.html', {'memberset': memberset, })

@login_required(login_url = "/login/")
def send_join_request(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    is_member = group.members.filter(pk=request.user.pk).exists()

    if is_member:
        messages.success(request, f"Already A member of the group")
        return redirect('home')
    
    if request.method == 'POST':
        GroupJoinRequest.objects.create(group=group, requester=request.user)
        messages.success(request, f"Join request sent to {group.leader.username}")
        return redirect('home')

    return render(request, 'home.html', {'group': group})

@login_required(login_url = "/login/")
def profile(request):
    this_user = request.user
    
    groupset = Group.objects.all()

    memberset = []
    for group in groupset:
        is_member = group.members.filter(pk=request.user.pk).exists()
        members_count = group.members.count()
        memberset.append({'group': group, 'members_count': members_count, 'is_member' : is_member})

    queryset = Group.objects.filter(leader = this_user)

    leaderset = []
    for group in queryset:
        members_count = group.members.count()
        leaderset.append({'group': group, 'members_count': members_count})

    return render(request, 'profile.html', { 'user' : this_user , 'memberset' : memberset, 'leaderset' : leaderset})

@login_required(login_url = "/login/")
def leave_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.user == group.leader:
        if group.members.count() >= 1:
            new_leader = group.members.first()
            group.leader = new_leader
            group.save()
            messages.info(request, f"You have transferred leadership to {new_leader.username} and left the group")
        else:
            group.delete()
            messages.info(request, "Group has been removed due to insufficient members")
            return redirect('home')

    elif request.user in group.members.all():
        group.members.remove(request.user)
        messages.success(request, f"You have left the group {group.name}")
    
    else:
        messages.error(request, "You are not a member of this group")

    return redirect('home')

def group_details(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    members = group.members.all()

    is_leader = False
    if request.user == group.leader:
        is_leader = True

    context = {
        'group': group,
        'members': members,
        'is_leader' : is_leader
    }
    return render(request, 'group_details.html', context)

def kick_user(request, group_id, user_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.user != group.leader:
        messages.error(request, "You are not authorized to kick members from this group.")
        return redirect('home')
    

    user_to_kick = get_object_or_404(group.members, pk=user_id)

    if user_to_kick == group.leader:
        messages.error(request, "You cannot kick yourself from the group.")
        return redirect('home')

    group.members.remove(user_to_kick)
    messages.success(request, f"{user_to_kick.username} has been kicked from the group {group.name}")

    return redirect('home')

# def create_event(request):
