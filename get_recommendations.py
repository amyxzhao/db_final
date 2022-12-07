from contextlib import closing
from recommendations import Recommendation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlite3 import connect


DB_PATH = 'file:database.sqlite'

def get_matching(title_snip):
    
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            v = '%' + title_snip + '%'
            query_string = "SELECT courseid, coursecode, coursetitle from springdemand WHERE coursetitle LIKE ?"
            cursor.execute(query_string, [v])
            
            return cursor.fetchall()

def get_course_descriptions():
    '''
    Returns a list of course descriptions for all courses in the database.

        Parameters:
            none

        Returns:
            all_descriptions: List of strings, each of which is a course description.
    '''
    
    all_descriptions = []

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT cleansentence from nlpformat"
            cursor.execute(query_string)

            row = cursor.fetchone()
            while row is not None:
                all_descriptions.append(row[0])
                row = cursor.fetchone()

    return all_descriptions

def get_courseid(coursetitle):
    '''
    Returns the course id for a given course title by querying the database.

        Parameters:
            coursetitle: The full title of the course to search.

        Returns:
            row[0]: The courseid corresponding to the tile. 
    '''

    # TODO: Address the crosslisting issue!

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT courseid from springcourses WHERE title=?"
            cursor.execute(query_string, [coursetitle])

            row = cursor.fetchone()
            return row[0]

def get_coursetitle(courseid):
    '''
    Returns the course title for a given course id by querying the database.
    
        Parameters:
            courseid: The course id of the course to search.
        
        Returns:
            new_title: A dictionary containing the course number and the course title. 
    
    '''

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT coursetitle from springdemand WHERE courseid=?"
            cursor.execute(query_string, [courseid])

            row = cursor.fetchone()

            return row[0]

def create_tfidf(course_descriptions):
    '''
    Create a matrix for the term frequency-inverse document frequency for all course descriptions. 

        Parameters:
            course_descriptions: A list of strings that contains all course descriptions.

        Returns:
            tfidf_matrix: A transformed matrix for tfidf suitable for processing.
    '''

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(course_descriptions)

    return tfidf_matrix

def create_cosine_matrix(tfidf_matrix):
    '''
    Creates a cosine similarity matrix which assigns a numerical value for the similarity between every pair of courses.

        Parameters:
            tfidf_matrix: The formatted matrix returned by create_tfidf(course_descriptions)

        Returns:
            cosine_sim: A square similarity matrix for all courses with course descriptions.
    '''
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def get_recommendations(coursetitle, cosine_sim):
    '''
    Gets a list of the top ten most similar courses to a given input course.

        Parameters:
            coursetitle: The title of the course to get recommendations for.
            cosine_sim: The cosine similarity matrix.

        Returns:
            course_names: List of dictionaries that represent the most similar courses to the one provided. 
    '''
    idx = get_courseid(coursetitle)
    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores.sort(key=lambda x: x[1], reverse=True)

    # Top 20 matching courses. 
    top_scores = sim_scores[1:50]

    # TODO: Crosslisting issue persists :(

    course_names = []
    for course in top_scores:
        c_dict = {}
        c_dict["courseid"], c_dict["similarity_score"] = course[0], course[1]
        course_names.append(c_dict)

    return course_names[0:10]

def build_rec_table(course_names):
    
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:

            clean_up_query = "DROP TABLE IF EXISTS courserecs"
            cursor.execute(clean_up_query)

            create_base_query = "CREATE TABLE courserecs (courseid INTEGER PRIMARY KEY, similarity NUMERIC(3, 5))"
            cursor.execute(create_base_query)

            for c in course_names:
                insert_query = f"INSERT INTO courserecs VALUES ({c['courseid']}, {c['similarity_score']})"
                cursor.execute(insert_query)

def sort_by_sim():
    
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            sort_similarity_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid ORDER BY similarity DESC"
            
            cursor.execute(sort_similarity_query)

            sorted_by_similarity = cursor.fetchall()
            return sorted_by_similarity

def sort_by_demand():

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            sort_demand_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid ORDER BY coursedemand DESC"

            cursor.execute(sort_demand_query)

            sorted_by_demand = cursor.fetchall()
            return sorted_by_demand

def get_overall_demand():
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            overall_avg_query = "SELECT AVG(d.coursedemand) FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid"

            cursor.execute(overall_avg_query)

            row = cursor.fetchone()
            overall_avg_demand = row[0]

            return overall_avg_demand

def get_dept_demand():
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            avg_by_dept_query = "SELECT s.deptname, AVG(d.coursedemand) FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid GROUP BY s.deptname"

            cursor.execute(avg_by_dept_query)

            avg_demand_by_dept = cursor.fetchall()
            return avg_demand_by_dept

def get_dept_count():
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            count_query = "SELECT s.deptname, COUNT(*) FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid GROUP BY s.deptname"

            cursor.execute(count_query)

            course_count_by_dept = cursor.fetchall() # Formatted as a list of tuples (department name, count).
            return course_count_by_dept

def get_popular_recs():
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            high_demand_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid WHERE d.coursedemand > (SELECT AVG(d.coursedemand) FROM courserecs c LEFT JOIN springdemand d)"

            cursor.execute(high_demand_query)

            high_demand_courses = cursor.fetchall()
            return high_demand_courses

def get_unpopular_recs():
     with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            low_demand_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid WHERE d.coursedemand < (SELECT AVG(d.coursedemand) FROM courserecs c LEFT JOIN springdemand d)"

            cursor.execute(low_demand_query)

            low_demand_courses = cursor.fetchall()
            return low_demand_courses
