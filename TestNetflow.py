#!/usr/bin/python -u

#############################################################
# Antica Innesteria Dippolitoni presents:
#
# Test NetFlows oO Threaded 2.0
#############################################################

import argparse
import os
import Queue
import threading
import time
import warnings
import cryptography

from testnetflow.impl.ClientObjectImpl import ClientObjectImpl
from testnetflow.impl.ServerObjectImpl import ServerObjectImpl
from testnetflow.impl.CloserObjectImpl import CloserObjectImpl
from testnetflow.util.Reporting import Reporting
from testnetflow.util.Configurator import Configurator
from testnetflow.util.Log import Log
from testnetflow.constants.LoggingConstant import LoggingConstant

def init_args():
    """
    Initialize command line arguments
    :return: a parser for command line arguments
    """

    # Default values
    configfile = os.path.join(os.getcwd(), "properties", "config.yml")
    ctimeout = "3"
    stimeout = "30"

    parser = argparse.ArgumentParser(prog='TestNetflow.py',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30))
    parser.add_argument("-c", "--cfg", help="use specified config file (default {})".format(configfile),
                        default=configfile)
    parser.add_argument("-d", "--debug", help="turn on debug log level", action="store_true")
    parser.add_argument("-ct", "--clienttimeout", help="socket client timeout (default: {} sec)".format(ctimeout),
                        type=str, default=ctimeout)
    parser.add_argument("-st", "--servertimeout", help="socket client timeout (default: {} sec)".format(stimeout),
                        type=str, default=stimeout)
    parser.add_argument("-s", "--stdout", help="Output Debug actions on stdout", action="store_true")
    parser.add_argument("-v", "--version", help="Display the version of the program", action="version",
                        version="Antica Innesteria Dippolitoni presents: %(prog)s 2.0")

    return parser


def main():

    warnings.simplefilter("ignore", cryptography.utils.CryptographyDeprecationWarning)
    date_format = time.strftime("%d-%b-%Y")

    logname = os.path.join(os.getcwd(), "log", "TestNetflow.log")
    paramiko_logname = os.path.join(os.getcwd(), "log", "TestNetflow.paramiko.log")

    userargs = init_args().parse_args()

    level = "INFO"
    if userargs.debug:
        level = "DEBUG"

    log = Log(logname, level, "testnetflow")
    paramikolog = Log(paramiko_logname, level, "paramiko")
    logger = log.create_log()
    log.set_stdout(userargs.stdout)
    paramikologger = paramikolog.create_log()
    stringConstants = LoggingConstant()

    configurator = Configurator(userargs.cfg, logger)
    config_list = configurator.get_config()

    client_list = []
    server_list = []

    server_result_list = []
    client_result_list = []
    server_to_close_list = []


    client_thread_list = []
    server_thread_list = []
    reporting_list = []

    client_result_queue = Queue.Queue()
    server_result_queue = Queue.Queue()
    server_to_close_queue = Queue.Queue()
    server_to_close_exception_queue = Queue.Queue()
    server_exeception_queue = Queue.Queue()
    client_exeception_queue = Queue.Queue()
    reporting_exception_queue = Queue.Queue()

    print(stringConstants.FRAME)
    print(stringConstants.GREETINGS)
    print(stringConstants.WAIT_MSG_1)
    print(stringConstants.WAIT_MSG_2 + " " +logname)
    print(stringConstants.FRAME)

    servermutex = threading.Lock()
    clientmutex = threading.Lock()
    closingmutex = threading.Lock()

    count = 1
    [map(lambda pos: server_list.append(config_list[index]["client"]["server_list_to_test"][pos]),
         range(len(config_list[index]["client"]["server_list_to_test"]))) for index in range(len(config_list))]

    for position, server in enumerate(server_list):
        name = "Server_Thread_{}".format(count)
        if not server_list[position]["try_to_spawn_socket_on_remote_server"]:
            map(lambda socket: server_result_list.append(
                {"socket": socket["address"] + ":" + str(socket["port"]), "deployed": False}),
                server_list[position]["socket_to_test"])
            continue

        logging_header = stringConstants.MAIN_THREAD + stringConstants.SEP

        server_thread = ServerObjectImpl(server_list[position]["ssh_server_username"],
                                         server_list[position]["ssh_server_password"],
                                         server_list[position]["ssh_server_ip_address"],
                                         server_list[position]["socket_to_test"],
                                         logger,
                                         server_exeception_queue,
                                         server_result_queue,
                                         server_to_close_queue,
                                         name, servermutex, userargs, server_result_list, server_to_close_list)
        server_thread.start()
        server_thread_list.append(server_thread)
        count += 1

    for s in server_thread_list:
        exception_list = server_exeception_queue.get()
        if type(exception_list) is not str:
            for i in exception_list:
                msg=stringConstants.MAIN_EXC_MESSAGE + stringConstants.SEP +str(i)
                logger.printStdoutMessage(msg,stringConstants.DEBUG_STDOUT_HEADER)
                logger.loggingDebugMessage(msg)

        server_result_list = server_result_queue.get()
        server_to_close_list = server_to_close_queue.get()
        s.join()

    count = 1
    for i in range(len(config_list)):
        name = "Client_Thread_{}".format(count)

        [map(lambda x: client_list.append(x), config_list[i]["client"]["server_list_to_test"][idx]["socket_to_test"])
         for idx in range(len(config_list[i]["client"]["server_list_to_test"]))]

        client_thread = ClientObjectImpl(config_list[i]["client"]["ssh_client_username"],
                                         config_list[i]["client"]["ssh_client_password"],
                                         config_list[i]["client"]["ssh_client_ip_address"],
                                         client_list,
                                         logger,
                                         client_exeception_queue,
                                         client_result_queue,
                                         name,
                                         clientmutex,
                                         userargs,
                                         server_result_list)
        client_thread.start()
        client_thread_list.append(client_thread)
        client_list = []
        count += 1

    for c in client_thread_list:
        exc = client_exeception_queue.get()
        if type(exc) is not str:
            for i in exc:
                msg=stringConstants.MAIN_EXC_MESSAGE + stringConstants.SEP + str(i)
                logger.printStdoutMessage(msg,stringConstants.DEBUG_STDOUT_HEADER)
                logger.loggingDebugMessage(msg)

        response = client_result_queue.get()
        client_result_list.append(response)
        c.join()

    count = 1
    for i in range(len(client_result_list)):
        name = "Reporting_Thread_{}".format(count)
        reporting_thread = Reporting(client_result_list[i], logger, reporting_exception_queue, name, userargs)
        reporting_thread.start()
        reporting_list.append(reporting_thread)
        count += 1

    for a in reporting_list:
        exc = reporting_exception_queue.get()
        if type(exc) is not str:
            exc_type, exc_obj, exc_trace = exc
            msg=stringConstants.MAIN_EXC_MESSAGE + Reporting.__class__.name
            msg=msg + stringConstants.SEP + str(exc_obj)
            logger.error(msg)
            log.printStdoutMessage(msg,stringConstants.ERROR_STDOUT_HEADER)
        a.join()

    if server_to_close_list:
        count = 1
        for i in server_to_close_list:
            name = "Closer_Thread_{}".format(count)
            close_thread = CloserObjectImpl(i["username"], i["password"], i["mgmt_ip"], i["binding_address"], i["port"],
                                            logger, server_to_close_exception_queue, closingmutex, userargs, name)
            close_thread.start()
            exc = server_to_close_exception_queue.get()
            if type(exc) is not str:
                exc_type, exc_obj, exc_trace = exc
                msg= stringConstants.MAIN_EXC_MESSAGE + CloserObjectImpl.__class__.name \
                     +stringConstants.SEP + str(exc_obj)
                logger.error(msg)
                log.printStdoutMessage(msg,stringConstants.ERROR_STDOUT_HEADER)

            count += 1
            close_thread.join()

    print(stringConstants.FRAME)
    print(stringConstants.END_MSG)
    print(stringConstants.REVIEW_MSG)
    print(stringConstants.LOG_FILE_MSG + " " + logname)
    print(stringConstants.FRAME)

if __name__ == '__main__':
    main()
