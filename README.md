Phase 1: Breaking Through the "Security Wall"
When I started, I had the code, but Google wouldn’t let me in. I kept hitting Error 403, which felt like standing in front of a locked door without a key.

To fix this, I had to become my own "Security Administrator" in the Google Cloud Console. I created a project, downloaded my Passport (credentials.json), and—the most important part—I added my email as a Test User. This told Google that even though my app wasn't "verified" for the public yet, it was safe for me to use. Once I logged in through the browser, the code generated token.pickle, my Digital Keycard, which now lets me bypass the login screen every time I run the app.

Phase 2: Connecting the "Waiter" (The API)
I realized that the Google Calendar API is like a waiter in a restaurant. I don't go into Google's "kitchen" to move data myself; instead, I wrote functions that give the waiter specific orders.

At first, my waiter was only looking at my Primary Calendar. I could see my personal life, but not my business slots. To fix this, I went into Google Calendar and created a brand new Salon Calendar. I found its unique "Address"— the Calendar ID—and pasted it into my code. Now, when I tell my script to "View," the API knows exactly which "Sign-up Sheet" to look at.

Phase 3: Creating the "Sync" Magic
The coolest part for me was figuring out how to make an appointment show up on two calendars at once. I didn't want to write code that copied the event; I wanted it to be a Live Connection.

I used the Attendees feature. In my book function, I told the API to find a specific event ID and add the client's email as a guest.

On the Salon side: The slot changes from "Available" to "Booked."

On the Client side: Because they are an "Attendee," Google automatically "teleports" that event onto their personal phone.

Phase 4: Making it Safe with "Cancel"
I knew that if I could book, I had to be able to undo it. I built a cancel function that acts as a "Digital Eraser." It checks the guest list to make sure the person canceling is actually the person who booked. If it matches, I have the code wipe the attendee list and rename the event back to "Available." This clears the client's phone and opens the chair back up for a new customer.

How My Files Work Together
My salon.py is my "Voice": It’s the interface where I type my commands. It captures what I want to do and sends those details to the brain.

My salon_engine.py is my "Brain": It holds my Salon ID and all the logic for talking to Google. It handles the security, the viewing, the booking, and the syncing.

I have now successfully built a professional-grade booking system that handles authentication, cloud storage, and real-time synchronization.
