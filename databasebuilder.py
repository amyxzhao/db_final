import csv
import pandas as pd
from dotenv import load_dotenv
from table import Base, FallDemand, SpringDemand
from sqlite3 import connect as sqlite_connect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

def format_crosslistings(course_data):
    print("Working")

def find_corresonding_course_name(course_data, id):

    with open(course_data, 'r') as csvfile:
        all_courses = csv.reader(csvfile)
        for row in all_courses:
            if id == row[0]:
                return row[2]


def find_corresonding_course_code(course_data, id):

    with open(course_data, 'r') as csvfile:
        all_courses = csv.reader(csvfile)
        for row in all_courses:
            if id == row[0]:
                return row[1]

def populate_fall_courses(course_data, sql_session):
    print("Working")

def populate_fall_demand(course_data, demand_data, sql_session, dates):

    d = pd.read_csv(demand_data)
    demand_length = len(d)

    with open(demand_data, 'r') as csvfile:
        all_demand = csv.reader(csvfile)
        all_demand = list(all_demand)

        for i in range(dates + 1, demand_length, dates):
            if i < demand_length:
                current_course = all_demand[i]
                code = find_corresonding_course_code(course_data, current_course[0])
                subject_code = code[:-3]
                section = code[-2:]
                title = find_corresonding_course_name(course_data, current_course[0])
                print(current_course, subject_code, title)
                new_demand = FallDemand(courseid=current_course[0], coursecode=subject_code, section=section, coursetitle=title, coursedemand=current_course[2])
                sql_session.add(new_demand)
    
    sql_session.commit()

def populate_spring_courses(course_data, sql_session):
    print("Working")

def populate_spring_demand(course_data, demand_data, sql_session, dates):
    d = pd.read_csv(demand_data)
    demand_length = len(d)

    with open(demand_data, 'r') as csvfile:
        all_demand = csv.reader(csvfile)
        all_demand = list(all_demand)

        for i in range(dates + 1, demand_length, dates):
            current_course = all_demand[i]
            code = find_corresonding_course_code(course_data, current_course[0])
            subject_code = code[:-3]
            section = code[-2:]
            title = find_corresonding_course_name(course_data, current_course[0])
            new_demand = SpringDemand(courseid=current_course[0], coursecode=subject_code, section=section, coursetitle=title, coursedemand=current_course[2])
            sql_session.add(new_demand)
    
    sql_session.commit()

if __name__ == "__main__":

    engine = create_engine(
        'sqlite://',
        creator=lambda: sqlite_connect(
            'file:' + 'database.sqlite' + '?mode=rwc', uri=True
        )
    )

    fall_courses = "/Users/zhaoamyx/Desktop/CPSC437/Final/db_final/courses_fall22.csv"
    fall_demand = "/Users/zhaoamyx/Desktop/CPSC437/Final/db_final/demand_fall22.csv"
    spring_courses = "/Users/zhaoamyx/Desktop/CPSC437/Final/db_final/courses_spring23.csv"
    spring_demand = "/Users/zhaoamyx/Desktop/CPSC437/Final/db_final/demand_spring23.csv"

    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    populate_fall_demand(fall_courses, fall_demand, session, 7)
    populate_spring_demand(spring_courses, spring_demand, session, 8)

    print("Done")