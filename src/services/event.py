from src.models.models import Event, User, Participants, ParticipantData
import jwt
from fastapi import Header, Depends
from fastapi import Response, APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from src.routes.userAuth import get_current_user
from datetime import datetime, timezone, timedelta
import json
from bson import ObjectId  
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mongoengine import Q
import os
import gspread
from google.auth import exceptions, credentials
from oauth2client.service_account import ServiceAccountCredentials
from dateutil.relativedelta import relativedelta
import pytz
gc = gspread.service_account(filename="credentials/service-account-key.json")

# sh_key = os.environ.get("SH_KEY")
sh = gc.open_by_key('1BU-VckOH-wEX-xGqgUo21f0o1MKD-I-c6LfTQWWTYtc')

current_utc_time = datetime.utcnow()

def spreadsheet(eventName: str):
    try:
        worksheet_current = sh.add_worksheet(title=eventName, rows=100, cols=20)
        worksheet_current.append_row(['Participant Email',' ','Participant Name',' ','Participant Phone No',' ','Participant DOB'], table_range='A1')
        return worksheet_current.url

    except Exception as e:
        return {"message ","Unable to add to the spreadsheet"}


def create_event(event_data: 'event_data', current_user: 'current_user'):
    user_id = current_user.userId
    url = spreadsheet(event_data.eventName)
    print(type(url))
    if isinstance(url, str): 
        event = Event(
            eventName=event_data.eventName,
            eventDesc=event_data.eventDesc,
            user=user_id,
            eventDate=event_data.eventDate,
            eventMinAge=event_data.eventMinAge,
            url=url
        )
        event.save()
    else:
        return {"message": "Unable to add the spreadsheet url"}

def check_in(event_id: 'event_id', participant_id: 'participant_id'):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return {"message": "Event does not exist."}

    participant_data = None
    for pd in event.participants:
        if str(pd.participant_ref.id) == participant_id:
            participant_data = pd
            break

    if not participant_data:
        return {"message": "Participant not found."}

    if participant_data.participant_checked_in:
        return {"message": "You have already checked-in."}

    event_date = event.eventDate
    current_time = datetime.utcnow()

    if current_time >= event_date:
        time_threshold = timedelta(seconds=195170)
        time_difference = event_date - current_time
        if time_difference <= time_threshold:
            participant_data.participant_checked_in = True
            event.save()
            return {"message": "Participant checked in successfully."}
        else:
            return {"message": "Event check-in time has passed."}
    else:
        return {"message": "Event has not started yet."}

def join_event(event_id: str, new_participant: 'NewParticipant'):
    try:
        event = Event.objects.get(id=event_id)
    except Exception as e:
        return {"message": "Event does not exist."}

    if len(event.participants) > 0:
        for thisp in event.participants:
            if str(thisp.participant_ref.participant_email) == new_participant.participant_email:
                return {"message": "You have already joined the event"}
                break

    if current_utc_time > event.eventDate:
        return {"message": "This event has passed."}
    else:
        age = relativedelta(current_utc_time, new_participant.participant_dob)
        print("age is ", age.years)
        if age.years >= event.eventMinAge:
            participant = Participants(participant_email=new_participant.participant_email, participant_name=new_participant.participant_name, participant_number=new_participant.participant_number, participant_dob=new_participant.participant_dob)
            participant.save()
            
            participant_data = ParticipantData(participant_ref=participant)
            event.participants.append(participant_data)
            event.save()

            subject = 'Participation in an event'
            message = f'You participated in this event. Your Ticket ID is {participant.id}'
            to_email = participant.participant_email
            send_email(subject, message, to_email)
            get_worksheet(event.eventName, participant)
            return {"message": "You have joined the event"}
        else:
            return {"message": "You are not eligible to join this event"}


def get_worksheet(eventName: str, participant: 'participant'):
    worksheet = sh.worksheet(eventName)
    participant_dob_str = participant.participant_dob.strftime("%Y-%m-%d ")

    worksheet.append_row([participant.participant_email,' ',participant.participant_name,' ',participant.participant_number,' ', participant_dob_str], table_range='A2')

def get_event(event_id :str):
    try:
        event = json.loads(Event.objects.get(id = event_id).to_json())
        return event
    except Event.DoesNotExist:
        return {"message": "Event does not exist."} 

def get_participant(participant_id :str):
    try:
        participant = json.loads(Participants.objects.get(id = participant_id).to_json())
        return participant
    except Event.DoesNotExist:
        return {"message": "Event does not exist."} 


def get_all_upcoming_events():
    all_events = Event.objects.all()
    events_data = []
    # current_utc_time = datetime.utcnow()
    # formatted_time = current_utc_time.strftime("%Y-%m-%d %H:%M:%S")

    for event in all_events:
        if(current_utc_time<event.eventDate):
            event_data = {
                "event_id": str(event.id),
                "eventName": event.eventName,
                "eventDesc": event.eventDesc,
                "eventDate": event.eventDate.strftime("%Y-%m-%d %H:%M:%S"),
                "eventMinAge": event.eventMinAge,
                "url": event.url
            }
            events_data.append(event_data)
        
    return Response(content=json.dumps(events_data), media_type="application/json")


def get_all_events():
    all_events = Event.objects.all().to_json()
    event_list = json.loads(all_events)
    events_data = []
    current_utc_time = datetime.utcnow()
    formatted_time = current_utc_time.strftime("%Y-%m-%d %H:%M:%S")

    for event in event_list:
        event_data = {
            "event_id": event["_id"]["$oid"],
            "eventName": event["eventName"],
            "eventDesc": event["eventDesc"],
            "eventDate": event["eventDate"],
            "eventMinAge": event["eventMinAge"],
            "url": event["url"]
        }
        events_data.append(event_data)
    return Response(content=json.dumps(events_data), media_type="application/json")   


def delete_event(event_id: str):
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        return True
    except Exception as e:
        return False

def delete_event_main(event_id: 'event_id', current_user: 'current_user'):
    try:
        event = json.loads(Event.objects.get(id = event_id).to_json())

        if event["user"]["$oid"] != current_user.userId:
            raise HTTPException(status_code=403, detail="Unauthorized Access")
        result = delete_event(event_id)

        if result:
            return {"message": "Event Deleted"}
        else:
            return {"message":"Failed to delete"}
            
    except Exception as e:
        return {"message":"Event does not exist"}


def send_email(subject, message, to_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    # sender_email = 'priyankaghansela22@gmail.com'  # Replace with your email address
    # sender_password = 'mykdbcbamvohmfxi'
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password =os.environ.get("SENDER_PASS")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return {"Email sent successfully"}
    except Exception as e:
        return {"message": "Error sending email:"}

