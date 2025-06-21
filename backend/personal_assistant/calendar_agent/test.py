from datetime import datetime, timedelta
import tool

if __name__ == "__main__":
    # 1. Add an event with individual parameters
    print("Adding event...")
    now = datetime.utcnow()
    start_time = now.replace(microsecond=0).isoformat() + "Z"
    end_time = (now + timedelta(hours=1)).replace(microsecond=0).isoformat() + "Z"

    created_event = tool.add_event(
        summary="Test Event",
        start=start_time,
        end=end_time,
        description="This is a test event",
        location="Online",
        timezone="UTC",
    )
    print("Created event:", created_event)

    # 2. Invite attendees (if event creation was successful)
    if isinstance(created_event, dict) and "id" in created_event:
        attendee_emails = ["wenhaos0225@gmail.com", "wenhaos@umich.edu"]
        for email in attendee_emails:
            print(f"Inviting attendee {email} to event...")
            invite_result = tool.invite_attendee_to_event(created_event["id"], email)
            print(f"Invite result for {email}:", invite_result)

        # 3. Respond to the event as an attendee
        test_email = attendee_emails[0]
        print(f"Responding to event as attendee {test_email}...")
        rsvp_result = tool.respond_to_event(created_event["id"], "accepted")
        print("RSVP result:", rsvp_result)
    else:
        print("Could not find event id to invite or RSVP.")

    # 4. Get events for today
    today_str = now.strftime("%Y-%m-%d")
    print(f"Getting events for {today_str}...")
    events = tool.get_events(start_date=today_str, timezone="UTC")
    print("Events:", events)

    # 5. Delete the created event
    if isinstance(created_event, dict) and "id" in created_event:
        print("Deleting the created event...")
        delete_result = tool.cancel_event(created_event["id"])
        print("Delete result:", delete_result)
    else:
        print("Could not find event id to delete.")

    # 6. Add a contact
    new_contact_name = "Wenhao Song"
    new_contact_email = "wenhaos@umich.edu"
    print(f"Adding new contact: {new_contact_name}, {new_contact_email}...")
    add_contact_result = tool.add_contact_info(new_contact_name, new_contact_email)
    print("Add contact result:", add_contact_result)

    # 7. Get contact info
    print("Getting contact list...")
    contact_list = tool.get_contact_info()
    print("Contact list:", contact_list)
