# Technical Decisions

## 1. Django for the Backend
Decision: I used Django with Django REST Framework.

Alternative: Node.js with Express.

Reason: Django provides an organized backend structure, ORM, migrations, and built-in testing support.

## 2. Relational Database Models
Decision: I used relational models for locations, System A records, and System B entries.

Alternative: Storing imported CSV rows directly as JSON files.

Reason: The records have relationships, and relational models make organization-based filtering easier.

## 3. Preserve Original CSV Values
Decision: I store parsed values separately from their original raw values.

Alternative: Rejecting rows containing invalid dates or numbers.

Reason: Invalid source values should not be silently lost during import.

## 4. Normalize References
Decision: I normalize record references before comparing the two systems.

Alternative: Comparing reference strings exactly as they appear in the CSV files.

Reason: Formatting differences should not create false mismatches.

## 5. Separate Reconciliation Logic
Decision: I placed reconciliation logic in a separate service function.

Alternative: Writing all comparison logic inside the API view.

Reason: This makes the logic easier to test, maintain, and reuse.