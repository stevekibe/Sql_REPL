from django.shortcuts import render, redirect
from django.db import connection
from .models import UserQuery
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse

def index(request):
    results = None
    columns = None
    error = None
    history = None 
    query = request.POST.get('query', '')

    # Fetch history if user is logged in
    if request.user.is_authenticated:
        history = UserQuery.objects.filter(user=request.user)

    if request.method == "POST" and query:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                # Only fetch results if there is a description (e.g., SELECT queries)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
            
            if request.user.is_authenticated:
                UserQuery.objects.create(user=request.user, code=query)
                # Refresh history
                history = UserQuery.objects.filter(user=request.user)
                
        except Exception as e:
            error = str(e)

    return render(request, 'repl/index.html', {
        'query': query,
        'results': results,
        'columns': columns,
        'error': error,
        'history': history
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def schema_data(request):
    """
    Returns a JSON representation of the database tables and columns.
    Used for the sidebar visualization.
    """
    tables_structure = []
    
    # Use Django's introspection to get table names safely
    all_table_names = connection.introspection.table_names()
    
    # Filter out Django internal tables to keep the view clean for the user
    user_tables = [
        t for t in all_table_names 
        if not t.startswith('django_') 
        and not t.startswith('auth_') 
        and t != 'sqlite_sequence'
    ]

    with connection.cursor() as cursor:
        for table in user_tables:
            # Get columns for each table
            try:
                relations = connection.introspection.get_table_description(cursor, table)
                columns = [col.name for col in relations]
                tables_structure.append({
                    'name': table,
                    'columns': columns
                })
            except Exception:
                continue

    return JsonResponse({'tables': tables_structure})