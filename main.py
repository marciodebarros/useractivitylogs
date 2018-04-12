import logging
from logging.handlers import RotatingFileHandler
from app import quart_app

if __name__ == '__main__':

    # initialize the log handler
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)

    # set the log handler level
    logHandler.setLevel(logging.INFO)

    # set the app logger level
    quart_app.logger.setLevel(logging.INFO)

    quart_app.logger.addHandler(logHandler)

    quart_app.run()

