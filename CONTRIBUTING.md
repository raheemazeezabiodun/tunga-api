# Contributing
These are the general guidelines to follow when contributing to Tunga API development.

* Follow the [readme](https://github.com/tunga-io/tunga-api/blob/master/readme.md) for instructions on setting up your development environment.
* Follow industry best practices for [Python](https://www.python.org/) and [Django](https://www.djangoproject.com/) for issues not addressed in this document.

## Sending a Pull Request

In general, the contribution workflow looks like this:

* Choose an open issue from the [Issue tracker](https://github.com/tunga-io/tunga-api/issues).
* Fork the repo.
* Create a new feature branch based off the `develop` branch.
* Make sure all tests pass and there are no linting errors.
* Submit a pull request, referencing any issues it addresses.

Please try to keep your pull request focused in scope and avoid including unrelated commits.

After you have submitted your pull request, we'll try to get back to you as soon as possible. We may suggest some changes or improvements.

## Coding Guide
Tunga API is built on a core of [Python](https://www.python.org/), [Django](https://www.djangoproject.com/) and [Django REST framework](http://www.django-rest-framework.org/)

Follow the following coding guidelines when contributing:

* For security, keep sensitive data (e.g passwords, API keys and OAuth secrets) out of the repo.
* Follow the style guide defined in [.editorconfig](https://github.com/tunga-io/tunga-web/blob/master/.editorconfig)
* Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python styling unless otherwise stated.
* Follow Django conventions, best practices and style guides like keeping your code DRY, loosely coupled, modular and readable e.t.c. 

Use the resources below to get yourself up to speed if necessary.
https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/#model-style
https://streamhacker.com/2011/01/03/django-application-conventions/
http://django-best-practices.readthedocs.io/en/latest/applications.html

* Use [Django REST framework](http://www.django-rest-framework.org/) to define all endpoints and serializers instead of using normal Django views unless otherwise stated.
* Use [DRY Rest Permissions](https://github.com/dbkaplan/dry-rest-permissions) to define global and object permissions for actions.
* Use [Django Activity Stream](https://github.com/justquick/django-activity-stream) for generating activity streams for user actions.
* Use [django-rq](https://github.com/rq/django-rq) to create and manage long running background tasks.
* Use [Advanced Python Scheduler](https://apscheduler.readthedocs.io/en/latest/) to schedule tasks that execute periodically, see the [tunga_scheduler](https://github.com/tunga-io/tunga-api/blob/master/tunga_utils/management/commands/tunga_scheduler.py) command for details.
* Use [Django REST Swagger](https://github.com/marcgibbons/django-rest-swagger) to generate API docs.

* The code base is loosely divided in appropriately named apps that manage specific entities and activites

`tunga_auth` - manages simple user authentication

`tunga_profiles` - manages user data that is not required for authentication

`tunga_comments` - manages generic message carriers used on the platform by tasks

`tunga_messages` - manages user to user messaging

`tunga_pages` - manages custom pages like skill pages and blog posts

`tunga_settings` - manages user settings

`tunga_support` - manages user facing support documentation

`tunga_tasks` - manages tasks/projects and related actions like task applications, task invitations and payments

`tunga_utils` - manages generic entities that may be used by other apps to create a clearer dependency hierarchy

* To override settings in `tunga/settings.py`, create a file `tunga/env/local.py` and keep it out of Git.
* Use Django management commands to trigger one-time or scheduled tasks tasks that happen outside the request-response cycle.
* Use built-in and custom signals to trigger responses to specific actions while keeping the codebase decoupled and the request-response cycle as minimalist as possible. 
* Define generic methods for notifications which then call methods for specific providers like Email and Slack.

Thank you for contributing!
