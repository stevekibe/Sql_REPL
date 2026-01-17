# SQL REPL - Collaborative SQL Playground

A web-based SQL Read-Eval-Print Loop (REPL) built with Django. This tool provides a safe, isolated environment for users to write, execute, and visualize SQL queries directly in the browser.

# Features

# Core Functionality

Interactive Editor: Built with CodeMirror 5 (Dracula theme) featuring syntax highlighting and line numbers.

Visual Schema Browser: A dynamic sidebar that lists all tables and their columns in your current session.

Query History: Automatically saves your executed queries to a sidebar list for easy re-running.

Data Export: Download query results instantly as a .csv file.

SQL Formatter: "Prettify" button to format messy SQL code automatically.

Session Management & Security

# Database Isolation:

Guests: Operate on a temporary SQLite database file that is physically deleted when the page is refreshed. No data persists.

Registered Users: Operate on a persistent, private SQLite database file unique to their user ID. Tables and data survive page reloads.

Collision Prevention: Since every user has their own database file, multiple users can create a table named users simultaneously without conflict.

AJAX Execution: Queries run asynchronously without reloading the page, providing a smooth app-like experience.

# Tech Stack

Backend: Python 3, Django 6.0.1

Database: SQLite (Dynamic multi-db routing)

Frontend: HTML5, CSS3, JavaScript (Fetch API)

Libraries:

codemirror (Editor)

sql-formatter (JS Library)

# Installation & Setup

Clone the repository:

git clone [https://github.com/stevekibe/sql-repl.git](https://github.com/stevekibe/sql-repl.git)
cd sql-repl


# Create a virtual environment:

python -m venv venv
 Windows
venv\Scripts\activate
 Mac/Linux
source venv/bin/activate

# Install dependencies:

pip install -r requirements.txt



Apply Migrations:
This sets up the main Django database for User Authentication and History metadata.

python manage.py makemigrations
python manage.py migrate


Run the Server:

python manage.py runserver


Access the App:
Open http://127.0.0.1:8000 in your browser.

# Usage Guide

Guest Mode

Open the home page.

Type CREATE TABLE test (id int, name text); and click Execute.

You will see the table appear in the "Tables" sidebar.

Type INSERT INTO test VALUES (1, 'Hello'); and execute.

Type SELECT * FROM test; to see the results.

Note: If you refresh the browser, the database is wiped clean.

User Mode

Click Sign Up to create an account.

Once logged in, any table you create is saved to user_dbs/user_<id>.sqlite3.

Refresh the page, log out, and log back in — your data remains intact.

Your query history is also saved permanently to the main database.

# Project Structure

core/: Main project configuration (settings, urls).

sql_repl/: The application logic.

views.py: Handles database isolation, query execution, and session cleanup.

models.py: Stores query history metadata.

templates/repl/index.html: The main single-page interface.

user_dbs/: (Auto-generated) Stores the isolated SQLite files for users and guests.

# Security Note

This project creates SQLite files dynamically based on session keys. In a production environment, ensure the user_dbs directory has appropriate write permissions and consider a periodic cleanup script for stale guest files.
