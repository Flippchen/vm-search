from django.shortcuts import render, redirect
import ldap
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
import csv
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User


def index(request):
    return redirect('/csv')


@login_required
def csv_to_table(request):
    data = []
    search_term = request.GET.get('search', None)

    if search_term:
        search_terms: list = search_term.lower().split(",")
        reader = settings.READER
        for row in reader[1:]:
            if all(search_term in ''.join(row).lower() for search_term in search_terms):
                data.append(row)
        headers = reader[0]
        rows = data
        length = len(rows)
        return render(request, 'table2.html',
                      {'headers': headers, 'rows': rows, 'search_term': search_term, 'len': length})
    else:
        return render(request, 'table2.html', )


def ldap_login(request):
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # Get the username and password provided by the user
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate against ldap server
        try:
            conn = ldap.initialize(settings.LDAP_SERVER)
            conn.simple_bind_s("{}@ad.Test.com".format(username), password)
        # If authentication fails, return an 'invalid login' error message.
        except ldap.INVALID_CREDENTIALS:
            form.add_error(None, "Invalid username or password")
            return render(request, 'login.html', {'form': form})
        # If authentication succeeds, search for user in ldap
        search_base = "OU=Test,dc=ad,dc=Test,dc=com"
        search_filter = "(sAMAccountName={})".format(username)
        results = conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
        # If user is not found, return an 'Invalid Group' error message.
        if len(results) == 0:
            form.add_error(None, "Invalid Group")
            return render(request, 'login.html', {'form': form})
        # If user is found, check if user is in the right group
        try:
            groups = results[0][1]["memberOf"]
            if any("TEST GROUP".encode("utf-8") in item for item in groups):
                # If user is in the right group, try to get user from database
                try:
                    user = User.objects.get(username=username)
                except:
                    # If user is not in database, create user
                    user = User.objects.create_user(username=username, password="123")
                    user.save()
                # Authenticate against database
                user = authenticate(username=username, password="123")
                # Login user
                if user:
                    login(request, user)
                return redirect(reverse('csv_to_table'))
        except:
            form.add_error(None, "Invalid Group")
            return render(request, 'login.html', {'form': form})
    else:
        return HttpResponse("Invalid request")


def logout_view(request):
    logout(request)
    return redirect('login')
