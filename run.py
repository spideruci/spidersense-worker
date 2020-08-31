from apscheduler.schedulers.background import BackgroundScheduler
from src import workerServer

import logging
if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone='America/Los_Angeles')
    scheduler.add_job(func=workerServer.autopolling, trigger="interval", seconds=1800)
    scheduler.add_job(func=workerServer.dockercheck, trigger="interval", seconds=60)
    scheduler.start()
    workerServer.autopolling()
    handler=logging.FileHandler('flask.log')
    #workerServer.autopolling()
    workerServer.app.run(use_reloader=False,debug=False,host='0.0.0.0')