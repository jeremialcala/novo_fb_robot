# coding=utf-8
import os
import sys
import json
import requests
from flask import Flask, request
from flask import render_template
from flask import send_file

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/termandcond', methods=['GET'])
def termandcond():
    return render_template('termandcond.html')


@app.route('/buttons', methods=['GET'])
def buttons():
    return render_template('buttons.html')

@app.route('/img/hola', methods = ['GET'])
def hola():
    filename = '/templates/images/bot-greet.png'
    return send_file(filename, mimetype='image/gif')

@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                    log(messaging_event)
                    sender_id = messaging_event["sender"]["id"]  # the facebook ID
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    # message_text = "regist " # the message's text
                    log("Sender_id " + sender_id)
                    log("Recipient_id " + recipient_id)
                    # msg = sender_id

                    s = json_loads_byteified(get_user_by_id(sender_id))
                    # log(s)
                    r = json_loads_byteified(get_user_by_id(recipient_id))
                    # log(r)
                    key = "first_name"
                    if message_text.lower().find("regist") is not -1:
                        if key in r and not (r[key] is None):
                            msg = "Seguro " + r[key] + ", ¿deseas registrarte en TDM?"
                        elif key in s and not (s[key] is None):
                            msg = "Seguro " + s[key] + ", ¿deseas registrarte en TDM?"

                        # user = get_user_by_id(sender_id)
                        # log(user)
                        # send_message(recipient_id, msg)
                        # send_message(sender_id, msg)
                        send_termandc(sender_id)

                    elif message_text.lower().find("hola") is not -1:
                        if key in r and not (r[key] is None):
                            msg = "Hola " + r[key] + ", en que te puedo ayudar"
                        elif key in s and not (s[key] is None):
                            msg = "Hola " + s[key] + ", en que te puedo ayudar"

                        # msg = "Hola " + j['first_name'] + ", en que te puedo ayudar"
                        # msg = "Hola, en que te puedo ayudar"
                        send_message(sender_id, msg)

                    elif message_text.lower().find("saldo") is not -1:
                        if key in r and not (r[key] is None):
                            msg = "Hola " + r[key] + ",  Tu saldo es: 0.00"
                        elif key in s and not (s[key] is None):
                            msg = "Hola " + s[key] + ",  Tu saldo es: 0.00"
                        # msg = j['first_name'] + " Tu saldo es: 0.00"
                        # msg = " Tu saldo es: 0.00 "
                        send_message(sender_id, msg)

                    elif message_text.lower().find("acepto") is not -1:
                        msg = "Gracias " + \
                              ", para continuar ¿me indicas tu numero DNI?"
                        send_message(sender_id, msg)

                    elif message_text.lower().find("9") is not -1:
                        msg = "Gracias " + \
                              ", para continuar ¿me indicas tu numero Celular Movistar?"
                        send_message(sender_id, msg)

                    else:
                        # msg = "Gracias por tu Comentario " + j['first_name'] +\
                        msg = "Gracias por tu Comentario " + \
                              ", ¿requieres asistencia? o ¿tienes alguna duda con nuestro servicio?"
                        send_message(sender_id, msg)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    if message_text.lower().find("acepto") is not -1:
                        msg = "Gracias " + \
                              ", para continuar ¿me indicas tu numero DNI?"
                        send_message(sender_id, msg)
                    pass

    return "ok", 200


def get_user_by_id(user_id):
    url = "https://graph.facebook.com/USER_ID?&access_token="
    url = url.replace("USER_ID", user_id) + os.environ["PAGE_ACCESS_TOKEN"]
    # log(url)
    r = requests.get(url)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
        return r.status_code, r.text
    else:
        return r.text


def send_termandc(recipient_id):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        }, "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Tu Dinero Móvil",
                            "subtitle": "Para continuar con el proceso \n por favor acepta los terminos y condiciones del servicio",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "url": "https://damp-brushlands-76403.herokuapp.com/termandcond",
                                    "title": "Términos y Condiciones"
                                },
                                {
                                    "type": "postback",
                                    "title": "Acepto",
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    })
    log(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_message(recipient_id, message_text):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
            }
    # if it's anything else, return it in its original form
    return data


if __name__ == '__main__':
    app.run(debug=True)
