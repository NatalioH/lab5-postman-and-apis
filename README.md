# Lab 5 Postman and APIs

This project implements the lab's Flask and SQLite user management API and the graded Postman exercise. The collection is named **Flask user app**, covers every required endpoint, includes saved response examples, and uses the environment variable `base_url` for the server URL.

## Run the application

Open this folder in VS Code. In a PowerShell terminal, run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Python 3.10 or later is recommended. SQLite is part of Python; do not install `db-sqlite3`. The app creates an empty `database.db` beside `app.py` automatically. Keep the terminal running while using Postman. Press Ctrl+C to stop it. This is a local teaching app without authentication; use fictional records.

Open http://127.0.0.1:5000/api/users in a browser to view the user list. Initially it is `[]`. After adding a user, open `/api/users/1` if the returned user ID is 1, or substitute the returned ID.

## Complete the Postman workflow

1. Create a workspace in Postman if you do not already have one.
2. Use Import to import `Flask user app.postman_collection.json` and `Flask local.postman_environment.json`.
3. Select the **Flask local** environment. Its `base_url` value is `http://127.0.0.1:5000` with no trailing slash.
4. Run the collection in numbered order, or send each request in that order. The first request creates a fictional user and stores its ID in the `user_id` environment variable. Later requests use that ID. Keep every request selected when running the collection.
5. Inspect the response body, status, and test results. Each request already contains a saved example captured from a live local HTTP run. To save your own result, send the request and choose **Save response as example** (the label may vary by version).
6. The final request intentionally returns **404** to confirm deletion; its test should pass. Running the complete collection again creates and deletes a new record.

For the web version of Postman, use the Desktop Agent for the local API, or use the Postman desktop app.

## Required endpoints

| Operation | Method | URL | Success |
| --- | --- | --- | --- |
| List users | GET | `{{base_url}}/api/users` | 200 and an array |
| Read one user | GET | `{{base_url}}/api/users/{{user_id}}` | 200 and a user |
| Create user | POST | `{{base_url}}/api/users/add` | 201 and the created user |
| Update user | PUT | `{{base_url}}/api/users/update` | 200 and the updated user |
| Delete user | DELETE | `{{base_url}}/api/users/delete/{{user_id}}` | 200 and a status message |

POST and PUT use **Body → raw → JSON**. Example POST body:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "067765434567",
  "address": "John Doe Street, Innsbruck",
  "country": "Austria"
}
```

PUT includes all five fields plus a numeric `user_id`. The collection provides this automatically. Phone numbers are strings so leading zeroes are preserved. Required text fields must be nonempty strings. Invalid data returns 400; missing or incorrect JSON content type returns 415; nonexistent users return 404.

## How the code works

`database.py` opens SQLite connections, creates the users table, and implements the five database functions. Parameterized SQL keeps user input separate from SQL syntax. Transactions commit successful changes, roll back failures, and close connections. The database path is relative to the project file, so changing the terminal directory does not create another database accidentally.

`app.py` maps the lab's routes to these functions. It validates request bodies and returns JSON with explicit HTTP status codes. CORS is enabled for the lab's API routes; CORS controls browser access and is not authentication or a firewall.

The supplied handout's broken multiline strings, indentation, `conn().rollback()` typo, and missing connection cleanup have been corrected. Table creation can safely run more than once.

## Validation

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

Five tests passed during preparation: complete CRUD with database persistence, missing users, invalid inputs, SQL-like text stored safely, and repeated table initialization. Seven additional live HTTP requests passed, covering create, list, read, update, read after update, delete, and read after deletion. Their actual response bodies are embedded in the collection examples. Test records used a temporary database; the supplied database is empty.

The Postman files were generated for import. The Postman desktop interface itself was not operated, and no workspace or GitHub repository was created online.

## Git and GitHub

The delivered folder includes a local Git repository with a database commit on `main`, an `api-implementation` branch containing the API and Postman files, and a merge back into `main`. Inspect it with:

```powershell
git log --oneline --graph --all
```

To complete the online part, create an empty GitHub repository in your account, then run these commands using its actual URL:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
git push -u origin api-implementation
```

The remote URL above is a placeholder. No pull was performed because no remote was supplied. The local branch starts from the database commit, which provides the same starting code. The database and virtual environment are ignored by Git. A portable `Lab5-history.bundle` is included beside this project; if extraction loses the hidden `.git` folder, restore the history with `git clone Lab5-history.bundle Lab5-restored`.

## References

- Lab handout: `Lab5-Postman and APIs.docx`.
- Postman quick start: https://learning.postman.com/docs/getting-started/quick-start/
- Sending requests: https://learning.postman.com/docs/use/send-requests/requests/
- Flask testing: https://flask.palletsprojects.com/en/stable/testing/
