import tempfile
import unittest
from pathlib import Path
import database
from app import app


class UserAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = database.DATABASE
        database.DATABASE = Path(self.temp.name) / "test.db"
        database.create_db_table()
        self.client = app.test_client()
        self.user = dict(name="John Doe", email="john@example.com", phone="067765434567",
                         address="John Doe Street, Innsbruck", country="Austria")

    def tearDown(self):
        database.DATABASE = self.original
        self.temp.cleanup()

    def test_crud_and_persistence(self):
        self.assertEqual(self.client.get('/api/users').json, [])
        created = self.client.post('/api/users/add', json=self.user)
        self.assertEqual(created.status_code, 201)
        uid = created.json['user_id']
        self.assertEqual(self.client.get(f'/api/users/{uid}').json, created.json)
        self.assertEqual(self.client.get('/api/users').json, [created.json])
        changed = dict(self.user, user_id=uid, name="Jane Doe")
        self.assertEqual(self.client.put('/api/users/update', json=changed).json, changed)
        self.assertEqual(database.get_user_by_id(uid), changed)
        self.assertEqual(self.client.delete(f'/api/users/delete/{uid}').status_code, 200)
        self.assertEqual(self.client.get(f'/api/users/{uid}').status_code, 404)
        self.assertEqual(self.client.get('/api/users').json, [])

    def test_missing_users(self):
        self.assertEqual(self.client.get('/api/users/999').status_code, 404)
        self.assertEqual(self.client.delete('/api/users/delete/999').status_code, 404)
        self.assertEqual(self.client.put('/api/users/update', json=dict(self.user, user_id=999)).status_code, 404)

    def test_invalid_payloads(self):
        for body in [[], {}, dict(self.user, name=" "), dict(self.user, phone=123)]:
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/api/users/add', json=body).status_code, 400)
        for uid in [True, -1, "1", None]:
            self.assertEqual(self.client.put('/api/users/update', json=dict(self.user, user_id=uid)).status_code, 400)
        self.assertEqual(self.client.post('/api/users/add', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/users/add', data='text').status_code, 415)
        self.assertEqual(database.get_users(), [])

    def test_parameterized_sql(self):
        user = dict(self.user, name="Robert'); DROP TABLE users;--")
        self.assertEqual(self.client.post('/api/users/add', json=user).status_code, 201)
        self.assertEqual(database.get_users()[0]['name'], user['name'])

    def test_repeated_initialization(self):
        database.insert_user(self.user)
        database.create_db_table()
        self.assertEqual(len(database.get_users()), 1)

    def test_partial_update_preserves_other_fields(self):
        created = self.client.post('/api/users/add', json=self.user).json
        uid = created['user_id']
        result = self.client.patch(f'/api/users/{uid}', json={'country': 'Lebanon'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, dict(created, country='Lebanon'))
        self.assertEqual(database.get_user_by_id(uid), result.json)

    def test_invalid_patch_does_not_change_record(self):
        created = self.client.post('/api/users/add', json=self.user).json
        uid = created['user_id']
        for body in [{}, [], {'user_id': 5}, {'country': ''}, {'name': 'Changed', 'phone': 123}]:
            with self.subTest(body=body):
                self.assertEqual(self.client.patch(f'/api/users/{uid}', json=body).status_code, 400)
                self.assertEqual(database.get_user_by_id(uid), created)
        self.assertEqual(self.client.patch('/api/users/999', json={'country': 'Lebanon'}).status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
