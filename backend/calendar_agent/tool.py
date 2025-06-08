from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from common.tool_utils import get_google_service
import os
import json
from typing import Optional

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/contacts'
]

def get_calendar_service():
    return get_google_service(service_name='calendar', version='v3', scopes=SCOPES)

def get_people_service():
    return get_google_service(service_name='people', version='v1', scopes=SCOPES)

def get_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    keyword: Optional[str] = None,
    timezone: Optional[str] = None,
    calendar_id: str = 'primary',
    max_results: int = 10
) -> list:
    """
    Fetches events from the user's calendar with optional filters for date range, keyword, and timezone.

    Args:
        start_date (str, optional): Start date (YYYY-MM-DD or RFC3339 timestamp).
        end_date (str, optional): End date (YYYY-MM-DD or RFC3339 timestamp).
        keyword (str, optional): Keyword to search in event summary or description.
        timezone (str, optional): Timezone for the query (default 'UTC').
        calendar_id (str, optional): Calendar ID (default 'primary').
        max_results (int, optional): Maximum number of events to return.
    Returns:
        list: List of event dicts with details.
    """
    try:
        service = get_calendar_service()
        time_min = None
        time_max = None
        if start_date:
            if 'T' in start_date:
                time_min = start_date
            else:
                time_min = start_date + 'T00:00:00Z'
        if end_date:
            if 'T' in end_date:
                time_max = end_date
            else:
                time_max = end_date + 'T23:59:59Z'
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            q=keyword,
            timeZone=timezone
        ).execute()
        events = events_result.get('items', [])
        output = []
        for event in events:
            event_info = {
                'id': event.get('id'),
                'summary': event.get('summary'),
                'description': event.get('description'),
                'start': event.get('start'),
                'end': event.get('end'),
                'location': event.get('location'),
                'attendees': event.get('attendees', []),
                'status': event.get('status'),
                'creator': event.get('creator'),
                'organizer': event.get('organizer'),
            }
            output.append(event_info)
        return output
    except HttpError as error:
        return f"An error occurred: {error}"

def add_event(
    summary: str,
    start: str,
    end: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timezone: str = 'UTC',
    calendar_id: str = 'primary'
) -> dict:
    """
    Adds a new event to the user's calendar.
    
    Args:
        summary (str): Event title/subject (required)
        start (str): Start date/time in RFC3339 format (required)
        end (str): End date/time in RFC3339 format (required)
        description (str, optional): Detailed event description
        location (str, optional): Physical location or meeting link
        timezone (str, optional): Timezone identifier (default 'UTC')
        calendar_id (str, optional): Calendar ID (default 'primary')
    
    Returns:
        dict: The created event object or error message.
    """
    try:
        service = get_calendar_service()
        event = {
            'summary': summary,
            'start': {
                'dateTime': start,
                'timeZone': timezone
            },
            'end': {
                'dateTime': end,
                'timeZone': timezone
            },
        }
        if description:
            event['description'] = description
        if location:
            event['location'] = location
            
        created_event = service.events().insert(
            calendarId=calendar_id, 
            body=event
        ).execute()
        return created_event
    except HttpError as error:
        return f"An error occurred: {error}"

def cancel_event(event_id: str, calendar_id: str = 'primary'):
    """
    Cancels (deletes) an event from the user's calendar by event ID.
    Args:
        event_id (str): The event ID to cancel.
        calendar_id (str, optional): Calendar ID (default 'primary').
    Returns:
        dict: Status and event_id or error message.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return {'status': 'cancelled', 'event_id': event_id}
    except HttpError as error:
        return f"An error occurred: {error}"

def invite_attendee_to_event(event_id: str, attendee_email: str, calendar_id: str = 'primary'):
    """
    Invites an attendee (by email) to an existing event.
    Args:
        event_id (str): The event ID.
        attendee_email (str): The email address to invite.
        calendar_id (str, optional): Calendar ID (default 'primary').
    Returns:
        dict: The updated event object or error message.
    """
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        attendees = event.get('attendees', [])
        attendees.append({'email': attendee_email})
        event['attendees'] = attendees
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event, sendUpdates='all').execute()
        return updated_event
    except HttpError as error:
        return f"An error occurred: {error}"


def respond_to_event(event_id: str, response: str, calendar_id: str = 'primary'):
    """
    Accepts or declines an event invitation for the authenticated user.
    Args:
        event_id (str): The event ID.
        response (str): 'accepted' or 'declined'.
        calendar_id (str, optional): Calendar ID (default 'primary').
    Returns:
        dict: The updated event object or error message.
    """
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        attendees = event.get('attendees', [])
        # Try to get the user's email from token.json
        user_email = None
        token_path = os.path.join(os.path.dirname(__file__), '../token.json')
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                token_data = json.load(f)
                user_email = token_data.get('token_response', {}).get('email') or token_data.get('email')
        if not user_email:
            # fallback: try to get from attendees
            for att in attendees:
                if att.get('self'):
                    user_email = att.get('email')
                    break
        if not user_email:
            return 'Could not determine user email for RSVP.'
        updated = False
        for att in attendees:
            if att.get('email') == user_email:
                att['responseStatus'] = 'accepted' if response == 'accepted' else 'declined'
                updated = True
        if not updated:
            return 'User is not an attendee of this event.'
        event['attendees'] = attendees
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event, sendUpdates='all').execute()
        return updated_event
    except HttpError as error:
        return f"An error occurred: {error}"

def get_contact_info():
    """
    Returns the entire contact list using the Google People API.
    Args:
        None
    Returns:
        list: List of contacts with name and email.
    """
    try:
        service = get_people_service()
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1000,
            personFields='names,emailAddresses'
        ).execute()
        contacts = results.get('connections', [])
        contact_list = []
        for person in contacts:
            names = person.get('names', [])
            emails = person.get('emailAddresses', [])
            if names and emails:
                contact_list.append({
                    'name': names[0].get('displayName'),
                    'email': emails[0].get('value')
                })
        return contact_list
    except HttpError as error:
        return f"An error occurred: {error}"

def add_contact_info(name: str, email: str):
    """
    Adds a new contact to the user's Google Contacts using the People API.
    Args:
        name (str): The contact's name.
        email (str): The contact's email address.
    Returns:
        dict: The created contact object or error message.
    """
    try:
        service = get_people_service()
        contact_body = {
            'names': [{'givenName': name}],
            'emailAddresses': [{'value': email}]
        }
        new_contact = service.people().createContact(body=contact_body).execute()
        return new_contact
    except HttpError as error:
        return f"An error occurred: {error}"
