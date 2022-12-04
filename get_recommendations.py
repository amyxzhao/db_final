from contextlib import closing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlite3 import connect


DB_PATH = 'file:database.sqlite?mode=ro'

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
            row[0] + ': ' + row[1]: A formatted string of the course subject code and title. 
    
    '''

    # TODO: Address the crosslisting issue!

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT fullcode, title from springcourses WHERE courseid=?"
            cursor.execute(query_string, [courseid])

            row = cursor.fetchone()
            return row[0] + ': ' + row[1]

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
            course_names: List of strings that represent the most similar courses to the one provided. 
    '''

    # TODO: Address the crosslisting issue!
    idx = get_courseid(coursetitle)
    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores.sort(key=lambda x: x[1], reverse=True)

    top_scores = sim_scores[1:10]

    top_courses_idx = [i[0] for i in top_scores]
    course_names = []
    for courseid in top_courses_idx:
        course_names.append(get_coursetitle(courseid))

    return course_names

if __name__ == "__main__":

    # A proof of concept. 
    d = get_course_descriptions()
    m = create_tfidf(d)
    n = create_cosine_matrix(m)

    print(get_recommendations("Compilers and Interpreters", n))