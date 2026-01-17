import os
import pickle
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

hairdresser_calender_ID = 'b602c310b120403069e78e1cc2c9a9212f6dd7f1c7b5fda480211f23994f2e1f@group.calendar.google.com'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def get_upcoming_events(service):
    # Get current time in UTC format
    now = datetime.utcnow().isoformat() + 'Z' 
    events_result = service.events().list(
        calendarId= hairdresser_calender_ID , timeMin=now,
        maxResults=10, singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def book_appointment(service, event_id, client_email, service_note):
    event = service.events().get(calendarId= hairdresser_calender_ID, eventId=event_id).execute()
    
    # Check if someone already booked it
    if event.get('attendees'):
        return {"success": False, "message": "Slot already taken!"}

    # Update event details
    event['summary'] = f"Salon: {service_note}"
    event['attendees'] = [{'email': client_email}]
    
    service.events().update(calendarId=hairdresser_calender_ID, eventId=event_id, body=event).execute()
    return {"success": True, "message": "Booked & Synced successfully!"}

def cancel_appointment(service, event_id, client_email):
    """Cancels a booking by removing attendees and resetting the title."""
    try:
        event = service.events().get(calendarId=hairdresser_calender_ID, eventId=event_id).execute()
        
        
        attendees = event.get('attendees', [])
        if not any(a['email'] == client_email for a in attendees):
            return {"success": False, "message": "Error: This email did not book this appointment."}

        
        event['summary'] = 'Available Salon Slot'
        event['attendees'] = [] 
        
        service.events().update(
            calendarId=hairdresser_calender_ID, 
            eventId=event_id, 
            body=event,
            sendUpdates='all'
        ).execute()
        
        return {"success": True, "message": "Appointment canceled. The slot is now available again."}
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}