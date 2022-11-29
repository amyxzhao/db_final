import csv, pickle
import pandas as pd
from dotenv import load_dotenv
from table import Base, SpringDemand, SpringCourses
from sqlite3 import connect as sqlite_connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from codes import DEPARTMENTS

load_dotenv()

S23_DEMAND = "/Users/zhaoamyx/Desktop/CPSC437/Final/db_final/full_spring_demand.csv"

def tag_courseid():

    with open('spring_courses', 'rb') as fp:
        all_schools = pickle.load(fp)

    counter = 0
    flat_list = [course for school in all_schools for course in school]

    for c in flat_list:
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
                print("Course ID: ", course["courseid"], "Course Title: ", course["coursetitle"])
                new_demand = SpringDemand(courseid=course["courseid"], coursecode=course["coursecode"], coursetitle=course["coursetitle"], coursedemand=course["coursedemand"])
                seen_ids.append(course["courseid"])
                sql_session.add(new_demand)
        # # else:
        #     new_demand = SpringDemand(courseid=course["courseid"], coursecode=course["coursecode"], coursetitle=course["coursetitle"], coursedemand=course["coursedemand"])
        #     sql_session.add(new_demand)

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

    print("Done")