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
from flask_cors import CORS, cross_origin

load_dotenv(find_dotenv())


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
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
    # @cross_origin()
    def verify_otp():
        '''
        This function is used to verify the OTP sent to the user's mobile number.

        requires raw json data in the form of:
        {
            "otp": "123456"
            "contact_number": "1234567890"
        }
        '''
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

        message = "Invalid OTP / OTP Expired" if otp != otp_to_verify else "No slots available"
        return jsonify({"status": "failure", "message": message}), 200

    def verify_otp_with_database(otp, otpDB, timestamp):
        '''
        This function is used to verify the OTP
        @param otp: OTP displayed to the user
        @param otpDB: OTP stored in the database
        @param timestamp: timestamp of the OTP generation
        '''
        if otp == otpDB:
            if (datetime.datetime.now() - timestamp).total_seconds() < 60:
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
    # @cross_origin()
    def update_parking_lot():
        '''
        This function is used to update the parking lot status.
        requires slot_number in the request arguments
        '''
        slot_number = request.args.get("slot_number")
        stat = request.args.get("status")
        status = True if int(stat) == 1 else False
        try:
            slot_number = int(slot_number)
            # print(stat, status)
            updated_result = db.parking_lot.update_one(
                {"slot": slot_number}, {"$set": {"isPresent": status}})
            # if updated_result.modified_count < 1:
            # return jsonify({"status": "success", "message": "Car is already present"}), 200
        except:
            return jsonify({"status": "Update Failed"}), 200
        return jsonify({"status": "success", "message": "Parking lot updated"}), 200

    @app.route("/get-parking-lot/", methods=["GET"])
    # @cross_origin()
    def get_parking_lot():
        '''
        This function is used to get the parking lot status.
        @return: json data of the parking lot status
        '''
        slots = parking_lot_collection.find({}, {"_id": False}).sort("slot")
        return jsonify({"status": "success", "slots": list(slots)}), 200

    @app.route("/generate-otp/", methods=["GET"])
    # @cross_origin()
    def generate_otp():
        otp = generate_random_otp()
        timestamp = datetime.datetime.now()
        otp_collection.insert_one(
            {"otp": otp, "generatedTimestamp": timestamp})
        return jsonify({"status": "success", "otp": otp}), 200

    def generate_random_otp():
        return random.randint(100000, 999999)

    @app.route("/fetch-otp-status/", methods=["GET"])
    # @cross_origin()
    def fetch_otp_details():
        response = otp_collection.find_one(
            {}, {"otp": 1, "generatedTimestamp": 1, "_id": 0})
        if not response:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "failure"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
