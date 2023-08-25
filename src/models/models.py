from mongoengine import Document,EmbeddedDocumentField,EmbeddedDocument, BooleanField, ReferenceField, StringField, ListField, DateTimeField, IntField, BooleanField, EmailField
import datetime

class User(Document):
    _id= IntField()
    email = EmailField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)

class Participants(Document):
    participant_email = EmailField(required=True)
    participant_name = StringField(required=True)
    participant_number = StringField(required=True)
    participant_dob = DateTimeField(required=True)
    # participant_checked_in = IntField(default = 0)

class ParticipantData(EmbeddedDocument):
    participant_ref = ReferenceField(Participants)
    participant_checked_in = BooleanField(default = False)

class Event(Document):
    event_id = StringField()
    eventName = StringField(required=True)
    eventDesc = StringField(required=True)
    eventMinAge = IntField(required=True)
    user = ReferenceField(User, required=True)
    participants = ListField(EmbeddedDocumentField(ParticipantData))
    # participant_checked_in = ListField(ReferenceField(Participants))
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    eventDate = DateTimeField(required=True)
    subsheet_id = StringField()
    url = StringField()
