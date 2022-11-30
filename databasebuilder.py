import csv, pickle
import pandas as pd
from dotenv import load_dotenv
from table import Base, SpringDemand, SpringCourses, NLPFormat
from sqlite3 import connect as sqlite_connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from codes import DEPARTMENTS
from io import StringIO 
from html.parser import HTMLParser

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re 

STOPWORDS = set(stopwords.words('english'))
MIN_WORDS = 1
MAX_WORDS = 1500

PATTERN_S = re.compile("\'s")  # matches `'s` from text  
PATTERN_RN = re.compile("\\r\\n") # matches `\r` and `\n`
PATTERN_PUNC = re.compile(r"[^\w\s]") # matches all non 0-9 A-z whitespace 

load_dotenv()

S23_DEMAND = "/Users/zhaoamyx/Desktop/CPSC437/Final/db_final/full_spring_demand.csv"

def tag_courseid():

    with open('spring_courses', 'rb') as fp:
        all_schools = pickle.load(fp)

    counter = 0
    flat_list = [course for school in all_schools for course in school]

    seen = []
    final_list = []

    for course in flat_list:
        if course["subjectNumber"] not in seen:
            final_list.append(course)

    for c in final_list:
        c["courseId"] = counter
        counter += 1

    return flat_list

COURSE_LIST = tag_courseid()


def populate_courses(sql_session):

    '''
    Adds all courses from all schools to the springcourses table in the database.

        Parameters:
            sql_session: The session that is responsible for creating the database.

        Returns:
            none
    '''

    for course in COURSE_LIST:
        new_course = SpringCourses(term=course['termCode'], courseid=course["courseId"], fullcode=course["subjectCode"] + ' ' + course["courseNumber"], deptcode=course['department'], subcode=course["subjectCode"], deptname=DEPARTMENTS[course['department']], coursenum=course['courseNumber'], title=course['courseTitle'], description=course['description'], school=course['schoolDescription'])
        sql_session.add(new_course)

    sql_session.commit()

def get_courseid(subject_code, course_number):

    for course in COURSE_LIST:
        if subject_code == course["subjectCode"] and course_number == course["courseNumber"]:
            return course["courseId"]

def create_demand_dict():

    with open(S23_DEMAND, 'r') as spring_demand:
        all_course_demand = csv.reader(spring_demand)
        all_course_demand = list(all_course_demand)
        del all_course_demand[0]
        all_course_copy = all_course_demand

    full_dict = []

    for course in all_course_copy:
        courseid = get_courseid(course[3], course[4])
        full_dict.append({ "courseid": courseid, "coursecode": course[3] + ' ' + course[4], "coursetitle": course[8], "coursedemand": course[11]})

    return full_dict

def populate_demand(demand_dict, sql_session):

    seen_ids = []

    for count, course in enumerate(demand_dict):
        if (count + 1 < len(demand_dict)) and (course["courseid"] != None) and course["courseid"] not in seen_ids:
            next = demand_dict[count + 1]
            if course["coursecode"] != next["coursecode"]:
                # print("Course ID: ", course["courseid"], "Course Title: ", course["coursetitle"])
                new_demand = SpringDemand(courseid=course["courseid"], coursecode=course["coursecode"], coursetitle=course["coursetitle"], coursedemand=course["coursedemand"])
                seen_ids.append(course["courseid"])
                sql_session.add(new_demand)

    sql_session.commit()

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def strip_all_tags():
    for course in COURSE_LIST:
        if course["description"] != None:
            course["description"] = strip_tags(course["description"])

    return COURSE_LIST

COURSE_LIST = strip_all_tags()

def clean_text(text):
    text = text.lower()
    text = re.sub(PATTERN_S, ' ', text)
    text = re.sub(PATTERN_RN, ' ', text)
    text = re.sub(PATTERN_PUNC, ' ', text)
    return text

def tokenizer(sentence, min_words=MIN_WORDS, max_words=MAX_WORDS, stopwords=STOPWORDS, lemmatize=True):
    if lemmatize:
        stemmer = WordNetLemmatizer()
        tokens = [stemmer.lemmatize(w) for w in word_tokenize(sentence)]
    else:
        tokens = [w for w in word_tokenize(sentence)]

    tokens = [w for w in tokens if (len(w) > min_words and len(w) < max_words and w not in stopwords)]
    return tokens 

def clean_data():
    for course in COURSE_LIST:
        if course["description"] != None:
            course["cleansentence"] = clean_text(course["description"])
            course["toklemsentence"] = tokenizer(course["cleansentence"], min_words=MIN_WORDS, max_words=MAX_WORDS, stopwords=STOPWORDS, lemmatize=True)
        else:
            course["cleansentence"] = ''
            course["toklemsentence"] = ''

    return COURSE_LIST

COURSE_LIST = clean_data()

def populate_nlp_data(sql_session):
    for course in COURSE_LIST:
        if course["toklemsentence"] != '':
            converted_tl = '|'.join(course["toklemsentence"])
        else:
            converted_tl = ''
        new_nlp_data = NLPFormat(courseid=course["courseId"], cleansentence=course["cleansentence"], tokenlemmasentence=converted_tl)
        sql_session.add(new_nlp_data)

    sql_session.commit()

if __name__ == "__main__":

    engine = create_engine(
        'sqlite://',
        creator=lambda: sqlite_connect(
            'file:' + 'database.sqlite' + '?mode=rwc', uri=True
        )
    )

    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    populate_courses(session)
    demand_dict = create_demand_dict()
    populate_demand(demand_dict, session)
    populate_nlp_data(session)

    print("Done")