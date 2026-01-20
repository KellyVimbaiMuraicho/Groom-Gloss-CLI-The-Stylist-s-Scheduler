import clinic_engine as engine
from datetime import datetime

def display_slots(my_email):
    service = engine.get_service()
    events = engine.get_data(service)
    events.sort(key=lambda x: x['start'])

    print(f"\n{'REF':<4} | {'DATE':<12} | {'TIME':<8} | {'ROLE':<12} | {'STATUS'}")
    print("-" * 75)
    
    mapping = {}
    for i, e in enumerate(events):
        letter = chr(97 + i) if i < 26 else str(i)
        mapping[letter] = e['id']
        dt = datetime.fromisoformat(e['start'].replace('Z', ''))
        attendees = e.get('attendees', [])

        # Role Logic
        role = "---"
        if my_email in attendees:
            role = "⭐ VOLUNTEER" if attendees[0] == my_email else "🎓 STUDENT"

        # Status Logic
        if e['source'] == 'Student': status = "🟦 PERSONAL"
        elif len(attendees) >= 2: status = "🔴 BOOKED"
        elif len(attendees) == 1: status = "🟢 READY"
        else: status = "⚪ OPEN"

        print(f"({letter})  | {dt.strftime('%a %d %b'):<12} | {dt.strftime('%H:%M'):<8} | {role:<12} | {status}")
    
    print("-" * 75)
    return mapping

def main():
    service = engine.get_service()
    print("👋 Welcome to the WeThinkCode_ Coding Clinic")
    my_email = input("Please enter your @student.wethinkcode.co.za email: ").strip().lower()

    # Domain Validation
    if not engine.is_authorized(my_email):
        print("\n🚫 ACCESS DENIED: Only WeThinkCode_ students can use this tool.")
        return

    while True:
        print(f"\nLogged in as: {my_email}")
        print("1. View Schedule\n2. Volunteer\n3. Book\n4. Cancel\n5. Exit")
        choice = input("Select: ")

        if choice == '1':
            display_slots(my_email)
        elif choice == '2':
            d, t = input("Date (YYYY-MM-DD): "), input("Time (HH:MM): ")
            print(engine.volunteer_for_slot(service, f"{d}T{t}:00Z", my_email))
        elif choice == '3':
            refs = display_slots(my_email)
            pick = input("\nLetter of 🟢 READY slot to book: ").lower()
            if pick in refs:
                note = input("Coding problem: ")
                print(engine.book_session(service, refs[pick], my_email, note))
        elif choice == '4':
            refs = display_slots(my_email)
            pick = input("\nLetter to cancel: ").lower()
            if pick in refs:
                print(engine.cancel_event(service, refs[pick], my_email))
        elif choice == '5':
            break

if __name__ == "__main__":
    main()