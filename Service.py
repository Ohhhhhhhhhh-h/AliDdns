# --coding:utf-8--
#   @Author:    Alpaca
#   @Time:      2023/4/1 13:36
#   @Software:  PyCharm
#   @File:      Service
import logging
import win32serviceutil
import win32event
import inspect
import os
import win32service
import main


class AliDdnsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AliDdnsServiceService"
    _svc_display_name_ = "AliDdnsService"
    _svc_description_ = "This is a AliDdnsService test code "

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.run = True

    def _getLogger(self):
        logger = logging.getLogger('[AliDdnsService]')

        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        handler = logging.FileHandler(os.path.join(dirpath, "service.log"))

        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger

    def svc_do_run(self):
        import time
        self.logger.info("service is run....")
        while self.run:
            resp = main.start()
            self.logger.info("service is runing....")
            self.logger.info(resp)
            time.sleep(2)

    def svc_stop(self):
        self.logger.info("service is stop....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AliDdnsService)
