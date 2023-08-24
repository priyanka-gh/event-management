from src.models.models import Event, User, Participants
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.services.userAuth import get_current_user
import datetime
from src.services.event import check_in, send_email,get_all_events, delete_event_main, get_all_upcoming_events, create_event, get_event, delete_event, join_event
import json
from fastapi import Response, APIRouter, Depends, HTTPException, Query, status

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}}
)

class NewEvent(BaseModel):
    eventName: str
    eventDesc: str
    eventDate: datetime.datetime
    eventMinAge: int

class NewParticipant(BaseModel):
    participant_email: str
    participant_name: str
    participant_number: str
    participant_dob: datetime.datetime

@router.post("/create-event", dependencies=[Depends(get_current_user)])
async def create_this_event(event_data: NewEvent, current_user: dict = Depends(get_current_user)):
    return create_event(event_data, current_user)


@router.post("/join-event/{event_id}")
async def join_this_event(event_id: str, new_participant: NewParticipant):
    return join_event(event_id, new_participant)

@router.post("/check-in/{event_id}/{participant_id}")
async def check_in_event(event_id: str, participant_id: str):
    return check_in(event_id, participant_id)

@router.get("/get-event/{event_id}")
def get_this_event(event_id :str):
    return get_event(event_id)  

@router.get("/get-all-events")
def get_upcoming_events(includePastEvents : bool = False):
    if not includePastEvents:
        return get_all_upcoming_events()
    else:
        return get_all_events()

@router.delete("/delete-event/{event_id}",dependencies=[Depends(get_current_user)])
def delete_this_event(event_id: str, current_user: dict = Depends(get_current_user)):
    return delete_event_main(event_id, current_user)