Groom & Gloss is a terminal-based scheduling application designed for boutique salons. It bridges the gap between a stylist's availability and a client's busy schedule by synchronizing with Google Calendar.

The system treats "Stylists" as the primary resource creators (opening time slots) and "Clients" as the consumers (booking those slots). By using a local JSON cache, it ensures that even if the internet is spotty, users can still view the most recently downloaded schedule.

1.Technical Stack

Language: Python 3.10+

API: Google Calendar API v3

Auth: OAuth 2.0 (Google Auth Library)

Data Format: JSON (for local caching)

Libraries: google-api-python-client, google-auth-oauthlib, python-dateutil, tabulate (for pretty tables).

2. System Workflow (The "Flow")
Step 1: Initialization & Auth
When the user types python salon.py, the system checks for ~/.salon_token.pickle. If it doesn't exist, it initiates a browser-based OAuth flow. Once authenticated, the service object is created to talk to Google.

Step 2: The "Sync" Loop
The system fetches events for the next 7 days.

Logic: If cache_file is less than 1 hour old, read from disk.

Logic: If cache_file is older or missing, call service.events().list() and overwrite the local JSON.

Step 3: Action Execution

The user inputs a command like book or shift.

Validation: The script checks the local JSON to see if the slot is still AVAILABLE.

Execution: If valid, it sends a PATCH or UPDATE request to the Google Calendar API.

Confirmation: The script updates the local JSON immediately so the change is reflected without a second API call.
