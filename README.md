# DealerOS – CSV Reconciliation System

## About

DealerOS is a project I developed to compare transaction records from two different systems using CSV files.

The purpose is to identify differences between the records and make them easier to review through a dashboard. The application also handles multiple organizations, so reconciliation results are generated separately for each organization.

I used Django for the backend and React for the frontend.

## Technologies Used

- Python
- Django
- Django REST Framework
- SQLite
- React.js
- Vite
- JavaScript
- CSS
- HTML
- CSV processing

## Features

- Import data from Locations, System A and System B CSV files.
- Store imported records in a database.
- Normalize transaction references before comparing records.
- Identify records missing from System B.
- Detect duplicate entries in System B.
- Identify orphan records in System B.
- Compare transaction values and find mismatches.
- Handle transactions received in multiple parts.
- Exclude voided System A records from reconciliation.
- Filter results by discrepancy reason.
- Sort records by System A value.
- View reconciliation results separately for ORG-A and ORG-B.
- Preserve original CSV values when parsing invalid dates or numbers.

## Project Structure

```text
DealerOS/
│
├── backend/
│   ├── config/
│   ├── reconciliation/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_csv.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── data/
│   │   ├── locations.csv
│   │   ├── system_a.csv
│   │   └── system_b.csv
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── package-lock.json
│
├── requirements.txt
├── DECISIONS.md
├── README.md
└── .gitignore
```

## Running the Project

### Backend Setup

Open a terminal in the project root.

Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

Move into the backend directory:

```powershell
cd backend
```

Apply database migrations:

```powershell
python manage.py migrate
```

Import the CSV data:

```powershell
python manage.py import_csv
```

Start the backend server:

```powershell
python manage.py runserver
```

Backend URL: http://127.0.0.1:8000/

### Frontend Setup

Open another terminal:

```powershell
cd C:\Users\YASWANTH\Downloads\DealerOS\frontend
npm install
npm run dev
```

Frontend URL: http://localhost:5173/

## API Endpoint

The reconciliation API accepts an organization ID as a query parameter.

```text
GET /api/reconciliation/?org=ORG-A
GET /api/reconciliation/?org=ORG-B
```

The response includes the selected organization, total number of disagreements, and corresponding reconciliation records.

## How Reconciliation Works

The application first imports the three CSV files into the database.

During reconciliation, transaction references are normalized to handle formatting differences. System A and System B records are then compared using their transaction references.

For each organization, the application checks for missing records, duplicate references, orphan entries, and differences in transaction values.

When a transaction is received in multiple valid parts, the individual values are added together before comparison. Voided records from System A are excluded from the comparison.

The results are returned through a Django API and displayed in the React dashboard.

## Running Tests

The backend includes tests for the main reconciliation scenarios.

Run the following commands from the project root:

```powershell
cd backend
python manage.py test reconciliation
```

The test suite covers:

- Records missing from System B.
- Orphan entries in System B.
- Duplicate entries in System B.
- Mismatched transaction values.
- Valid split transactions.
- Organization-level data isolation.

All six tests are currently passing.

## What I Deliberately Did Not Build

I kept the implementation focused on CSV importing, reconciliation, and reviewing disagreements through the dashboard.

I did not implement user authentication, role-based permissions, automatic scheduled imports, background processing, email notifications, or production deployment infrastructure.

The organization filter currently uses an organization ID supplied through the API request. It demonstrates organization-based data separation but is not a replacement for authenticated tenant access control.

I prioritized the core reconciliation requirements instead of adding features outside the scope of the assignment.

## How I Worked With the AI Agent

I used an AI assistant to understand the requirements, plan the project structure, review the reconciliation logic, troubleshoot errors, and prepare test cases.

I reviewed the generated suggestions, implemented them, and verified the results by running the application and tests locally.

I also used the assistant to understand technical decisions rather than simply copying code without knowing how it worked.

One issue occurred when the assistant provided Git commands with paths relative to the project root, while my terminal was inside the backend directory. I noticed the pathspec error, checked my current directory, and corrected the paths.

## Reflection

### 1. One AI Agent Error I Noticed

The AI assistant once provided Git commands with incorrect file paths.  
I was inside the backend directory, but the commands assumed I was in the project root.  
Git returned a pathspec error because it could not find the specified file.  
I checked my current directory and reviewed the Git status output.  
I understood that the issue was with the relative paths, not the files.  
I corrected the paths based on my current directory.  
After that, I successfully staged and committed the changes.  
This taught me to verify AI-generated commands before executing them.

### 2. The Part I Am Least Confident About

I am least confident about handling every possible dirty CSV data scenario.  
The current importer handles invalid dates and numbers while preserving raw values.  
However, real-world CSV files may contain many unexpected formats and missing fields.  
I would like to test more cases involving invalid references and duplicate identifiers.  
I would also review the split-transaction validation more deeply.  
Tenant isolation is another area that needs improvement.  
Currently, records are filtered using the organization ID supplied in the API request.  
A production application should enforce this through authenticated user permissions.

### 3. What I Would Improve With One More Day

I would first implement authentication and stronger organization-level access control.  
The backend should identify the user's organization instead of trusting a query parameter.  
Next, I would add more tests for malformed CSV rows and invalid references.  
I would improve error reporting during CSV imports.  
I would also test incomplete and incorrectly labelled split transactions.  
I would review the API responses and dashboard for edge cases.  
Finally, I would improve validation to prevent incorrect reconciliation results.  
My priority would be reliability and data correctness rather than adding extra features.

## Technical Decisions

The main implementation decisions and alternatives considered are documented in [DECISIONS.md](DECISIONS.md).
