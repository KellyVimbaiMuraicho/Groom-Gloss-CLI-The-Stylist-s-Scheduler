import os, json, pickle
from datetime import datetime, timedelta
from googleapiclient.discovery import build

SALON_ID = 'b602c310b120403069e78e1cc2c9a9212f6dd7f1c7b5fda480211f23994f2e1f@group.calendar.google.com'
DATA_FILE = 'salon_cache.json'

def get_service():
    if not os.path.exists('token.pickle'):
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token: pickle.dump(creds, token)
    with open('token.pickle', 'rb') as token:
        return build('calendar', 'v3', credentials=pickle.load(token))

def is_authorized(email):
    """Rule: Only @student.wethinkcode.co.za emails are permitted."""
    return email.lower().endswith("@student.wethinkcode.co.za")

def sync_data(service):
    """Rule: Downloads exactly 7 days and overwrites local cache."""
    now = datetime.utcnow()
    t_min, t_max = now.isoformat() + 'Z', (now + timedelta(days=7)).isoformat() + 'Z'
    events = []
    for cal in ['primary', SALON_ID]:
        res = service.events().list(calendarId=cal, timeMin=t_min, timeMax=t_max, singleEvents=True).execute()
        for e in res.get('items', []):
            events.append({
                'id': e['id'],
                'summary': e.get('summary', 'No Title'),
                'start': e['start'].get('dateTime', e['start'].get('date')),
                'source': 'Student' if cal == 'primary' else 'Clinic',
                'attendees': [a.get('email') for a in e.get('attendees', [])]
            })
    data = {"last_sync": datetime.now().strftime("%Y-%m-%d"), "events": events}
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    return events

def get_data(service):
    """Rule: Check local file first before using Google API."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            cached = json.load(f)
        if cached.get("last_sync") == datetime.now().strftime("%Y-%m-%d"):
            return cached["events"]
    return sync_data(service)

def volunteer_for_slot(service, start_time, email):
    if not is_authorized(email): return "Unauthorized domain."
    
    start_dt = datetime.fromisoformat(start_time.replace('Z', ''))
    end_t = (start_dt + timedelta(minutes=30)).isoformat() + 'Z'
    check = service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_t).execute()
    if check.get('items'): return "Personal calendar conflict."
    
    event = {'summary': f"Volunteer: {email}", 'start': {'dateTime': start_time}, 'end': {'dateTime': end_t}, 'attendees': [{'email': email}]}
    service.events().insert(calendarId=SALON_ID, body=event).execute()
    sync_data(service)
    return "Slot opened for volunteering."

def book_session(service, event_id, email, issue):
    if not is_authorized(email): return "Unauthorized domain."
    
    event = service.events().get(calendarId=SALON_ID, eventId=event_id).execute()
    attendees = event.get('attendees', [])
    if len(attendees) == 0: return "No volunteer found."
    if len(attendees) >= 2: return "Slot already booked."
    
    event['summary'] = f"Clinic: {issue}"
    event['attendees'].append({'email': email})
    service.events().update(calendarId=SALON_ID, eventId=event_id, body=event).execute()
    sync_data(service)
    return "Clinic session booked."

def cancel_event(service, event_id, email):
    event = service.events().get(calendarId=SALON_ID, eventId=event_id).execute()
    attendees = [a.get('email') for a in event.get('attendees', [])]
    if email not in attendees: return "Not authorized for this slot."

    if attendees[0] == email: # Volunteer
        if len(attendees) > 1: return "Student has already booked you."
        service.events().delete(calendarId=SALON_ID, eventId=event_id).execute()
    else: # Student
        event['attendees'] = [{'email': attendees[0]}]
        event['summary'] = f"Volunteer: {attendees[0]}"
        service.events().update(calendarId=SALON_ID, eventId=event_id, body=event).execute()

    sync_data(service)
    return "Sucessfully Cancelled."