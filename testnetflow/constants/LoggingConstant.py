
class LoggingConstant:
    def __init__(self):
        pass

    # COMMON
    DEBUG_STDOUT_HEADER = "DEBUG STDOUT: "
    INFO_STDOUT_HEADER = "INFO STDOUT: "
    ERROR_STDOUT_HEADER = "ERROR STDOUT: "
    EXC_HEADER = "Exception: "
    ON_IP_MSG = " On remote box: "
    ON_SOCKET = " On socket: "
    ON_PORT_MSG = " port: "
    SEP = " -- "  # type: str
    WITH_MESSAGE = " with message: "

    # MAIN
    GREETINGS = "Welcome to Network Flow Testing Tool"
    WAIT_MSG_1 = "Please wait for program completion"
    WAIT_MSG_2 = "or look for details at the log file "
    END_MSG = "Program has finished testing flows between clients and servers"
    REVIEW_MSG = "Please review flows status report"
    LOG_FILE_MSG = "inside log file"
    MAIN_EXC_MESSAGE = "Main_Thread_0 -- Exception from class "
    MAIN_THREAD = "Main_Thread_0"
    FRAME = "*" * 80

    # NetHelperBase:
    CONNECT_WITH_USERNAME = " Connecting with Username: "
    NETSTAT_ERROR = "cannot find either \"ss\" command or \"netstat\""
    SOCKET_NOT_LISTENING = "socket has not been found in LISTEN state"
    SOCKET_LISTENING = "socket has been found in LISTEN state"
    PYTHON_NOT_FOUND = "Python was not found on the remote machine $PATH"
    PYTHON_EXC_ERROR = "Unable to execute python on the remote machine: "
    PYTHON_VER_ERROR = "Unable to verify python version on the remote machine: "
    SHEBANG_ERROR = "Unable to sed the shebang on the remote machine"
    UPLOAD_ERROR = "Unable to upload the following script: "
    SCRIPT_NOT_FOUND_ERROR = "Following script was not found: "
    X_BIT_ERROR = "Unable to set the execution bit on: "
    MKDIR_ERROR = "Unable to create remote directory: "

    # NetObjectBase
    DNS_ERROR = " Unable to find a corresponding DNS name for address: "
    PYTHON_VER_UNSUPPORTED = "Python version not supported, please install: "

    # TerminalHandlerBase
    SEND_SSH_METHOD = " send_ssh_events method "
    SCAND_BUFFER_METHOD = " scan_buffer_end method "
    TIMEOUT_MSG = " timeout error while scanning buffer "
    PATTERN_ERROR = " Can not find pattern: "
    SUDO_USER_ERROR = " User is not able to run sudo "
    SUDO_WRONG_RESPONSE = " Sudo command got an unexpected response "

    # ClientHelperImpl
    NULL_RESPONSE_ERROR = "null response from client script"
    CLIENT_CONN_ERROR = " unable to connect to the remote server: "
    CLIENT_CONN_OK = " successful connection to server "
    UNKNOWN_ERROR = "Unknown Exception while testing the remote endpoint"

    # ClientObjectImpl
    CLIENT_IP_ERROR = " unable to determine client ip "
    LOAD_BALANCER_CFG_ERROR = " Empty load balancer address was found in config file "

    # CloserHelperImpl
    CLOSE_ERROR = "Unknown ERROR while closing the remote connection: "
    CLOSE_OK_MGS = " following socket has been closed: "
    ALREADY_CLOSED_MSG = " socket already closed on server: "

    CLOSE_CONNECTION_MSG = "The following connection the connection has been closed: "
    CLOSE_CONNECTION_ERROR = "Error closing the following connection: "
    CLOSE_CONNECTION_EXC = "Exception closing the following connection: "

    # ServerHelperImpl
    SUDO_ERROR = "Unable to run sudo with user: "
    SUDO_SOCKET_ERROR = " unable to start Socket Server python script with sudo command "
    NORMAL_SOCKET_ERROR = " unable to start Socket Server python script "
    SOCKET_STARTED = " SocketServer has been started on "
    SOCKET_IS_STARTING = " ...Going to start socket "
    SOCKET_ALREADY_LISTENING = " socket is already in LISTEN state on the remote server "

    # Config
    ERROR_CONFIG = " Error in parsing configuration file "
    REPORTING_STATUS_MSG = "Network Flow between "
