import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import datetime
import json
import pymongo as pm
import ssl
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
import re
from dotenv import load_dotenv, find_dotenv

parking_slots = [False] * 8

fixed_OTP = 346545

load_dotenv(find_dotenv())


def create_app():
    app = Flask(__name__)
    database = os.environ.get('DATABASE')
    user = os.environ.get('USER')
    password = os.environ.get('PASSWORD')
    MONGO_URI = f"mongodb+srv://{user}:{password}@iot.yjg6l.mongodb.net/{database}?retryWrites=true&w=majority"
    try:
        mongo = pm.MongoClient(MONGO_URI,ssl_cert_reqs=ssl.CERT_NONE)
        db = mongo.parking_lot
        collection = db.parking_lot
    except Exception as e:
        print(e)

    @app.route("/verify-otp/",methods=["POST"])
    def verify_otp():
        data = json.loads(request.data)
        contact_number = data["contact_number"]
        otp = data["otp"]

        # if pyotp.TOTP(contact_number).verify(otp):
        #     return jsonify({'status':'success'}), 200
        
        slots = collection.find({"isPresent":True})
        slots = list(slots)
        
        if otp == fixed_OTP and len(slots) < 8:
            return jsonify({"status": "success"}), 200

        message = "Invalid OTP" if otp!=fixed_OTP else "No slots available"
        return jsonify({"status": "failure", "message": message}), 200

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
            updated_result = db.parking_lot.update_one({"slot":slot_number}, {"$set" : {"isPresent": True}})
            if updated_result.modified_count < 1:
                return jsonify({"status": "success", "message":"Car is already present"}), 200
        except:
            return jsonify({"status": "Update Failed"}), 200
        return jsonify({"status": "success", "message": "Parking lot updated"}), 200

    @app.route("/get-parking-lot/", methods=["GET"])
    def get_parking_lot():
        slots = collection.find({},{"_id": False})
        return jsonify({"status": "success", "slots": list(slots)}), 200


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)