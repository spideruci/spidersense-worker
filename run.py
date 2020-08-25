from apscheduler.schedulers.background import BackgroundScheduler
from src import workerServer

import logging
if __name__ == '__main__':
    workerServer.autopolling()
    scheduler = BackgroundScheduler(timezone='America/Los_Angeles')
    scheduler.add_job(func=workerServer.autopolling, trigger="interval", seconds=3600)
    scheduler.start()
    handler=logging.FileHandler('flask.log')
    #workerServer.autopolling()
    workerServer.app.run(use_reloader=False,debug=False,host='0.0.0.0')