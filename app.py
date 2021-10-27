import os
from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import Client
import datetime


def create_app():
    app = Flask(__name__)

    # @app.route('/login/')
    # def login():
    #     pass

    @app.route('/verify-otp/')
    def verify_otp():
        pass

    @app.route('/send-otp/')
    def send_otp():
        pass

    @app.route('/send-sms/')
    def send_sms(smsFrom,body,smsTo):
        account_sid = 'SK6761b783847974fa88d602edbb6ded12'
        auth_token = 'dNkQGyINLyc5zzFNNWNyHJsO15a31IHI'

        client = Client(account_sid, auth_token)

        body = f"You entered into the parking lot on {}"
        message = client.messages.create(from_=smsFrom,body=body,to=smsTo)

    @app.route('/update-parking-lot/')
    def update_parking_lot():
        pass

    @app.route('/get-parking-lot/')
    def get_parking_lot():
        pass


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
