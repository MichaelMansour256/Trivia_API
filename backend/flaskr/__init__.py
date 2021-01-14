import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @TODO(done): Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return "hello"

    '''
  @TODO(done): Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def set_headers(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'ContentType,Authorization, True')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,DELETE,UPDATE,OPTIONS,PUT')
        return response
    '''
  @TODO(done):
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        if not categories:
            abort(404)
        dect = {}
        for c in categories:
            dect[c.id] = c.type
        return jsonify({
            'success': True,
            'categories': dect
        })

    '''
  @TODO(done):
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.
  #page = request.args.get('page', 1, type=int)

  TEST: At this point, when you start the application
  you should see questions and
  categories generated,ten questions per page and
  pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', 1, type=int)
        total_questions = Question.query.count()
        questions_page = Question.query.order_by(
            Question.id).paginate(
            page,
            QUESTIONS_PER_PAGE,
            error_out=False).items
        questions = [question.format() for question in questions_page]
        if len(questions) == 0:
            abort(404)
        categories = Category.query.all()
        dect = {}
        for c in categories:
            dect[c.id] = c.type
        return jsonify({
            'success': True,
            'questions': questions,
            'categories': dect,
            'total_questions': total_questions,
            'current_category': category})
    '''
  @TODO(done):
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question,
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(404)
        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except BaseException:
            abort(422)
    '''
  @TODO(done):
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        if not (question and answer and category and difficulty):
            abort(400)
        try:
            newQuestion = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty)
            newQuestion.insert()
            return jsonify({'success': True, 'created': newQuestion.id})
        except BaseException:
            abort(422)
    '''
  @TODO(done):
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_question():

        try:
            body = request.get_json()
            search_term = body.get('searchTerm')
            print(search_term)
            question_list = Question.query.filter(
                Question.question.like(f'%{search_term}%')).all()
            if len(question_list) == 0:
                raise Exception('no result')
            return jsonify({
                'success': True,
                'questions': [question.format() for question in question_list],
                'total_questions': len(question_list)})
        except BaseException:
            abort(422)
    '''
  @TODO(done):
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_by_category(category_id):

        question_list = Question.query.filter(
            Question.category == category_id).all()
        if len(question_list) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': [question.format() for question in question_list],
                'total_questions': len(question_list),
                'current_category': category_id})

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()

        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(400)
        try:
            category = body.get('quiz_category')['id']
            previous_questions = body.get('previous_questions')
            if category == 0:
                questions_list = Question.query.filter(
                  Question.id.notin_(
                    previous_questions)).all()
            else:
                questions_list = Question.query.filter_by(
                    category=category).filter(
                      Question.id.notin_(
                        previous_questions)).all()
            if len(questions_list) > 0:
                random_question = questions_list[random.randint(
                    0, len(questions_list))].format()
            else:
                random_question = None
            print(random_question)
            return jsonify({
                'success': True,
                'question': random_question
            })
        except BaseException:
            abort(422)

    '''
  @TODO(done):
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
