from contextlib import closing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlite3 import connect


DB_PATH = 'file:database.sqlite'

def get_matching(title_snip):
    '''
        Returns a list of courses that are related to the inputted course.

        Parameters:
            title_snip: Inputted text that user seeks to find related courses for.

        Returns:
            matching_courses: list of courses.
    '''
    courses = []
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            v = '%' + title_snip + '%'
            query_string = "SELECT courseid, coursecode, coursetitle from springdemand WHERE coursetitle LIKE ? ORDER BY coursecode"
            cursor.execute(query_string, [v])
            courses = cursor.fetchall()
    matching_set = {}
    matching_courses = []
    for course in courses:
        if course[2] not in matching_set:
            modified_course = ([course[0]], course[1], course[2])
            matching_courses.append(modified_course)
            matching_set[course[2]] = len(matching_courses) - 1
        else:
            modified_ids = matching_courses[matching_set[course[2]]][0]
            modified_ids.append(course[0])
            modified_course_code = matching_courses[matching_set[course[2]]][1] + f"/{course[1]}"
            matching_courses[matching_set[course[2]]] = (modified_ids, modified_course_code, matching_courses[matching_set[course[2]]][2])
    return matching_courses

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
            row[0]: The courseid corresponding to the title. 
    '''

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
            row[0]: The coursetitle corresponding to the id.
    
    '''

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT title from springcourses WHERE courseid=?"
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

    course_names = []
    seen_names = set()
    seen_names.add(coursetitle)
    for course in top_scores:
        title = get_coursetitle(course[0])
        if title not in seen_names:
            c_dict = {}
            c_dict["courseid"], c_dict["similarity_score"] = course[0], round(course[1], 5)
            course_names.append(c_dict)
            seen_names.add(title)

    return course_names[0:10]

def build_rec_table(course_names):
    '''
        Builds the table of recommended courses by performing insert queries.

        Parameters:
            course_names: The names of the courses to add to the table.
            
        Returns:
            None
    '''
    
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:

            clean_up_query = "DROP TABLE IF EXISTS courserecs"
            cursor.execute(clean_up_query)

            create_base_query = "CREATE TABLE courserecs (courseid INTEGER PRIMARY KEY, similarity NUMERIC(3, 5))"
            cursor.execute(create_base_query)

            for c in course_names:
                insert_query = f"INSERT INTO courserecs VALUES ({c['courseid']}, {c['similarity_score']})"
                cursor.execute(insert_query)

def query_fetch_all_helper(query):
    '''
        Executes a query and returns all the data that is fetched upon execution.
    
        Parameters:
            query: The query to execute.
        
        Returns:
            results: list of tuples corresponding to the information fetched from executing the query.
    '''
    with connect(DB_PATH, uri=True) as connection:
        with(closing(connection.cursor())) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results

def get_overall_demand():
    '''
        Executes a query that fetches the overall average demand of the related courses.
        
        Returns:
            overall_age_demand: number.
    '''
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            overall_avg_query = "SELECT AVG(d.coursedemand) FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid"

            cursor.execute(overall_avg_query)

            row = cursor.fetchone()
            overall_avg_demand = row[0]
            overall_avg_demand = round(overall_avg_demand, 3)

            return overall_avg_demand

def sort_by_sim():
    '''
        Executes a query that fetches courses related to the selected source sorted by similarity in a descending order.
        
        Returns:
            results: list of courses and useful information, including courseid, title, demand, and similarity score.
    '''
    sort_similarity_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid ORDER BY similarity DESC"
    sorted_by_similarity = query_fetch_all_helper(sort_similarity_query)
    return sorted_by_similarity

def sort_by_demand():
    '''
        Executes a query that fetches courses related to the selected source sorted by demand in a descending order.
        
        Returns:
            results: list of courses and useful information, including courseid, title, demand, and similarity score.
    '''
    sort_demand_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid ORDER BY coursedemand DESC"
    sorted_by_demand = query_fetch_all_helper(sort_demand_query)
    return sorted_by_demand

def get_dept_demand():
    '''
        Executes a query that fetches information pertaining to the department's demand based on the demand of the courses that belong to the departments.
        
        Returns:
            results: list of departments.
    '''
    avg_by_dept_query = "SELECT s.deptname, AVG(d.coursedemand) FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid GROUP BY s.deptname"
    avg_demand_by_dept = query_fetch_all_helper(avg_by_dept_query)
    return avg_demand_by_dept

def get_dept_count():
    '''
        Executes a query that fetches information pertaining to the number of departments that the targeted courses belong to.
        
        Returns:
            results: list of departments.
    '''
    count_query = "SELECT s.deptname, COUNT(*) FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid GROUP BY s.deptname"
    course_count_by_dept = query_fetch_all_helper(count_query)
    return course_count_by_dept

def get_popular_recs():
    '''
        Executes a query that fetches courses with highest demand.
        
        Returns:
            results: list of courses.
    '''
    high_demand_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid WHERE d.coursedemand > (SELECT AVG(d.coursedemand) FROM courserecs c LEFT JOIN springdemand d)"
    high_demand_courses = query_fetch_all_helper(high_demand_query)
    return high_demand_courses

def get_unpopular_recs():
    '''
        Executes a query that fetches courses with lowest demand.
        
        Returns:
            results: list of courses.
    '''
    low_demand_query = "SELECT c.courseid, s.fullcode, s.title, s.description, d.coursedemand, c.similarity FROM courserecs c LEFT JOIN springcourses s ON c.courseid = s.courseid LEFT JOIN springdemand d ON s.courseid = d.courseid WHERE d.coursedemand < (SELECT AVG(d.coursedemand) FROM courserecs c LEFT JOIN springdemand d)"
    low_demand_courses = query_fetch_all_helper(low_demand_query)
    return low_demand_courses
