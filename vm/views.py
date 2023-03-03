from django.shortcuts import render, redirect
import ldap
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.
from django.http import HttpResponse
import csv
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings


def index(request):
    return redirect('/csv')


# @login_required
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
    if request.method == 'POST':
        return redirect('csv_to_table')
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            ldap_server = 'ldap://example.com'
            ldap_dn = 'uid={},ou=users,dc=example,dc=com'.format(username)
            try:
                # ldap_conn = ldap.initialize(ldap_server)
                # ldap_conn.simple_bind_s(ldap_dn, password)
                a = 1
            except ldap.INVALID_CREDENTIALS:
                form.add_error(None, 'Invalid username or password')
            else:
                user = authenticate(request, username=username, password=password)
                user = a
                if user is not None:
                    login(request, user)
                    return redirect(reverse('csv'))
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
