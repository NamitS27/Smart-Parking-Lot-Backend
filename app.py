import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import datetime
import json

parking_slots = [False] * 8

fixed_OTP = 346545


def create_app():
    app = Flask(__name__)

    @app.route("/verify-otp/")
    def verify_otp():
        contact_number = request.form.get("contact_number")
        otp = request.form.get("otp")

        # if pyotp.TOTP(contact_number).verify(otp):
        #     return jsonify({'status':'success'}), 200
        if otp == fixed_OTP:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "fail"}), 200

    """
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
    """

    @app.route("/update-parking-lot/", methods=["POST"])
    def update_parking_lot():
        slot_number = json.loads(request.data)["slot_number"]
        if not parking_slots[int(slot_number)]:
            parking_slots[int(slot_number)] = False
        else:
            return jsonify({"status": "Already present"}), 200
        return jsonify({"status": "success", "message": "Parking lot updated"}), 200

    @app.route("/get-parking-lot/", methods=["GET"])
    def get_parking_lot():
        return jsonify({"lotStatus": parking_slots}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
