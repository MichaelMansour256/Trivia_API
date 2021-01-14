import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}/{}".format(
            'postgres', '123456@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test
    for successful operation and for expected errors.
    """

    def test_get_categories(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_categories_404(self):
        result = self.client().get('/categories/123654')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'not found')

    def test_get_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_get_questions_valid_page(self):
        result = self.client().get('/questions?page=2')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_questions_invalid_page(self):
        result = self.client().get('/questions?page=2000')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        result = self.client().delete('/questions/22')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 22)

    def test_delete_question_invalid_404(self):
        result = self.client().delete('/questions/10000')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):
        test_entry = {
            'question': 'who the best player in the world',
            'answer': 'messi',
            'difficulty': 1,
            'category': 6
        }
        result = self.client().post('/questions', json=test_entry)
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_add_question_invalid(self):
        result = self.client().post('/questions', json={})
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['message'], 'bad request')

    def test_get_question_by_category(self):
        result = self.client().get('/categories/1/questions')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_question_by_category_invalid(self):
        result = self.client().get('/categories/100000/questions')
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_search_question(self):
        search_word = {
            'searchTerm': 'what',
        }

        result = self.client().post('/questions/search', json=search_word)
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_question_invalid(self):
        result = self.client().post('/questions/search', json={})
        data = json.loads(result.data)
        print(result)
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity')

    def test_quiz(self):
        test_data = {
            'quiz_category': {
                'type': 'Art',
                'id': 2},
            'previous_questions': []}

        result = self.client().post('/quizzes', json=test_data)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_quiz_invalid(self):
        test_data = {'quiz_category': {'type': 'Art', 'id': 7}}

        result = self.client().post('/quizzes', json=test_data)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")


if __name__ == "__main__":
    unittest.main()
