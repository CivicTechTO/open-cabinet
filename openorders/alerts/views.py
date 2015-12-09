from flask import request, redirect, jsonify, url_for, render_template
from . import alerts_blueprint
from emailtoken import generate_confirmation_token, confirm_token
from validation import EmailSchema
from . import get_db
# from mailer import send_confirmation

@alerts_blueprint.route('subscribe', methods=['POST'])
def subscribe():
    email_json = request.get_json()
    data, errors = EmailSchema().load(email_json)
    ## VALIDATE EMAIL
    if bool(errors) is True:
        return jsonify( **errors )
    else:
        with get_db() as cur:
            cur.execute("""INSERT INTO users(email) SELECT %s 
                            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = %s) 
                            RETURNING email;""", ( data['email'], data['email'], ) )
            email = cur.fetchone()
            cur.connection.commit()
        if email[0] is not None:
            token = generate_confirmation_token(data['email']) 
            # TRIGGER EMAIL SENDING
            # confirm_url = url_for('alerts.confirm_email', token=token, _external=True)
            # html = render_template('user/activate.html', confirm_url=confirm_url)
            # subject = "Confirmation OpenOrders"
            # send_confirmation(html, user.email, subject)
            
            return 'A confirmation email has been sent'
        return 'Email already exists?'

@alerts_blueprint.route('confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = confirm_token(token, expiration=172800) # 2 days
    except:
        return 'Confirmation link is invalid/expired.'

    with get_db() as cur:
        cur.execute(""" UPDATE users SET confirmation = 1 WHERE email=%s;""", ( email, ) )
        return 'Subscription to OpenOrders daily digest confirmed.'

@alerts_blueprint.route('unsubscribe/<token>', methods=['GET'])
def unsubscribe(token):
    try:
        email = confirm_token(token, expiration=5270400) # 61 days
    except:
        return 'Unsubscribe link is invalid/expired.'

    with get_db() as cur:
        cur.execute(""" DELETE FROM users WHERE email=%s;""", ( email, ) )
        return 'You have successfully unsubscribed from the OpenOrders daily digest.'