from langchain_core.tools import tool
from datetime import datetime

@tool
def get_current_time()->str:
    """
    :return: Current timestamp in system time zone
    """
    current_time_ist = datetime.now()
    formatted_timestamp = current_time_ist.strftime('%Y-%m-%d %H:%M:%S')
    print(formatted_timestamp)

    return str(formatted_timestamp)

