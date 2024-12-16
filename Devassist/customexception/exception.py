import traceback
import sys

def custom_exception() -> str:
    exc_type, exc_value, tb = sys.exc_info() 
    if tb is None:  
        return "No exception traceback available."

    traceback_details = traceback.extract_tb(tb)
    error_details = [f"File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}" for frame in traceback_details]

    formatted_error = "\n".join(error_details)
    exception_message = f"Exception Type: {exc_type.__name__}, Message: {exc_value}"

    return f"{formatted_error}\n{exception_message}"
