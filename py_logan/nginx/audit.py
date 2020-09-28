from glob import glob
import re
from ua_parser import user_agent_parser
from pprint import pprint
import requests
import pandas as pd
from datetime import datetime


def get_log_files(dir_path: str, pattern: str = "*log*") -> list:
    """
    grabs path of all the files that has log in their filenames.
        >>> get_log_files('path/of/dir/')
        []
    """
    filenames = []
    for file_name in glob(dir_path + pattern):
        filenames.append(file_name)
    return filenames