import csv, json, os, pickle, requests
from dotenv import load_dotenv
from progressbar import progressbar
from codes import SCHOOLS

load_dotenv()

def get_courses(subj_code, term_code, school):
    """Given subject code and term_code, get relevant courses"""

    if term_code is not None:

        parameters = {
            "apikey": os.environ.get("API_KEY"),
            # "apikey": qwerqerqwerqr, # uncomment this line if dot_env is being weird
            "subjectCode": subj_code,
            "termCode": term_code,
            "mode": "json", 
            "school": school,
        }
    else:
        parameters = {
            "apikey": os.environ.get("API_KEY"),
            # "apikey": qwerqerqwerqr, # uncomment this line if dot_env is being weird
            "subjectCode": subj_code,
            "mode": "json", 
            "school": school,
        }

    response = requests.get(
        "https://gw.its.yale.edu/soa-gateway/courses/webservice/v3/index",
        params=parameters,
        timeout=30,
    )

    response_list = json.loads(response.text)
    return response_list

def get_subj_codes():
    """Get all subject codes"""

    parameters = {
        "apikey": os.environ.get("API_KEY"),
        # "apikey": qwerqerqwerqr, # uncomment this line if dot_env is being weird
        "mode": "json"
    }

    response = requests.get(
        "https://gw.its.yale.edu/soa-gateway/course/webservice/v2/subjects",
        params=parameters,
        timeout=30,
    )

    response_list = json.loads(response.text)

    subj_codes = [subj["code"] for subj in response_list]

    return subj_codes

def get_all_courses(term_code, school):
    """Given term_code, get relevant courses"""

    print("Accessing all courses...")
    subj_codes = get_subj_codes()
    all_courses = []

    for subj_code in progressbar(subj_codes):
        response_list = get_courses(subj_code, term_code, school)
        for class_info in response_list:
            all_courses.append(class_info)

    return all_courses

def get_all_courses_all_schools(term_code):

    dict_list = []
    
    for school in SCHOOLS:
        c = get_all_courses(term_code, school)
        dict_list.append(c)

    return dict_list

if __name__ == "__main__":

    # term = '202203'
    # fall_results = get_all_courses_all_schools(term)

    # with open('fall_courses', 'wb') as fp:
    #     pickle.dump(fall_results, fp)

    term = '202301'
    spring_results = get_all_courses_all_schools(term)
    
    with open('spring_courses', 'wb') as fp:
        pickle.dump(spring_results, fp)