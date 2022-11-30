from sklearn.feature_extraction.text import TfidfVectorizer
from sqlite3 import connect
from contextlib import closing
from sklearn.metrics.pairwise import linear_kernel

DB_PATH = 'file:database.sqlite?mode=ro'

def get_course_descriptions():
    
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

    # coursetitle = '%' + coursetitle + '%'
    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT courseid from springcourses WHERE title=?"
            cursor.execute(query_string, [coursetitle])

            row = cursor.fetchone()
            return row[0]

def get_coursetitle(courseid):

    with connect(DB_PATH, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_string = "SELECT title from springcourses WHERE courseid=?"
            cursor.execute(query_string, [courseid])

            row = cursor.fetchone()
            return row[0]

def create_tfidf(course_descriptions):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(course_descriptions)

    return tfidf_matrix

def create_cosine_matrix(tfidf_matrix):
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def get_recommendations(coursetitle, cosine_sim):
    idx = get_courseid(coursetitle)
    sim_scores = list(enumerate(cosine_sim[idx]))
    # print(sim_scores)

    # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores.sort(key=lambda x: x[1], reverse=True)
    print(sim_scores)
    top_scores = sim_scores[0:9]
    print(top_scores)

    top_courses_idx = [i[0] for i in top_scores]
    course_names = []
    for courseid in top_courses_idx:
        course_names.append(get_coursetitle(courseid))

    return course_names

if __name__ == "__main__":
    d = get_course_descriptions()
    m = create_tfidf(d)
    n = create_cosine_matrix(m)

    print(get_recommendations("Algorithms", n))