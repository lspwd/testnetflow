#!/usr/bin/python

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

from testnetflow.impl.Client import Client
from testnetflow.impl.Server import Server
from testnetflow.util.AnalyzeData import AnalyzeData
from testnetflow.util.Configurator import Configurator
from testnetflow.util.Log import Log

##############################################################


if __name__ == '__main__':

    date_format = time.strftime("%d-%b-%Y")
    logname = os.getcwd() + os.sep + "log" + os.sep + "TestNetflow.log"
    paramiko_logname = os.getcwd() + os.sep + "log" + os.sep + "TestNetflow.paramiko.log"

    parser = argparse.ArgumentParser(prog='TestNetflow.py',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30))
    parser.add_argument("-d", "--debug", help="turn on debug log level", action="store_true")
    parser.add_argument("-ct", "--clienttimeout", type=str,
                        help="socket client timeout (default: 3 sec)", default="3")
    parser.add_argument("-st", "--servertimeout", type=str,
                        help="socket client timeout (default: 20 sec)", default="20")
    parser.add_argument("-s", "--stdout", help="Output Debug actions on stdout", action="store_true")
    parser.add_argument("-v", "--version", help="Display the version of the program", action="version",
                        version="Antica Innesteria Dippolitoni presents: %(prog)s 2.0")
    userargs = parser.parse_args()

    level = "INFO"
    if userargs.debug:
        level = "DEBUG"

    log = Log(logname, level, None)
    paramikolog = Log(paramiko_logname, level, "paramiko")
    logger = log.create_log()
    paramikologger = paramikolog.create_log()
    configfile = os.getcwd() + os.path.sep + "properties" + os.path.sep + "config.yml"
    configurator = Configurator(configfile, logger)
    config_list = configurator.get_config()

    client_list = []
    server_list = []

    server_result_list = []
    client_result_list = []

    client_thread_list = []
    server_thread_list = []
    analyze_thread_list = []

    client_result_queue = Queue.Queue()
    server_result_queue = Queue.Queue()
    server_exeception_queue = Queue.Queue()
    client_exeception_queue = Queue.Queue()
    analyze_exception_queue = Queue.Queue()

    print("*" * 80)
    print('\n%s\n%s\n%s\n' % ('Welcome to Network Flow Testing Tool', 'Please wait for program completion',
                              'or look for details at the log file ' + logname))
    print("*" * 80)

    servermutex = threading.Lock()
    clientmutex = threading.Lock()

    count = 1

    [map(lambda pos: server_list.append(config_list[index]["client"]["server_list_to_test"][pos]),
         range(len(config_list[index]["client"]["server_list_to_test"]))) for index in range(len(config_list))]

    for position, server in enumerate(server_list):
        name = "Thread-" + str(count)
        if not server_list[position]["try_to_spawn_socket_on_remote_server"]:
            map(lambda socket: server_result_list.append(
                {"socket": socket["address"] + ":" + socket["port"], "deployed": False}),
                server_list[position]["socket_to_test"])
            continue

        server_thread = Server(server_list[position]["ssh_server_username"],
                               server_list[position]["ssh_server_password"],
                               server_list[position]["ssh_server_ip_address"],
                               server_list[position]["socket_to_test"],
                               logger,
                               server_exeception_queue,
                               server_result_queue,
                               name, servermutex, userargs, server_result_list)
        server_thread.start()
        server_thread_list.append(server_thread)
        count += 1

    for s in server_thread_list:
        exception_list = server_exeception_queue.get()
        if type(exception_list) is not str:
            for exception in exception_list:
                logger.error("Thread-0(Main) -- Exception from Server class " + str(exception))
                if userargs.stdout:
                    print("DEBUG STDOUT: Thread-0(Main) -- Exception from Server class " + str(exception))

        # else:
        #     print("server_result_list: ")
        #     server_result_list.append(serverResponseList)

        server_result_list = server_result_queue.get()
        s.join()

    for i in range(len(config_list)):
        name = "Thread-" + str(count)

        [map(lambda x: client_list.append(x), config_list[i]["client"]["server_list_to_test"][idx]["socket_to_test"])
         for idx in range(len(config_list[i]["client"]["server_list_to_test"]))]

        client_thread = Client(config_list[i]["client"]["ssh_client_username"],
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
        count += 1

    for c in client_thread_list:
        exc = client_exeception_queue.get()
        if type(exc) is not str:
            logger.error("Thread-0(Main) -- Exception from Client class " + str(exc))
            if userargs.stdout:
                print("DEBUG STDOUT: Thread-0 (Main) -- Exception from Client class " + str(exc))

        response = client_result_queue.get()
        client_result_list.append(response)
        c.join()

    for i in range(len(client_result_list)):
        name = "Thread-" + str(count)
        analyze_thread = AnalyzeData(client_result_list[i], logger, analyze_exception_queue, name, userargs)
        analyze_thread.start()
        analyze_thread_list.append(analyze_thread)
        count += 1

    for a in analyze_thread_list:
        exc = analyze_exception_queue.get()
        if type(exc) is not str:
            exc_type, exc_obj, exc_trace = exc
            logger.error("Thread-0(Main) -- Exception from AnalyzeData class " + str(exc_obj))
            if userargs.stdout:
                print("DEBUG STDOUT: Thread-0 (Main) -- Exception from AnalyzeData class " + str(exc_obj))

        a.join()

    if userargs.stdout:
        print("*" * 80)
    print('\n%s\n%s\n%s\n' % (
        'Program has finished testing flows between clients and servers', 'Please review flows status report',
        'within the log file ' + logname))
    print("*" * 80)
    #
    ###########################################################################
