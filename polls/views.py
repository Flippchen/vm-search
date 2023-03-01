from django.shortcuts import render, redirect
import ldap
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.
from django.http import HttpResponse
import csv
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required
def csv_to_table(request):
    data = []
    search_term = request.GET.get('search', '').lower()
    with open('data.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if search_term in ''.join(row).lower():
                data.append(row)
    headers = data[0]
    rows = data[1:]
    return render(request, 'table2.html', {'headers': headers, 'rows': rows, 'search_term': search_term})


def ldap_login(request):
    if request.method == 'POST':
        return redirect(reverse('csv_to_table'))
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
