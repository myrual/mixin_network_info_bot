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

        if categoryindata == "PLAIN_TEXT":
            realData = realData.decode('utf-8')
            if "mixin" == realData.lower():
                main_net_info = wallet_api.main_net_info()
                response = "Uptime: %s Version: %s Total %d full nodes\n"%(main_net_info.uptime, main_net_info.version, len(main_net_info.graph.consensus))
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, response)
                return
            if "mixinfull" == realData.lower():
                main_net_info = wallet_api.main_net_info()
                response = "Uptime: %s Version: %s Total %d full nodes\n"%(main_net_info.uptime, main_net_info.version, len(main_net_info.graph.consensus))
                MIXIN_WS_API.sendUserText(ws, conversationId, userId, response)
                main_net_node = wallet_api.github_main_net_node_info()
                for eachNode in main_net_info.graph.consensus:
                    thisRecord = ""
                    thisRecord += eachNode.state
                    thisRecord += ","
                    thisRecord += eachNode.node
                    thisRecord += ","

                    i = 0
                    #for eachGithub in main_net_node:
                    #    if eachNode.signer == eachGithub.get("signer"):
                    #        thisRecord += eachGithub.get("host")
                    #        thisRecord += ","
                    #        break
                    #    else:
                    #        i+=1
                    #if i == len(github_node_info):
                    #    thisRecord += "Anonymous"
                    #    thisRecord += ","
                    thisRecord += str(datetime.date.fromtimestamp((eachNode.timestamp)/(1000 * 1000 * 1000)))
                    MIXIN_WS_API.sendUserText(ws, conversationId, userId, thisRecord)
                return
            if "search" in realData.lower():
                tosplit = realData.lower().split(":")
                if(len(tosplit) > 1):
                    try:
                        print(tosplit)
                        tosearch = tosplit[1]
                        result = mixin_api.SearchUser(tosearch)
                        print(result)
                        if "data" in result:
                            user_id_uuid = result["data"]["user_id"]
                            MIXIN_WS_API.sendUserText(ws, conversationId, userId, user_id_uuid)
                            return
                    except e:
                        print(sys.exc_info()[0])
                        
                    finally:
                        print("finish")

            response =  "send text mixin or mixinfull to me\n"
            MIXIN_WS_API.sendUserText(ws, conversationId, userId, response)
            return

if __name__ == "__main__":

    mixin_api = MIXIN_API(mixin_config)

    mixin_ws = MIXIN_WS_API(on_message=on_message)

    mixin_ws.run()
