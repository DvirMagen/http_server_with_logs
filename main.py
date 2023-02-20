import logging
import os.path
import time
from datetime import datetime
from math import factorial
from flask import Flask, request

server: Flask = Flask('__name__')

binary_operations = {"plus", "minus", "times", "divide", "pow"}
unary_operations = {"abs", "fact"}
log_levels = ["INFO", "DEBUG", "ERROR", "WARNING", "CRITICAL", "NOTSET"]

stack = []
global requests_counter
requests_counter = 1

global request_logger_level
request_logger_level: str = "INFO"
global stack_logger_level
stack_logger_level: str = "INFO"
global independent_logger_level
independent_logger_level: str = "DEBUG"


def files_creator():
    folder_name = "logs"
    files_name = [{'requests.log'}, {'stack.log'}, {'independent.log'}]
    if not os.path.exists(folder_name):
        os.makedirs('logs')


def create_logger_method():
    # Create Request Logger
    request_logger = logging.getLogger('request-logger')
    request_logger.setLevel(logging.INFO)
    open('logs/requests.log', 'w').close()
    request_file_handler = logging.FileHandler('logs/requests.log')
    request_screen_handler = logging.StreamHandler()
    msg_format = logging.Formatter("%(date-time-str)s %(levelname)s: %(message)s | request #%(request-number)s ")
    request_file_handler.setFormatter(msg_format)
    request_screen_handler.setFormatter(msg_format)
    request_logger.addHandler(request_file_handler)
    request_logger.addHandler(request_screen_handler)

    # Create Stack Logger
    stack_logger = logging.getLogger('stack-logger')
    stack_logger.setLevel(logging.INFO)
    open('logs/stack.log', 'w').close()
    stack_file_handler = logging.FileHandler('logs/stack.log')
    stack_file_handler.setFormatter(msg_format)
    stack_logger.propagate = False
    stack_logger.addHandler(stack_file_handler)

    # Create Independent Logger
    independent_logger = logging.getLogger("independent-logger")
    open('logs/independent.log', 'w').close()
    independent_logger.setLevel(logging.DEBUG)
    independent_logger.propagate = False
    independent_file_handler = logging.FileHandler('logs/independent.log')
    independent_file_handler.setFormatter(msg_format)
    independent_logger.addHandler(independent_file_handler)


def request_logger_message(resource, http_verb, start_request_time):
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    request_logger = logging.getLogger('request-logger')
    request_logger.info(f"Incoming request | #{requests_counter} | resource: {resource} | HTTP Verb {http_verb}",
                        extra={'date-time-str': date_time_str, 'request-number': requests_counter})
    finish_request_time = time.time()
    request_duration = int((finish_request_time - start_request_time) * 1000)
    request_logger.debug(f"request #{requests_counter} duration: {request_duration}ms",
                         extra={'request-number': requests_counter, 'date-time-str': date_time_str})
    requests_counter += 1


def independent_error_message(resource, http_verb, start_request_timer, error_message):
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    independent_logger = logging.getLogger('independent-logger')
    request_logger_message(resource, http_verb, start_request_timer)
    independent_logger.setLevel(logging.ERROR)
    independent_logger.error(f"Server encountered an error ! message: {error_message}",
                             extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
    independent_logger.setLevel(independent_logger_level)
    return {"error-message": error_message}, 409


def stack_error_message(resource, http_verb, start_request_timer, error_message):
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    stack_logger = logging.getLogger('stack-logger')
    request_logger_message(resource, http_verb, start_request_timer)
    stack_logger.setLevel(logging.ERROR)
    stack_logger.error(f"Server encountered an error ! message: {error_message}",
                       extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
    stack_logger.setLevel(stack_logger_level)
    return {"error-message": error_message}, 409


def get_logger_level_str(logger_level):
    if logger_level == logging.INFO:
        return 'INFO'
    elif logger_level == logging.DEBUG:
        return 'DEBUG'
    elif logger_level == logging.WARNING:
        return 'WARNING'
    elif logger_level == logging.ERROR:
        return 'ERROR'
    elif logger_level == logging.CRITICAL:
        return 'CRITICAL'


def update_default_logger_level(logger_name, logger_level):
    if logger_name == "request-logger":
        global request_logger_level
        request_logger_level = logger_level
    elif logger_name == "stack-logger":
        global stack_logger_level
        stack_logger_level = logger_level
    elif logger_name == "independent-logger":
        global independent_logger_level
        independent_logger_level = logger_level
    return


@server.route('/independent/calculate', methods=['POST'])
def independent_calculator():
    start_request_timer = time.time()
    http_verb = 'POST'
    resource = '/independent/calculate'
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    independent_logger = logging.getLogger('independent-logger')
    json_request = request.get_json()
    operator = json_request['operation']
    operator_lower_case = operator.lower()
    args = json_request['arguments']
    args_len = len(args)
    result = 0
    if operator_lower_case in binary_operations:
        if args_len < 2:
            error_message = "Error: Not enough arguments to perform the operation " + operator
            return independent_error_message(resource, http_verb, start_request_timer, error_message)
        elif args_len > 2:
            error_message = "Error: Too many arguments to perform the operation " + operator
            return independent_error_message(resource, http_verb, start_request_timer, error_message)
        else:
            x = args[0]
            y = args[1]
            if operator_lower_case == "plus":
                result = x + y
            elif operator_lower_case == "minus":
                result = x - y
            elif operator_lower_case == "times":
                result = x * y
            elif operator_lower_case == "divide":
                if y == 0:
                    error_message = "Error while performing operation Divide: division by 0"
                    return independent_error_message(resource, http_verb, start_request_timer, error_message)
                result = int(x / y)
            elif operator_lower_case == "pow":
                result = pow(x, y)
            request_logger_message(resource, http_verb, start_request_timer)
            independent_logger.info(f"Performing operation {operator}. Result is {result}",
                                    extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            independent_logger.debug(f"Performing operation: {operator}({x},{y}) = {result}",
                                     extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            return {"result": result}, 200
    elif operator_lower_case in unary_operations:
        if args_len < 1:
            error_message = f"Error: Operation {operator} require one argument"
            return independent_error_message(resource, http_verb, start_request_timer, error_message)
        elif args_len > 1:
            error_message = "Error: Too many arguments to perform the operation " + operator
            return independent_error_message(resource, http_verb, start_request_timer, error_message)
        else:
            x = args[0]
            if operator_lower_case == "abs":
                result = abs(x)
            elif operator_lower_case == "fact":
                if x < 0:
                    error_message = 'Error while performing operation Factorial: not supported for the negative number'
                    return independent_error_message(resource, http_verb, start_request_timer, error_message)
                else:
                    result = factorial(x)
            request_logger_message(resource, http_verb, start_request_timer)
            independent_logger.info(f"Performing operation {operator}. Result is {result}",
                                    extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            independent_logger.debug(f"Performing operation: {operator}({x}) = {result}",
                                     extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            return {"result": result}, 200
    else:
        error_message = f"unknown operation {operator}"
        return independent_error_message(resource, http_verb, start_request_timer, error_message)


def stack_calculator(operator, args_len, resource, http_verb, start_request_time):
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    result = 0
    operator_lower_case = operator.lower()
    stack_logger = logging.getLogger('stack-logger')
    if operator_lower_case in binary_operations:
        if args_len < 2:
            error_message = f"Error: cannot implement operation {operator}. " \
                            f"It requires 2 arguments and the stack has only {args_len} arguments"
            return stack_error_message(resource, http_verb, start_request_time, error_message)
        else:
            x = stack.pop()
            y = stack.pop()
            stack_size = len(stack)
            if operator_lower_case == "plus":
                result = x + y
            elif operator_lower_case == "minus":
                result = x - y
            elif operator_lower_case == "times":
                result = x * y
            elif operator_lower_case == "divide":
                if y == 0:
                    error_message = "Error while performing operation Divide: division by 0"
                    return stack_error_message(resource, http_verb, start_request_time, error_message)
                result = int(x / y)
            elif operator_lower_case == "pow":
                result = pow(x, y)
            request_logger_message(resource, http_verb, start_request_time)
            stack_logger.info(f"Performing operation {operator}. Result is {result} | stack size: {stack_size}",
                              extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            stack_logger.debug(f"Performing operation: {operator}({x},{y}) = {result}",
                               extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            return {"result": result}, 200
    elif operator_lower_case in unary_operations:
        if args_len == 0:
            error_message = f"Error: cannot implement operation {operator}. It requires 1 arguments and the stack is " \
                            f"empty"
            return stack_error_message(resource, http_verb, start_request_time, error_message)
        else:
            x = stack.pop()
            stack_size = len(stack)
            if operator_lower_case == "abs":
                result = abs(x)
            elif operator_lower_case == "fact":
                if x < 0:
                    error_message = "Error while performing operation Factorial: not supported for the negative number"
                    return stack_error_message(resource, http_verb, start_request_time, error_message)
                else:
                    result = factorial(x)
            request_logger_message(resource, http_verb, start_request_time)
            stack_logger.info(f"Performing operation {operator}. Result is {result} | stack size: {stack_size}",
                              extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            stack_logger.debug(f"Performing operation: {operator}({x}) = {result}",
                               extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
            return {"result": result}, 200
    else:
        error_message = "Error: Unknown operation " + operator
        return stack_error_message(resource, http_verb, start_request_time, error_message)


@server.route('/stack/size', methods=['GET'])
def get_stack_size():
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    start_request_time = time.time()
    resource = '/stack/size'
    http_verb = 'GET'
    stack_logger = logging.getLogger('stack-logger')
    stack_size = len(stack)
    stack_logger.info(f"Stack size is {stack_size}",
                      extra={'request-number': requests_counter, 'date-time-str': date_time_str})
    reverse_elements_list = list(reversed(stack))
    request_logger_message(resource, http_verb, start_request_time)
    stack_logger.debug(f"Stack content (first == top): {reverse_elements_list[:]}",
                       extra={'request-number': requests_counter-1, 'date-time-str': date_time_str})
    return {"result": stack_size}, 200


@server.route('/stack/arguments', methods=["PUT"])
def add_args_to_stack():
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    start_request_time = time.time()
    http_verb = 'PUT'
    resource = '/stack/arguments'
    stack_logger = logging.getLogger('stack-logger')
    json_request = request.get_json()
    args = json_request['arguments']
    args_len = len(args)
    if args_len == 0:
        error_message = "Error: No arguments to add"
        return stack_error_message(resource, http_verb, start_request_time, error_message)
    for argument in args:
        if type(argument) != int:
            error_message = "Error: invalid argument"
            return stack_error_message(resource, http_verb, start_request_time, error_message)
        else:
            stack.append(argument)
    stack_size_before_add = len(stack) - args_len
    request_logger_message(resource, http_verb, start_request_time)
    stack_logger.info(f"Adding total of {args_len} argument(s) to the stack | Stack size: {len(stack)}",
                      extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
    args_elements_list = [str(item) for item in args]
    str_elements_list = ','.join(args_elements_list)
    stack_logger.debug(
        f"Adding arguments: {str_elements_list} | Stack size before {stack_size_before_add} | stack size after {len(stack)}",
        extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
    return {"result": len(stack)}, 200


@server.route('/stack/operate', methods=["GET"])
def preform_operate():
    global requests_counter
    resource = "/stack/operate"
    http_verb = 'GET'
    start_request_time = time.time()
    query_parm = request.args
    operator = query_parm.get("operation", type=str)
    args_len = len(stack)
    return stack_calculator(operator, args_len, resource, http_verb, start_request_time)


@server.route('/stack/arguments', methods=["DELETE"])
def remove_arguments():
    global requests_counter
    date_time = datetime.now()
    date_time_str = date_time.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
    resource = "/stack/arguments"
    http_verb = 'DELETE'
    start_request_time = time.time()
    stack_logger = logging.getLogger('stack-logger')
    query_parm = request.args
    count = query_parm.get("count", type=int)
    count_for_log = count
    stack_len = len(stack)
    if count > stack_len:
        error_message = f"Error: cannot remove {count} from the stack. It has only {stack_len} arguments"
        return stack_error_message(resource, http_verb, start_request_time, error_message)
    else:
        while count > 0:
            stack.pop()
            count = count - 1
    stack_len = len(stack)
    request_logger_message(resource, http_verb, start_request_time)
    stack_logger.info(f"Removing total {count_for_log} argument(s) from the stack | Stack size: {stack_len}",
                      extra={'date-time-str': date_time_str, 'request-number': requests_counter - 1})
    return {"result": len(stack)}, 200


@server.route('/logs/level', methods=['GET'])
def get_logger_level():
    global requests_counter
    start_request_timer = time.time()
    resource = '/logs/level'
    http_verb = 'GET'
    query_parm = request.args
    logger_name = query_parm.get("logger-name", type=str)
    if logger_name not in logging.Logger.manager.loggerDict.keys():
        error_message = f"Error: The Logger-Name {logger_name} not valid!"
        request_logger_message(resource, http_verb, start_request_timer)
        return error_message, 409
    else:
        logger = logging.getLogger(logger_name)
        loger_level_str = get_logger_level_str(logger.level)
        request_logger_message(resource, http_verb, start_request_timer)
        return f"{logger_name} Level: {loger_level_str}", 200


@server.route('/logs/level', methods=['PUT'])
def set_logger_level():
    global requests_counter
    start_request_timer = time.time()
    resource = '/logs/level'
    http_verb = 'PUT'
    query_parm = request.args
    logger_name = query_parm.get("logger-name", type=str)
    logger_level = query_parm.get("logger-level", type=str)
    new_level = logger_level.upper()
    if logger_name not in logging.Logger.manager.loggerDict.keys():
        error_message = f"Error: Logger-Name {logger_name} not valid!"
        request_logger_message(resource, http_verb, start_request_timer)
        return error_message, 409
    elif new_level not in log_levels:
        error_message = f"Error: Logger-Level {logger_name} not valid!"
        request_logger_message(resource, http_verb, start_request_timer)
        return error_message, 409
    else:
        logger = logging.getLogger(logger_name)
        logger.setLevel(new_level)
        update_default_logger_level(logger_name, new_level)
        request_logger_message(resource, http_verb, start_request_timer)
        return f"{new_level}", 200


if __name__ == '__main__':
    files_creator()
    create_logger_method()
    server.run(host="0.0.0.0", port=9285, debug=False)
