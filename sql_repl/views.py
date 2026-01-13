from django.shortcuts import redirect, render
from django.db import connection
from .models import UserQuery
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm




def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def index(request):
    results = None
    columns = None
    error = None
    history = None # Initialize history
    query = request.POST.get('query', '')

    # Fetch history if user is logged in
    if request.user.is_authenticated:
        history = UserQuery.objects.filter(user=request.user)

    if request.method == "POST" and query:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
            
            if request.user.is_authenticated:
                UserQuery.objects.create(user=request.user, code=query)
                # Refresh history after saving new query
                history = UserQuery.objects.filter(user=request.user)
                
        except Exception as e:
            error = str(e)

    return render(request, 'repl/index.html', {
        'query': query,
        'results': results,
        'columns': columns,
        'error': error,
        'history': history  # Pass history to the template
    })