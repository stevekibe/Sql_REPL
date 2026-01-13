from django.shortcuts import render
from django.db import connection
from .models import UserQuery

def index(request):
    results = None
    columns = None
    error = None
    query = request.POST.get('query', '')

    if request.method == "POST" and query:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                # Only try to fetch if it's a SELECT-style query
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
            
            # Save if user is logged in
            if request.user.is_authenticated:
                UserQuery.objects.create(user=request.user, code=query)
                
        except Exception as e:
            error = str(e)

    return render(request, 'repl/index.html', {
        'query': query,
        'results': results,
        'columns': columns,
        'error': error
    })