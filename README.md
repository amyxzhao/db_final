# Final Project–CPSC 437: Introduction to Database Systems

## Team Members
- Kelvin Yip
- Amy Zhao
- Lily Zhou

## Setup (Please Read!) 
Several files in the repository are meant to set up the database. If you are not part of the development of this project, you shouldn't need to run them. If you are part of development, you shouldn't need to run them either (unless you're curious, and you have a lot of time; the scrapers are pretty slow). Below is a description of each setup file. 

### `codes.py`
This file contains two dictionaries: (1) all subjects offered at Yale, and (2) all schools under Yale. These are used to pull courses from the API.

### `pull_courses.py`
This file queries the Yale Courses API and pulls all courses from all Yale schools (College and graduate schools) for the Fall 2022 and Spring 2023 semesters. It pickles the data into `fall_courses.pkl` and `spring_courses.pkl` as temporary storage. Never un-pickle data you do not trust! 

### `demand_scraper.py`
This scraper is borrowed from the YDN Data Desk where Amy was a previous editor who contributed to the writing of the code. It accesses Yale Course Demand Statistics and pulls the demand numbers for all courses in a particular semester. The statistics are saved in csv files.  

### `table.py`
This file sets up the database tables. There are four: a courses table and a demand table for each semester. 

### `databasebuilder.py`
This file constructs the database with tables and columns as defined in `table.py`. It uses data obtained from the Yale Courses API and the Course Demand Statistics scraper. 