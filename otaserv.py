#!/usr/bin/env python3

import sys
try:
    from flask import Flask, redirect, url_for, request, abort
    from peewee import *
except ImportError:
    print("Missing requirements")
    print("sudo -H pip3 install flask peewee'")
    sys.exit(1)
import sys
import datetime
import hashlib
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

if len(sys.argv) < 2:
    print("Usage: %s <database> [-d]" % sys.argv[0])
    sys.exit(1)

db = SqliteDatabase(sys.argv[1])


class BaseModel(Model):
    class Meta:
        database = db # This model uses the "firmwares.db" database.

"""
Firmware list. We can a add firmwares primarily based on
 - node_id     - upgrade only a certain node
 - node_type   - upgrade all nodes of given type (eg ESP32CAM)

Secondarly, we can set the hw_rev to differentiate between different hardware 
revisions.
"""
class Firmware(BaseModel):
#    sha256 = CharField(unique = True)
    sha256 = CharField()
    added_on = DateTimeField(default = datetime.datetime.utcnow())
    updated_on = DateTimeField()
    name = CharField(null = True) # Name of image, for readability only
    platform = CharField(null = True) # Platform eg. ESP8266, ESP32, ..., for readability only
    node_type = CharField(null = True) # Uniquie node type identifier (eg. ESP32CAM)
    node_id = CharField(null = True) # 
    hw_rev = CharField(null = True)
    image = BlobField()

class Session(BaseModel):
    sha256 = CharField()
    node_id = CharField()
    started_on = DateTimeField(default = datetime.datetime.utcnow())
    ended_on = DateTimeField(null = True)
    success = BooleanField(null = True)

db.connect()
db.create_tables([Firmware, Session])

def add_firmware(dict, image):
    sha256 = hashlib.sha256(image).hexdigest()
    logging.info("sha256: %s" % sha256)
    # There is some discussion about this
    if 1:
        fw = Firmware(sha256 = sha256)
    else:
        try:
            # Modifications nor duplicates are not allowed
            if Firmware.get(sha256 = sha256):
                logging.info("sha256 exists, duplicates not allowed")
                abort(403)
        except Firmware.DoesNotExist:
            fw = Firmware(sha256 = sha256)
    try:
        now = datetime.datetime.utcnow()
        fw.added_on = now
        fw.updated_on = now
        fw.sha256 = sha256
        fw.image = image
        if 'name' in dict:
            fw.name = dict['name']
        if 'platform' in dict:
            fw.platform = dict['platform']
        if 'node_type' in dict:
            fw.node_type = dict['node_type']
        if 'node_id' in dict:
            fw.node_id = dict['node_id']
        if 'hw_rev' in dict:
            fw.hw_rev = dict['hw_rev']
        fw.save()
        return True
    except KeyError as e:
        logging.error("Exception occurred", exc_info = True)
        print(e)
        return False
    except IntegrityError as e:
        print("IntegrityError:")
        print(e)
        print(fw)
        return False
    except sqlite3.IntegrityError as e:
        print("sqlite3.IntegrityError:")
        print(e)
        print(fw)
        return False


def get_fimware(dict):
    fw = None
    if not fw and "node_id" in dict:
        if "hw_rev" in dict:
            logging.info("Looking for node id %s and hw_rev %s" % (dict["node_id"], dict["hw_rev"]))
            try:
                # Does SELECT COUNT - why...?
                fw = Firmware.select().where(Firmware.node_id == dict["node_id"] and Firmware.hw_rev == dict["hw_rev"]).order_by(Firmware.added_on.desc()).get()
                # Throws IndexError - why...?
#                fw = Firmware.get(Firmware.node_id == dict["node_id"] and Firmware.hw_rev == dict["hw_rev"]).order_by(Firmware.added_on.desc()).get()
                logging.info("Found!")
            except IndexError as e:
                logging.info("peewee made a boo-boo")
                #logging.error("Exception occurred", exc_info = True)
                fw = None
            except Exception as e:
#            except FirmwareDoesNotExist as e:
                fw = None
        if not fw:
            logging.info("Looking for node id %s" % dict["node_id"])
            try:
                #fw = Firmware.select().where(Firmware.node_id == dict["node_id"] and Firmware.hw_rev >> None).order_by(Firmware.added_on.desc()).dicts()
                fw = Firmware.select().where(Firmware.node_id == dict["node_id"]).order_by(Firmware.added_on.desc()).get()
#                fw = Firmware.select().where(Firmware.node_id == dict["node_id"] and Firmware.hw_rev >> None).order_by(Firmware.added_on.desc()).get()
                logging.info("Found!")
            except IndexError as e:
                logging.info("peewee made a boo-boo")
                #logging.error("Exception occurred", exc_info = True)
                fw = None
            except Exception as e:
#            except FirmwareDoesNotExist as e:
                fw = None

    if not fw and "node_type" in dict:
        if "hw_rev" in dict:
            logging.info("Looking for node type %s and hw_rev %s" % (dict["node_type"], dict["hw_rev"]))
            try:
                #fw = Firmware.select().where(Firmware.node_type == dict["node_type"] and Firmware.hw_rev == dict["hw_rev"]).order_by(Firmware.added_on.desc()).dicts()
                fw = Firmware.select().where(Firmware.node_type == dict["node_type"] and Firmware.hw_rev == dict["hw_rev"]).order_by(Firmware.added_on.desc()).get()
                logging.info("Found!")
            except IndexError as e:
                logging.info("peewee made a boo-boo")
                #logging.error("Exception occurred", exc_info = True)
                fw = None
            except Exception as e:
#            except FirmwareDoesNotExist as e:
                fw = None
        if not fw:
            logging.info("Looking for node type %s" % dict["node_type"])
            try:
                fw = Firmware.select().where(Firmware.node_type == dict["node_type"]).order_by(Firmware.added_on.desc()).get()
                logging.info("Found!")
                logging.info(fw.sha256)
            except IndexError as e:
                logging.info("peewee made a boo-boo")
                #logging.error("Exception occurred", exc_info = True)
                fw = None
            except Exception as e:
                logging.error("Exception occurred", exc_info = True)
#            except FirmwareDoesNotExist as e:
                fw = None
    if not fw and "sha256" in dict:
        logging.info("Looking for sha256 %s" % dict["sha256"])
        try:
            fw = Firmware.select().where(Firmware.sha256 == dict["sha256"]).order_by(Firmware.added_on.desc()).get()
            logging.info("Found")
        except IndexError as e:
            logging.info("peewee made a boo-boo")
            #logging.error("Exception occurred", exc_info = True)
            fw = None
        except Exception as e:
            fw = None

    if not fw:
        abort(404)

    return fw

    abort(404)


def handle_firmware(request):
    logging.info("FIRMWARE")
    for h in request.headers:
        logging.info(h)
    if request.method == 'GET':
        logging.info("Downloading FW")
        fw = get_fimware(request.headers)
        if fw:
            return fw.sha256
        else:
            abort(404)
    elif request.method == 'POST':
        logging.info("Adding new FW")
        image = request.stream.read()
        add_firmware(request.headers, image)
        return "OK"

# Get sha256 for current firmware
@app.route("/firmware", methods = ['GET', 'POST'])
def firmware():
    return handle_firmware(request)

@app.route("/firmware/", methods = ['GET', 'POST'])
def firmware_slash():
    return handle_firmware(request)

@app.route("/session/<string:verb>/<string:sha256>", methods = ['GET'])
def session(verb, sha256):
    if not verb or not sha256 or not "node_id" in request.headers:
        abort(404)
    try:
        if not Firmware.get(sha256 = sha256):
            abort(404)
    except Firmware.DoesNotExist:
        abort(404)

    node_id = request.headers["node_id"]
    logging.info("session '%s' sha256 '%s' node_id '%s'" % (verb, sha256, node_id))
    if verb == "begin":
        fw = Session(sha256 = sha256, node_id = node_id)
        now = datetime.datetime.utcnow()
        fw.added_on = now
        fw.sha256 = sha256
        fw.node_id = node_id
        fw.save()
        return "OK:%s" % sha256
    elif verb == "complete" or verb == "fail":
        try:
            s = Session.select().where(Session.sha256 == sha256 and Session.node_id == node_id and Session.success >> None).order_by(Session.started_on.desc()).get()
        except Session.DoesNotExist:
            abort(404)
        s.ended_on = datetime.datetime.utcnow()
        s.success = verb == "complete"
        s.save()
        return "OK:%s" % sha256
    else:
        abort(403)

@app.route("/firmware/<string:sha256>", methods = ['GET'])
def download_sha256(sha256):
    sha256 = sha256.lower()
    if request.method == 'GET':
        fw = get_fimware({"sha256" : sha256})
    if fw:
        return fw.image
    else:
        abort(404)

if __name__ == "__main__":
    debug = "-d" in sys.argv
    level = logging.DEBUG if debug else logging.WARN
#    level = logging.INFO # causes every HTTP call to be logged...
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    handler.setFormatter(log_formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    app.run(host= '0.0.0.0', port = 27532, debug = debug)


"""
curl --header "node_id:42" --header "node_type:esp32cam" --header "hw_rev:1" http://127.0.0.1:27532/firmware
curl --header "node_type:esp32cam" http://127.0.0.1:27532/firmware
curl --header "node_id:42" --header "hw_rev:1" http://127.0.0.1:27532/firmware
curl --header "node_id:42" http://127.0.0.1:27532/firmware

curl --header "node_id:42" --header "node_type:esp32cam" --header "hw_rev:1" -o fw2.bin http://127.0.0.1:27532/firmware/57dda900027355de85f0de9e6c966e3c4c16741d8eed134d209c0fb6304cf852

curl --request POST 'http://127.0.0.1:27532/firmware' --header "node_type:esp32cam" --data-binary "@fw.bin" --verbose

curl --header "node_id:42" --header "node_type:esp32cam" --header "hw_rev:1" http://127.0.0.1:27532/session/begin/57dda900027355de85f0de9e6c966e3c4c16741d8eed134d209c0fb6304cf852
"""