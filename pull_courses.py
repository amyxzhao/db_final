import json, os, pickle, requests

from codes import SCHOOLS
from dotenv import load_dotenv
from progressbar import progressbar

load_dotenv()

def get_courses(subj_code, term_code, school):
    """Given subject code and term_code, get relevant courses"""
    '''
    Returns a list of courses formatted as dictionaries that meet the specified parameters of subject, term, and school.

        Parameters:
            subj_code: The subject area that the course belongs to.
            term_code: The term in which the course is offered in. 
            school: The school in which the course is offered in. 

        Returns:
            response_list: List of all courses in a specified subject, term, and school. 
    '''

    if term_code is not None:

        parameters = {
            "apikey": os.environ.get("API_KEY"),
            "subjectCode": subj_code,
            "termCode": term_code,
            "mode": "json", 
            "school": school,
        }
    else:
        parameters = {
            "apikey": os.environ.get("API_KEY"),
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
    '''
    Returns a list of all subject codes at Yale, pulled from the Yale Subjects API.

        Parameters:
            none

        Returns:
            subj_codes: List of all subject codes. 
    '''

    parameters = {
        "apikey": os.environ.get("API_KEY"),
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
    '''
    Returns a list of courses for a given term code and school.

        Parameters:
            term_code: A six-digit string that represents the term for the desired courses. 
            school: A two-letter string abbreviation of the school for the desired courses. 

        Returns:
            all_courses: A list of dictionaries for all courses in the school and term specified. 

    '''

    print("Accessing all courses...")
    subj_codes = get_subj_codes()
    all_courses = []

    for subj_code in progressbar(subj_codes):
        response_list = get_courses(subj_code, term_code, school)
        for class_info in response_list:
            all_courses.append(class_info)

    return all_courses

def get_all_courses_all_schools(term_code):
    '''
    Returns a list of lists. Each sublist contains multiple dictionaries, and each dictionary represents a course. 

        Parameters:
            term_code: A six-digit string that represents the term for the desired courses. 

        Returns:
            dict_list: A list of lists that contains dictionaries for all courses in all schools at Yale University.
    '''

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