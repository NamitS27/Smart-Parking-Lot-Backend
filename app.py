import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import datetime
import json
import pymongo as pm
import ssl
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
import re
from dotenv import load_dotenv, find_dotenv
import random

load_dotenv(find_dotenv())


def create_app():
    app = Flask(__name__)
    database = os.environ.get('DATABASE')
    user = os.environ.get('USER')
    password = os.environ.get('PASSWORD')
    MONGO_URI = f"mongodb+srv://{user}:{password}@iot.yjg6l.mongodb.net/{database}?retryWrites=true&w=majority"
    try:
        mongo = pm.MongoClient(MONGO_URI, ssl_cert_reqs=ssl.CERT_NONE)
        db = mongo.parking_lot
        parking_lot_collection = db.parking_lot
        otp_collection = db.otp
    except Exception as e:
        print(e)

    @app.route("/verify-otp/", methods=["POST"])
    def verify_otp():
        data = json.loads(request.data)
        contact_number = data["contact_number"]
        otp = data["otp"]
        otpDB = None
        # if pyotp.TOTP(contact_number).verify(otp):
        #     return jsonify({'status':'success'}), 200
        try:
            slots = parking_lot_collection.find({"isPresent": True})
            slots = list(slots)
            otpDB = otp_collection.find_one(
                {}, {"otp": 1, "generatedTimestamp": 1, "_id": 0})
            otp_to_verify = otpDB["otp"]
            timestamp = otpDB["generatedTimestamp"]
        except Exception as e:
            print(e)
            return jsonify({'status': 'failure'}), 400

        if verify_otp_with_database(otp, otp_to_verify, timestamp) and len(slots) < 8:
            otp_collection.delete_one({"otp": otp_to_verify})
            return jsonify({"status": "success"}), 200

        message = "Invalid OTP / OTP Expired" if otp != fixed_OTP else "No slots available"
        return jsonify({"status": "failure", "message": message}), 200

    def verify_otp_with_database(otp, otpDB, timestamp):
        if otp == otpDB:
            if (datetime.datetime.now() - timestamp).total_seconds() < 300:
                return True
        return False

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

    @app.route("/update-parking-lot", methods=["POST"])
    def update_parking_lot():
        slot_number = request.args.get("slot_number")
        try:
            slot_number = int(slot_number)
            updated_result = db.parking_lot.update_one(
                {"slot": slot_number}, {"$set": {"isPresent": True}})
            if updated_result.modified_count < 1:
                return jsonify({"status": "success", "message": "Car is already present"}), 200
        except:
            return jsonify({"status": "Update Failed"}), 200
        return jsonify({"status": "success", "message": "Parking lot updated"}), 200

    @app.route("/get-parking-lot/", methods=["GET"])
    def get_parking_lot():
        slots = parking_lot_collection.find({}, {"_id": False})
        return jsonify({"status": "success", "slots": list(slots)}), 200

    @app.route("/generate-otp/", methods=["GET"])
    def generate_otp():
        otp = generate_random_otp()
        timestamp = datetime.datetime.now()
        otp_collection.insert_one(
            {"otp": otp, "generatedTimestamp": timestamp})
        return jsonify({"status": "success", "otp": otp}), 200

    def generate_random_otp():
        return random.randint(100000, 999999)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
