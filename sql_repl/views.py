import re
import json
import os
import csv
import sqlite3
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UserQuery
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponse

# Helper to get the isolated database path for the current user/guest
def get_user_db_path(request):
    # Create a directory for user databases if it doesn't exist
    db_dir = os.path.join(settings.BASE_DIR, 'user_dbs')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    if request.user.is_authenticated:
        # Persistent file for logged-in users
        return os.path.join(db_dir, f'user_{request.user.id}.sqlite3')
    else:
        # Temporary file for guests based on session key
        if not request.session.session_key:
            request.session.create()
        return os.path.join(db_dir, f'guest_{request.session.session_key}.sqlite3')

def index(request):
    # 1. Cleanup on Page Refresh (GET request)
    if request.method == "GET":
        # If guest, delete their specific database file to reset the session
        if not request.user.is_authenticated:
            db_path = get_user_db_path(request)
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except OSError:
                    pass # File might be in use or already deleted

    # 2. Handle Query Execution (POST)
    if request.method == "POST":
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        query = request.POST.get('query', '')
        results = None
        columns = None
        error = None
        
        # Connect to the USER'S isolated database
        db_path = get_user_db_path(request)
        conn = None
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Execute Query
            cursor.execute(query)
            
            # Fetch results if it's a SELECT-type query
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
            
            # Commit changes (Important for SQLite file persistence)
            conn.commit()

            # Save history to MAIN Django DB (Metadata only)
            new_history = None
            if request.user.is_authenticated:
                q = UserQuery.objects.create(user=request.user, code=query)
                new_history = {
                    'timestamp': q.created_at.strftime("%b %d, %Y %H:%M"),
                    'code_preview': (q.code[:60] + '..') if len(q.code) > 60 else q.code,
                    'raw_code': q.code
                }
            else:
                # GUEST: Generate history for display only
                new_history = {
                    'timestamp': datetime.now().strftime("%b %d, %Y %H:%M"),
                    'code_preview': (query[:60] + '..') if len(query) > 60 else query,
                    'raw_code': query
                }

            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'columns': columns,
                    'results': results,
                    'error': None,
                    'new_history': new_history
                })

        except Exception as e:
            if is_ajax:
                return JsonResponse({'status': 'error', 'error': str(e)})
        finally:
            if conn:
                conn.close()

    # Fallback for standard page load
    history = None
    if request.user.is_authenticated:
        history = UserQuery.objects.filter(user=request.user)

    return render(request, 'repl/index.html', {
        'history': history,
        'query': '' 
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
    Returns JSON of tables by inspecting the ISOLATED database file.
    """
    tables_structure = []
    db_path = get_user_db_path(request)

    # If DB file doesn't exist yet (no queries run), return empty
    if not os.path.exists(db_path):
        return JsonResponse({'tables': []})

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables from sqlite_master
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Get columns for each table using PRAGMA
            cursor.execute(f"PRAGMA table_info({table})")
            # Row structure: (cid, name, type, notnull, dflt_value, pk)
            columns = [row[1] for row in cursor.fetchall()]
            tables_structure.append({
                'name': table,
                'columns': columns
            })
            
    except Exception:
        pass
    finally:
        if conn:
            conn.close()

    return JsonResponse({'tables': tables_structure})

def download_csv(request):
    """
    Executes the query and returns the results as a CSV file attachment.
    """
    if request.method == "POST":
        query = request.POST.get('query', '')
        
        db_path = get_user_db_path(request)
        if not os.path.exists(db_path):
            return HttpResponse("No database session found.", status=404)

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if not cursor.description:
                 return HttpResponse("Query does not return data to export.", status=400)

            # Create the CSV response
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="query_results.csv"'},
            )

            writer = csv.writer(response)
            # Write Headers
            writer.writerow([col[0] for col in cursor.description])
            # Write Data
            writer.writerows(cursor.fetchall())

            return response

        except Exception as e:
            return HttpResponse(f"Error generating CSV: {str(e)}", status=400)
        finally:
            if conn:
                conn.close()
    
    return redirect('index')