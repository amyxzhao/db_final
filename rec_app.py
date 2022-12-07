from flask import Flask, request, make_response
from flask import render_template
from get_recommendations import get_course_descriptions, create_tfidf, create_cosine_matrix, get_matching, get_coursetitle, get_recommendations, build_rec_table
from get_recommendations import sort_by_sim, sort_by_demand, get_overall_demand, get_dept_demand, get_dept_count, get_popular_recs, get_unpopular_recs

app = Flask(__name__, template_folder='templates')

# GLOBAL VARIABLES
all_desciptions = get_course_descriptions()
tfidf_matrix = create_tfidf(all_desciptions)
cosine_sim_matrix = create_cosine_matrix(tfidf_matrix)

@app.route('/', methods=['GET'])
def root():
    """Primary page without any table
    """
    html = render_template(
        'index.html',
    )
    response = make_response(html)

    return response

@app.route('/search', methods=['GET'])
def search():

    has_been_submitted = 1

    coursename_input = request.args.get('coursename_input')

    if has_been_submitted:
        matching_courses = get_matching(coursename_input)
        print(matching_courses)

    html = render_template(
        'index.html',
        col_names=['Course ID', 'Course Code', 'Course Title'],
        all_results=matching_courses
    )

    response = make_response(html) 
    return response

@app.route('/recommendations', methods=['GET'])
def recommendations():

    courseid = request.args.get('courseid')
    coursetitle = get_coursetitle(courseid)

    recs = get_recommendations(coursetitle, cosine_sim_matrix)
    build_rec_table(recs)

    results_by_sim = sort_by_sim()
    results_by_dem = sort_by_demand()

    overall_avg = get_overall_demand()
    demand_by_dept = get_dept_demand()

    count_by_dept = get_dept_count()

    pop_courses = get_popular_recs()
    unpop_courses = get_unpopular_recs()

    html = render_template(
        'results.html',
        selected_courseid=courseid,
        selected_coursetitle=coursetitle,
        similarity_sorted=results_by_sim,
        demand_sorted=results_by_dem,
        avg_demand=overall_avg,
        dept_demand=demand_by_dept,
        dept_count=count_by_dept,
        most_demanded=pop_courses, 
        least_demanded=unpop_courses
    )

    response = make_response(html)
    return response