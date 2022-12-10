# Final Project–CPSC 437: Introduction to Database Systems

## Team Members
- Kelvin Yip
- Amy Zhao
- Lily Zhou

## How to Run
The project includes a web application. To start the web app, run the script `runserver.py` by executing:
```
python runserver.py [port-number]
```

## Project Setup (Please Read!) 
Several files in the repository are meant to set up the database or retrieve data. If you are not part of the development of this project, you shouldn't need to run them. If you are part of development, you shouldn't need to run them either (unless you're curious, and you have a lot of time; the scrapers are pretty slow). Below is a description of each setup file. 

### `requirements.txt`
This file contains a list of all the relevant Python libraries. First, make sure you have `pip` on your machine. You can install them by running the following:
```
pip install -r requirements.txt
```

### `codes.py`
This file contains two dictionaries: (1) all subjects offered at Yale, and (2) all schools under Yale. These are used to pull courses from the API.

### `databasebuilder.py`
This file constructs the database with tables and columns as defined in `table.py`. The functions used to format the course descriptions are also found in this file. For more detailed information, please see the docstrings for each function.

### `get_recommendations.py`
This file includes functions that build the necessary matrices for computing the similarity scores between each pair of courses. It also includes functions that queries the data tables, fetching information such as course description and course demand statistics.

### `pull_courses.py`
This file queries the Yale Courses API and pulls all courses from all Yale schools (College and graduate schools) for the Fall 2022 and Spring 2023 semesters. This program uses an API key. To replicate this locally, create a `.env` file and include the following line:
```
API_KEY=QWERTY12345
```
where `QWERTY12345` represents your actual API key.
The program proceeds to pickles the data into `fall_courses.pkl` and `spring_courses.pkl` as temporary storage. Never un-pickle data you do not trust! Note: For the sake of this project, we will focus on Spring 2023 courses. 

### `rec_app.py`
This file constructs the Flask application for the web server and defines its routes.

### `runserver.py`
Running this script launches a local development server that runs the web application. It requires an argument of port number. To run this script, execute `python runserver.py [port-number]`.

### `table.py`
This file sets up the database tables. There are three tables: 
- `springcourses`: Contains course information for all courses offered during the Spring 2023 semester; data retrieved using the Yale Courses API. 
- `springdemand`: Contains demand information (number of people registered) for each course; data retrieved directly from Yale Course Demand Statistics. 
- `nlpformat`: Contains various formats of the course description string for natural language processing purposes. 

### Others

- `/static`: This directory includes files for styling the web application.
- `/template`: This directory includes html templates that will be used to create the web application.
- `/course_csv`: This directory includes CSV files for the course information and demand statistics of Fall 2022 and Spring 2023. These are not directly used in the project, but provide helpful reference information.
- `progressbar.py`: Borrowed from department lecturer Alan Weide, this is essentially a sanity check. When the API calls are running, this gives a visual representation in the terminal of the progress. It holds no actual bearing on the functionality of the project. 
