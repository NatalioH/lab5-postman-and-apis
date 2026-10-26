# Lab 7 - Python Testing

**Natalio Hassoun**
Software Tools Lab - Fall 2026-2027

Pytest tests for the Flask and SQLite user-management project from Lab 5.

## Set up and test

Requires Python 3.10 or newer. In PowerShell, open this project directory and run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
```

To run only the Lab 7 tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v test_user_Natalio_Hassoun.py
```

The full suite contains **32 tests**: 25 Lab 7 test cases and 7 existing Lab 5 tests.
The existing unittest subtests are also checked by pytest.

## Graded requirements

| Requirement | Main test in `test_user_Natalio_Hassoun.py` |
| --- | --- |
| Database and initial users on the first app run | `test_database_created_with_initial_users_on_first_app_run` |
| `insert_user()` | `test_insert_user` |
| `get_users()` | `test_get_users_returns_all_users_in_id_order` |
| Get user by ID | `test_get_users_by_id` |
| `update_user()` | `test_update_user` |
| `delete_user()` | `test_delete_user_removes_only_requested_record` |
| `api_get_user()` | `test_api_get_user` |
| `api_add_user()` | `test_api_add_user` |
| `api_update_user()` | `test_api_update_user` |
| `api_delete_user()` | `test_api_delete_user` |

The project calls its lookup function `get_user_by_id()`; this is the function
listed as `Get_users_by_id()` in the Lab 7 handout.

All API tests check HTTP status and JSON response data. POST and PUT tests also
verify persisted fields and retrieve the saved user through GET. DELETE tests
check the response message, absence of the deleted user, and preservation of other
users. Additional tests cover missing IDs, invalid payloads, and restart behavior.

## Fixtures and first-run behavior

Each Lab 7 test uses a separate temporary SQLite file through `tmp_path` and
`monkeypatch`. The `client`, `user_data`, and `saved_user` fixtures provide the Flask
test client and reusable test data. No running web server is needed for the tests.

The original Lab 5 app created an empty table. For the Lab 7 first-run requirement,
the app now inserts the John Doe sample already documented in the Lab 5 project:

```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "067765434567",
  "address": "John Doe Street, Innsbruck",
  "country": "Austria"
}
```

The Lab 7 handout does not name a different set of initial users. This sample is
defined in `database.INITIAL_USERS`. Startup seeds it only when creating the users
table, so restarting neither duplicates users nor restores intentionally deleted
records. The first-run test launches the actual app import in a separate Python
process with a nonexistent database, then verifies the schema and exact user data.

Generated databases are excluded from the submission so a clean copy exercises
first-run creation. If using an existing Lab 5 database, startup preserves it.
The `LAB5_DATABASE` environment variable can select a different database file.

## Run the app

```powershell
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/api/users`. The app creates `database.db` beside its code.

| Operation | Method | Endpoint | Success status |
| --- | --- | --- | --- |
| Get all users | GET | `/api/users` | 200 |
| Get one user | GET | `/api/users/<user_id>` | 200 |
| Add a user | POST | `/api/users/add` | 201 |
| Update a user | PUT | `/api/users/update` | 200 |
| Delete a user | DELETE | `/api/users/delete/<user_id>` | 200 |
| Partial update from Lab 5 | PATCH | `/api/users/<user_id>` | 200 |

POST accepts the five user fields; PUT also requires `user_id`. Invalid fields
return 400; a missing user returns 404. These are the existing Lab 5 API behaviors.

## Files and evidence

- `app.py`, `database.py`: application and SQLite functions.
- `test_user_Natalio_Hassoun.py`: required Lab 7 pytest submission.
- `test_app.py`: original Lab 5 regression tests.
- `requirements.txt`, `pytest.ini`: dependencies and test discovery settings.
- `evidence/`: successful pytest output, XML results, browser report, and snapshot.
- `README-Lab5.md`, Postman JSON files, `screenshots/`: retained Lab 5 materials.

For Moodle, upload **Lab7-Natalio-Hassoun.zip** and the separate
**Lab7-Natalio-Hassoun-tests-passed.png** snapshot. The ZIP also includes the evidence.

The Lab 5 repository is `https://github.com/NatalioH/lab5-postman-and-apis`;
Lab 7 changes are on the `lab7-python-testing` branch.
