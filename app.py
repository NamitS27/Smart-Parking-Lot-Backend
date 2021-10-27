import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from twilio.rest import Client
import datetime
import pyotp
import datetime
import json

pyotp_secret_key = "8asdhaiha234bjh2"

account_sid = 'SK6761b783847974fa88d602edbb6ded12'
auth_token = 'dNkQGyINLyc5zzFNNWNyHJsO15a31IHI'
client = Client(account_sid, auth_token)

parking_slots = [False]*8


def create_app():
    app = Flask(__name__)

    # @app.route('/login/')
    # def login():
    #     pass

    @app.route('/verify-otp/')
    def verify_otp():
        # data = request.data
        contact_number = request.form.get('contact_number')
        otp = request.form.get('otp')

        if pyotp.TOTP(contact_number).verify(otp):
            return jsonify({'status':'success'}), 200
        return jsonify({'status':'fail'}), 200

    @app.route('/send-otp/')
    def send_otp():
        contact_number = request.form.get('contact_number')
        otp = None
        try:
            otp = pyotp.TOTP(contact_number)
        except Exception as e:
            return jsonify({'error' : e}), 500
        body = f"Your login otp is {otp}"
        smsFrom = "+917600900163"
        message = client.messages.create(from_=smsFrom,body=body,to=contact_number)
        return jsonify({'status': 'success'}), 200

    @app.route('/send-sms/',methods=['POST'])
    def send_sms():
        data = json.loads(request.data)
        contact_number = data['contact_number']
        current_time = datetime.datetime.strftime(datetime.datetime.now(),"%H:%M:%S")
        body = f"You entered into the parking lot on {current_time}"
        smsFrom = "+917600900163"
        message = client.messages.create(from_=smsFrom,body=body,to=contact_number)
        return jsonify({'status': 'success'}), 200

    @app.route('/update-parking-lot/')
    def update_parking_lot():
        pass

    @app.route('/get-parking-lot/',methods=["POST"])
    def get_parking_lot():
        json_data = json.loads(request.data)
        print(json_data)
        return jsonify({'status': 'success'}), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
