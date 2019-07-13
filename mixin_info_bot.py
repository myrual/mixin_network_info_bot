from mixin_ws_api import MIXIN_WS_API
from mixin_api import MIXIN_API
import mixin_config
import wallet_api

import json
import time
from io import BytesIO
import base64
import gzip
import datetime
import sys

try:
    import thread
except ImportError:
    import _thread as thread


def on_error(ws, error):
    print(error)
def on_message(ws, message):
    inbuffer = BytesIO(message)

    f = gzip.GzipFile(mode="rb", fileobj=inbuffer)
    rdata_injson = f.read()
    rdata_obj = json.loads(rdata_injson)
    action = rdata_obj["action"]



    if action == "CREATE_MESSAGE":

        data = rdata_obj["data"]
        msgid = data["message_id"]
        typeindata = data["type"]
        categoryindata = data["category"]
        userId = data["user_id"]
        conversationId = data["conversation_id"]
        dataindata = data["data"]

        realData = base64.b64decode(dataindata)

        MIXIN_WS_API.replayMessage(ws, msgid)

        if 'error' in rdata_obj:
            return

        if categoryindata == "SYSTEM_ACCOUNT_SNAPSHOT":
            rdJs = json.loads(realData)
            if ( float(rdJs["amount"]) > 0 ):
                mixin_api.transferTo(userId, rdJs["asset_id"], rdJs["amount"], "")
        if categoryindata == "PLAIN_TEXT":

            realData = realData.decode('utf-8')
            MIXIN_WS_API.sendUserText(ws, conversationId, userId, realData)

if __name__ == "__main__":

    mixin_api = MIXIN_API(mixin_config)
    while True:
        mixin_ws = MIXIN_WS_API(on_message=on_message)
        mixin_ws.run()
