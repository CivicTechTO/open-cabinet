import requests
import ALERTCONFIG

def send_confirmation(text, email, subject):
    return requests.post(
        ALERTCONFIG.POST_ADDR,
        auth=("api", ALERTCONFIG.MAILGUN_API ),
        data={"from": ALERTCONFIG.ALERTS_EMAIL,
              "to": [ email ],
              "subject": subject,
              "text": text})