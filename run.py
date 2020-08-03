from apscheduler.schedulers.background import BackgroundScheduler
from src import workerServer

if __name__ == '__main__':

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=workerServer.autopolling, trigger="interval", seconds=600)
    scheduler.start()
    workerServer.app.run(use_reloader=False)