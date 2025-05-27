from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_events(date: str, calendar_id: str = 'primary'):
    """
    Fetches events for a given date (YYYY-MM-DD) from the user's calendar.
    """
    try:
        service = get_calendar_service()
        start = datetime.strptime(date, '%Y-%m-%d')
        end = start + timedelta(days=1)
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        return events
    except HttpError as error:
        return f"An error occurred: {error}"

def add_event(event_details: dict, calendar_id: str = 'primary'):
    """
    Adds a new event to the user's calendar.
    event_details should include: summary, start (datetime str), end (datetime str), description (optional), location (optional)
    """
    try:
        service = get_calendar_service()
        event = {
            'summary': event_details.get('summary'),
            'start': {'dateTime': event_details.get('start'), 'timeZone': event_details.get('timeZone', 'UTC')},
            'end': {'dateTime': event_details.get('end'), 'timeZone': event_details.get('timeZone', 'UTC')},
        }
        if 'description' in event_details:
            event['description'] = event_details['description']
        if 'location' in event_details:
            event['location'] = event_details['location']
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event
    except HttpError as error:
        return f"An error occurred: {error}"

def cancel_event(event_id: str, calendar_id: str = 'primary'):
    """
    Cancels (deletes) an event from the user's calendar by event ID.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return {'status': 'cancelled', 'event_id': event_id}
    except HttpError as error:
        return f"An error occurred: {error}"

def main():
    # 1. Add an event
    now = datetime.utcnow()
    start_time = now.replace(microsecond=0).isoformat() + 'Z'
    end_time = (now + timedelta(hours=1)).replace(microsecond=0).isoformat() + 'Z'
    event_details = {
        'summary': 'Test Event',
        'start': start_time,
        'end': end_time,
        'description': 'This is a test event',
        'location': 'Online',
        'timeZone': 'UTC'
    }
    print('Adding event...')
    created_event = add_event(event_details)
    print('Created event:', created_event)

    # 2. Get events for today
    today_str = now.strftime('%Y-%m-%d')
    print(f'Getting events for {today_str}...')
    events = get_events(today_str)
    print('Events:', events)

    # 3. Delete the event we just created
    if 'id' in created_event:
        print('Deleting the created event...')
        result = cancel_event(created_event['id'])
        print('Delete result:', result)
    else:
        print('Could not find event id to delete.')

if __name__ == "__main__":
    main()
