import app.conf.appinfo as appinfo
import app.conf.config as cf
import system.log_manager as log
import system.mgmt as mgmt

log.info("App Name : " + appinfo.APP_NAME)
log.info("App Version : " + appinfo.APP_VERSION)

from system.bot import client

import os
for i in os.listdir("app/cogs/"):
    if i == "__pycache__" or i == ".ipynb_checkpoints" or i.endswith(".disabled") or i.endswith(".swp"):
        continue
    exec("import app.cogs." + i)
    mgmt.loaded_cogs.append(i.replace(".py", ""))
    log.info("Imported Module - " + i.replace(".py", ""))

log.info("Starting Bot")
client.run(token=cf.bot_token)
