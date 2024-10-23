from twilio.rest import Client

class TwilioClient:

    def __init__(self, account_sid: str, auth_token: str, twilio_phone_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.twilio_phone_number = twilio_phone_number
        self.client = Client(account_sid, auth_token)