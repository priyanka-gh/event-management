This FastAPI-based project provides an API for managing events, participants, and user authentication. It includes features such as creating events, checking in participants and joining events

**Event Creation:**
Receives a request to create a new event.
Creates a Google Sheets worksheet for the event.
Saves event details, including the spreadsheet URL.
Participant Joining an Event:

**Participant Joining an Event:**
Receives a request to join an event.
Verifies participant eligibility based on age.
Creates a new participant entry and updates the worksheet.
Sends an email to the participant with the Ticket ID.

**Participant Check-in:**
Receives a request to check-in a participant using Ticket ID.
Verifies event and participant existence.
Checks time difference and marks the participant as checked in.

**Event Deletion:**
Receives a request to delete an event.
Deletes can be deleted by the owner.

![Screenshot (144)](https://github.com/priyanka-gh/event-management/assets/72594113/88d600d5-71be-45ed-9eb7-4e5e85f54350)
![Screenshot (143)](https://github.com/priyanka-gh/event-management/assets/72594113/dc3748bf-2c47-4171-a3bb-0a61e51d1cba)
![Screenshot (145)](https://github.com/priyanka-gh/event-management/assets/72594113/a41afdcd-d9ba-4178-ba6c-b513707974e8)
![Screenshot (146)](https://github.com/priyanka-gh/event-management/assets/72594113/317fedc7-2998-40a1-9cd4-951feca3cd4a)
