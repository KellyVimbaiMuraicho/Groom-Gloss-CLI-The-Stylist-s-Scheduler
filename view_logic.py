import os
import pickle
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Handles the Google OAuth2 authentication process."""
    creds = None
    # token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Missing 'credentials.json' file in the project folder.")
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def get_upcoming_events(service):
    """Fetches the next 10 events from the primary calendar."""
    
    now = datetime.utcnow().isoformat() + 'Z' 
    print(f"DEBUG: Fetching events starting from {now}...")
    
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=now,
        maxResults=10, 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])

def is_busy(service, start_time, end_time, cal_id='primary'):
    """Checks for double-booking conflicts."""
    events_result = service.events().list(
        calendarId=cal_id,
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True
    ).execute()
    return len(events_result.get('items', [])) > 0

def book_appointment(service, event_id, client_email, service_note):
    """Links a client to an existing available slot."""
    
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    
    if event.get('attendees'):
        return {"success": False, "message": "This slot is already taken!"}

    
    if is_busy(service, event['start']['dateTime'], event['end']['dateTime'], 'primary'):
        return {"success": False, "message": "Conflict: You have an event at this time!"}

    event['summary'] = f"Salon Booking: {service_note}"
    event['attendees'] = [{'email': client_email}]
    
    service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return {"success": True, "message": "Successfully booked and synced to your calendar!"}

def cancel_appointment(service, event_id, client_email):
    """Removes a client from a booking and resets the slot."""
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    attendees = event.get('attendees', [])
    
    if not any(a['email'] == client_email for a in attendees):
        return {"success": False, "message": "Unauthorized: You did not book this slot."}

    event['summary'] = "Available Salon Slot"
    event['attendees'] = []
    
    service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return {"success": True, "message": "Booking successfully cancelled."}