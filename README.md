# DealerOS – CSV Reconciliation System

## About

DealerOS is a project I developed to compare transaction records from two different systems using CSV files.

The purpose is to identify differences between the records and make them easier to review through a dashboard. The application also handles multiple organizations, so reconciliation results are generated separately for each organization.

I used Django for the backend and React for the frontend.

## Technologies Used

- Python
- Django
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
│   │   └── urls.py
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

The response includes the selected organization, the total number of disagreements and the corresponding reconciliation records.

## How Reconciliation Works

The application first imports the three CSV files into the database.

During reconciliation, transaction references are normalized to handle formatting differences. System A and System B records are then compared using their transaction references.

For each organization, the application checks for missing records, duplicate references, orphan entries and differences in transaction values.

When a transaction is received in multiple valid parts, the individual values are added together before comparison. Voided records from System A are excluded from the comparison.

The results are returned through a Django API and displayed in the React dashboard.