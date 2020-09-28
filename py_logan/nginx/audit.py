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


def parse_nginx_log(string: str) -> list:
    """
        parses nginx log file and returns the data

            >>> parse_nginx_log('''127.0.0.1 - - [27/Sep/2020:06:50:38 +0000] "GET / HTTP/1.1" 200 31502 "https://example.com/page/referer/" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1"''')
            [{'ip': '127.0.0.1', 'date': '27/Sep/2020:06:50:38 +0000', 'path': '/', 'status_code': '200', 'bandwidth': '31502', 'referrer': 'https://example.com/page/referer/', 'user_agent': {'user_agent': {'family': 'Mobile Safari', 'major': '13', 'minor': '1', 'patch': '2'}, 'os': {'family': 'iOS', 'major': '13', 'minor': '7', 'patch': None, 'patch_minor': None}, 'device': {'family': 'iPhone', 'brand': 'Apple', 'model': 'iPhone'}, 'string': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1'}}]
    """
    result = []
    pattern = (
        r""
        "(\d+.\d+.\d+.\d+)\s-\s-\s"  # ip
        "\[(.+)\]\s"  # date_time
        '"GET\s(.+)\s\w+/.+"\s'  # url
        "(\d+)\s"  # status_code
        "(\d+)\s"  # bandwidth
        '"(.+)"\s'  # referrer
        '"(.+)"'  # user_agent
    )
    match_results = re.findall(pattern, string)
    if match_results:
        for match in match_results:
            data = dict()
            (
                data["ip"],
                data["date"],
                data["path"],
                data["status_code"],
                data["bandwidth"],
                data["referrer"],
                data["user_agent"],
            ) = match
            data["user_agent"] = user_agent_parser.Parse(data["user_agent"])
            result.append(data)
    return result


def parse_logs(dir_path: str) -> list:
    """
    parse all the text files containing logs & extract the log data
        >>> parse_logs("path/to/log/dir/")
        []
    """
    logs = []
    for log_file in get_log_files(dir_path):
        try:
            with open(log_file, "r") as f:
                text = f.read()
                logs.extend(parse_nginx_log(text))
        except Exception as e:
            print(e)

    return logs


def get_ip_information(ip: str) -> dict:
    """
    fetches ip information from http://ipinfo.io/
        >>> get_ip_information('8.8.8.8')
        {'ip': '8.8.8.8', 'hostname': 'dns.google', 'city': 'Mountain View', 'region': 'California', 'country': 'US', 'loc': '37.4056,-122.0775', 'org': 'AS15169 Google LLC', 'postal': '94043', 'timezone': 'America/Los_Angeles', 'readme': 'https://ipinfo.io/missingauth'}
    """
    r = requests.get("http://ipinfo.io/{}".format(ip))
    if r.status_code == 200:
        return r.json()
    else:
        print(r.content)
        return None


def get_demographic(data: list) -> list:
    return list(map(get_ip_information, set(i["ip"] for i in data)))


def generate_csv_reports(log_dir: str) -> None:
    log_dir = "logs/"
    demographic_csv = "demographic_report.csv"
    main_report_csv = "main_report.csv"
    data = parse_logs(log_dir)
    if not data:
        print("No Log data found in the dir {}".format(log_dir))
        return None
    demographic = get_demographic(data)
    demographic_df = pd.DataFrame()
    main_df = pd.DataFrame()
    main_df = main_df.append(data)
    if demographic:
        demographic_df = demographic_df.append(demographic)
        ips = [i["ip"] for i in data]
        demographic_df["number_of_visits"] = demographic_df["ip"].apply(
            lambda ip: ips.count(ip)
        )
        demographic_df.to_csv(demographic_csv, index=False)
        main_df = pd.merge([main_df, demographic_df], on=["ip"], how="inner")
    main_df.to_csv(main_report_csv, index=False)

