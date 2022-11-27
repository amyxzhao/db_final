import json, os, requests
from dotenv import load_dotenv

load_dotenv()

def get_courses(subj_code, term_code):
    """Given subject code and term_code, get relevant courses"""

    if term_code is not None:

        parameters = {
            "apikey": os.environ.get("API_KEY"),
            # "apikey": qwerqerqwerqr, # uncomment this line if dot_env is being weird
            "subjectCode": subj_code,
            "termCode": term_code,
            "mode": "json"
        }
    else:
        parameters = {
            "apikey": os.environ.get("API_KEY"),
            # "apikey": qwerqerqwerqr, # uncomment this line if dot_env is being weird
            "subjectCode": subj_code,
            "mode": "json"
        }

    response = requests.get(
        "https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index",
        params=parameters,
        timeout=30,
    )

    response_list = json.loads(response.text)
    return response_list

