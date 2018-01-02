#!/usr/bin/python

#############################################################
# Antica Innesteria Dippolitoni presents:
#
# Test NetFlows oO Threaded 1.4
#############################################################


import Queue
import argparse
import threading
import time
import os

from Server import Server
from Client import Client
from AnalyzeData import AnalyzeData
from ConfigLogic import ConfigLogic
from Configurator import Configurator
from Log import Log

##############################################################


if __name__ == '__main__':

    date_format = time.strftime("%d-%b-%Y")
    # "test-netflow-" + date_format + ".log"
    logname = os.getcwd() + os.sep + "log" + os.sep + "TestNetflow.log"
    # "test-netflow-" + date_format +".paramiko" +".log
    paramiko_logname = os.getcwd() + os.sep + "log" + os.sep + "TestNetflow.paramiko.log"

    # parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(prog='TestNetflow.py',
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30))
    parser.add_argument("-d", "--debug", help="turn on debug log level", action="store_true")
    parser.add_argument("-s", "--stdout", help="Output Debug actions on stdout", action="store_true")
    parser.add_argument("-n", "--netcat",
                        help="option to specify an alternate nc (netcat) binary path, "
                             "once omitted program will try to use \"nc\" in $PATH ",
                        default="nc", metavar="nc")
    parser.add_argument("-v", "--version", help="Display the version of the program", action="version",
                        version="Antica Innesteria Dippolitoni presents: %(prog)s 1.0")
    userargs = parser.parse_args()

    level = "INFO"
    if userargs.debug:
        level = "DEBUG"

    log = Log(logname, level, None)
    paramikolog = Log(paramiko_logname, level, "paramiko")
    logger = log.create_log()
    paramikologger = paramikolog.create_log()

    # paramiko.util.log_to_file(paramiko_log)

    configfile = os.getcwd() + os.path.sep + "properties" + os.path.sep + "config.properties"
    configurator = Configurator(configfile, logger)
    lst = configurator.get_config()
    client_data_list = []
    client_result_list = []
    server_data_list = []
    client_thread_list = []
    server_thread_list = []
    close_thread_list = []
    analyze_thread_list = []

    queue = Queue.Queue()
    server_exeception_queue = Queue.Queue()
    client_exeception_queue = Queue.Queue()
    closehelper_exception_queue = Queue.Queue()
    analyze_exception_queue = Queue.Queue()

    configlogic = ConfigLogic(server_data_list, client_data_list)
    configlogic.mainLogic(lst, server_data_list, client_data_list)

    print "*" * 80
    print('\n%s\n%s\n%s\n' % ('Welcome to Network Flow Testing Tool', 'Please wait for program completion',
                              'or look for details at the log file ' + logname))
    print "*" * 80

    # Trace
    # print "client_data_list: -> " +str(client_data_list)
    # print "server_data_list: -> " +str(client_data_list)
    # print "*"*80
    # print "Client!"
    # for idx,value in enumerate(client_data_list):
    # print idx, value
    # print "*"*80
    # print "*"*80
    # print "Server!"
    # for idx,value in enumerate(server_data_list):
    # print idx, value
    # print "*"*80

    servermutex = threading.Lock()
    clientmutex = threading.Lock()
    closemutex = threading.Lock()

    count = 1
    for i in range(len(server_data_list)):
        name = "Thread-" + str(count)
        server_thread = Server(server_data_list[i], logger,
                               server_exeception_queue,
                               name, servermutex, userargs)
        server_thread.start()
        server_thread_list.append(server_thread)
        count += 1

    for s in server_thread_list:
        exc = server_exeception_queue.get()
        if type(exc) is not str:
            exc_type, exc_obj, exc_trace = exc
            logger.error("Thread-0(Main) -- Exception from Server class " + str(exc_obj))
            if userargs.stdout:
                print("DEBUG STDOUT: Thread-0 (Main) -- Exception from Server class " + str(exc_obj))
                # print exc_type, exc_obj
                # print exc_trace
        s.join()

    for i in range(len(client_data_list)):
        name = "Thread-" + str(count)
        client_thread = Client(client_data_list[i], logger, queue,
                               client_exeception_queue, name,
                               clientmutex, userargs)
        client_thread.start()
        client_thread_list.append(client_thread)
        count += 1

    for c in client_thread_list:
        exc = client_exeception_queue.get()
        if type(exc) is not str:
            exc_type, exc_obj, exc_trace = exc
            logger.error("Thread-0(Main) -- Exception from Client class " + str(exc_obj))
            if userargs.stdout:
                print("DEBUG STDOUT: Thread-0 (Main) -- Exception from Client class " + str(exc_obj))
                # print exc_type, exc_obj
                # print exc_trace
        response = queue.get()
        # if type(response) is dict:
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
                # print exc_type, exc_obj
                # print exc_trace
        a.join()

    if userargs.stdout:
        print "*" * 80
    print('\n%s\n%s\n%s\n' % (
        'Program has finished testing flows between clients and servers', 'Please review flows status report',
        'within the log file ' + logname))
    print "*" * 80
    #
    ###########################################################################
