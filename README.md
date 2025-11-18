# LuminAcademy

A lightweight online course API built with Django and Django REST Framework.
This repository provides user registration/login (JWT), course/module/lesson management, and enrollment tracking with role-based permissions for students, instructors and admins.

**Repository layout (important files)**
- `manage.py` — Django management entry
- `luminacademy/` — project settings and URLs
- `api/` — DRF viewsets, serializers, permissions, URLs
- `accounts/` — custom user model (`CustomUser`), profile model, signals and manager
- `courses/` — course/module/lesson/enrollment models and business logic
- `requirements.txt` — Python dependencies
- `db.sqlite3` — (dev) SQLite database file

**Quick start (Windows / PowerShell)**
1. Activate the virtualenv shipped in the repo (if present):

```powershell
cd C:\Users\User\Desktop\Drf_code\luminacademy
.\luminacademy-env\Scripts\Activate
```

2. Install dependencies (if you need to):

```powershell
pip install -r requirements.txt
```

3. Apply migrations and create a superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. (Optional) Create missing user profiles if you see `RelatedObjectDoesNotExist` for `profile`:

```powershell
python manage.py create_missing_profiles
```

5. Run the dev server:

```powershell
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` (or the API root at `/api/`) to explore the API. The project commonly mounts the API at `/api/v1/`.

Authentication
- JWT-based login is available: POST `/api/v1/token/login/` with `{"email":..., "password":...}` returns an access token.
- Use the header `Authorization: Bearer <ACCESS_TOKEN>` for authenticated requests.

Key models & behaviors
- `CustomUser` (in `accounts.models`) has `role` (student/instructor/admin). The `save()` override sets `is_staff=True` for instructors and admins so they can access the Django admin if needed.
- `UserProfile` is a one-to-one model attached to `CustomUser` via `profile`. Signals are registered (in `accounts.signals`) to automatically create a profile when a user is created.
- `Course` auto-generates a unique `slug` from the `title` on save (see `courses.models.Course.save()`).
- `Enrollment` tracks `student`, `course`, `progress` (Decimal), and `completed` (Boolean). Unique constraint prevents duplicate `(student, course)`.

API endpoints (high level)
- Auth & registration:
  - `POST /dj-rest-auth/registration/` — register a new user (use this for public signups)
  - `POST /dj-rest-auth/login/` — obtain JWT access/refresh
  - `POST /dj-rest-auth/token/refresh/` — refresh JWT

- Users:
  - `GET /api/v1/users/` — list users (permissions apply)
  - `POST /api/v1/users/` — create user (admin only by default)
  - `GET /api/v1/users/{id}/` — retrieve
  - `PUT/PATCH /api/v1/users/{id}/` — update (admin or the user themself)
  - `GET /api/v1/users/roles/?role=instructor` — convenience action to list users by role; no `role` returns grouped lists by role

- Courses / Modules / Lessons:
  - Standard ModelViewSet endpoints under `/api/v1/courses/`, `/api/v1/modules/`, `/api/v1/lessons/`.
  - Instructors create courses/modules/lessons; safe methods available to others depending on permission classes.

- Enrollments:
  - `GET /api/v1/enrollments/` — list enrollments visible to the authenticated user (students see their own; instructors/admins may see more depending on permissions)
  - `POST /api/v1/enrollments/` — create enrollment:
    - Students may create an enrollment for themselves by providing `{"course": <id>}`.
    - Instructors and admins may create enrollments on behalf of a student by specifying `{"course": <id>, "student": <student_id>}`.
  - `POST /api/v1/enrollments/{pk}/update_progress/` — update an enrollment's progress. Accepts numeric progress (0–100). The endpoint coerces values to Decimal and validates range.
  - `GET /api/v1/enrollments/my_enrollments/` — convenience view: students get their enrollments; instructors get enrollments for their courses; admins get all enrollments.

Permissions summary
- `api/permissions.py` provides granular classes:
  - `IsAdminOrSelf` — used for users: admins manage all users, users can view/update themselves.
  - `IsStudentOrInstructorOrAdmin` — view-level check allowing students/instructors/admins where appropriate.
  - `IsEnrollmentOwnerOrCourseInstructorOrAdmin` — object-level permission for enrollments (owner student, course instructor, or admin may perform unsafe actions).

Developer notes & tips
- Slug generation: the `Course.save()` method generates unique slugs only when `slug` is blank. If you want slugs to update when `title` changes, update the logic accordingly.
- Profiles: Signals auto-create profiles for newly created users. If you import or create users outside normal flows, run `python manage.py create_missing_profiles`.
- Admin site: instructors and admins are automatically marked `is_staff=True` by the `CustomUser.save()` override; superusers created via the manager still get `is_superuser=True` and `is_staff=True`.
- Tests: add and run tests using `python manage.py test`.

Common commands
```powershell
# apply migrations
python manage.py migrate

# create superuser
python manage.py createsuperuser

# run development server
python manage.py runserver

# create missing user profiles
python manage.py create_missing_profiles

# run tests
python manage.py test
```

Contributing
- Fork and submit PRs.
- Keep changes minimal and add tests for new behaviors.

License
- This project does not include a license file in the repo. Add a LICENSE if you plan to open-source it.

Contact
- For questions about this project, open an issue in the repository.
