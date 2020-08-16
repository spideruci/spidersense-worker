from apscheduler.schedulers.background import BackgroundScheduler
from src import workerServer

import logging
if __name__ == '__main__':

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=workerServer.autopolling, trigger="interval", seconds=1200)
    scheduler.start()
    handler=logging.FileHandler('flask.log')
    #workerServer.autopolling()
    workerServer.app.run(use_reloader=False,debug=False)