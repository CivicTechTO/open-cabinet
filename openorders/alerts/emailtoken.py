from itsdangerous import URLSafeTimedSerializer
import ALERTCONFIG


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer( ALERTCONFIG.EMAIL_KEY )
    return serializer.dumps(email, salt=ALERTCONFIG.EMAIL_SALT )

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer( ALERTCONFIG.EMAIL_KEY )
    try:
        email = serializer.loads( token, salt=ALERTCONFIG.EMAIL_SALT, max_age=expiration )
    except:
        return False
    return email