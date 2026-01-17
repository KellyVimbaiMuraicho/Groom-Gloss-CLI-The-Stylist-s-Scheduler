import argparse
import sys
from salon_engine import get_calendar_service
from salon_engine import get_upcoming_events
from salon_engine import book_appointment 
from salon_engine import cancel_appointment

def main():
    
    print("--- Salon CLI System Initialized ---")
    
    parser = argparse.ArgumentParser(description="Groom & Gloss Salon CLI")
    subparsers = parser.add_subparsers(dest="command")

    
    subparsers.add_parser('view', help='View next 10 slots')

    
    book = subparsers.add_parser('book')
    book.add_argument('--id', required=True)
    book.add_argument('--service', required=True)
    book.add_argument('--email', required=True)

    
    cancel = subparsers.add_parser('cancel')
    cancel.add_argument('--id', required=True)
    cancel.add_argument('--email', required=True)

    args = parser.parse_args()

    
    if not args.command:
        print("Usage: python salon.py [view | book | cancel]")
        return

    print(f"Connecting to Google for: {args.command}...")
    service = get_calendar_service()

    if args.command == 'view':
        events = get_upcoming_events(service)
        if not events:
            print("No upcoming events found on your Google Calendar.")
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date'))
            summary = e.get('summary', 'No Title')
            print(f"ID: {e['id']} | Time: {start} | Status: {summary}")

    elif args.command == 'book':
        res = book_appointment(service, args.id, args.email, args.service)
        print(res['message'])

    elif args.command == 'cancel':
        res = cancel_appointment(service, args.id, args.email)
        print(res['message'])


if __name__ == "__main__":
    main()