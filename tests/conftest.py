"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from datetime import datetime
import json
import os

from squiggy import std_commit
from squiggy.models.asset import Asset
from squiggy.models.category import Category
from squiggy.models.course import Course
from squiggy.models.user import User

os.environ['SQUIGGY_ENV'] = 'test'  # noqa

from moto import mock_sts  # noqa
import pytest  # noqa
import squiggy.factory  # noqa
from tests.util import override_config  # noqa


class FakeAuth(object):
    def __init__(self, the_app, the_client):
        self.app = the_app
        self.client = the_client

    def login(
            self,
            user_id,
    ):
        with override_config(self.app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {
                'userId': user_id,
                'password': self.app.config['DEVELOPER_AUTH_PASSWORD'],
            }
            self.client.post(
                '/api/auth/dev_auth_login',
                data=json.dumps(params),
                content_type='application/json',
            )


# Because app and db fixtures are only created once per pytest run, individual tests
# are not able to modify application configuration values before the app is created.
# Per-test customizations could be supported via a fixture scope of 'function' and
# the @pytest.mark.parametrize annotation.

@pytest.fixture(scope='session')
def app(request):
    """Fixture application object, shared by all tests."""
    _app = squiggy.factory.create_app()

    # Create app context before running tests.
    ctx = _app.app_context()
    ctx.push()

    # Pop the context after running tests.
    def teardown():
        ctx.pop()
    request.addfinalizer(teardown)

    return _app


# TODO Perform DB schema creation and deletion outside an app context, enabling test-specific app configurations.
@pytest.fixture(scope='session')
def db(app):
    """Fixture database object, shared by all tests."""
    from squiggy.models import development_db
    # Drop all tables before re-loading the schemas.
    # If we dropped at teardown instead, an interrupted test run would block the next test run.
    development_db.clear()
    _db = development_db.load()

    return _db


@pytest.fixture(scope='function', autouse=True)
def db_session(db):
    """Fixture database session used for the scope of a single test.

    All executions are wrapped in a session and then rolled back to keep individual tests isolated.
    """
    # Mixing SQL-using test fixtures with SQL-using decorators seems to cause timing issues with pytest's
    # fixture finalizers. Instead of using a finalizer to roll back the session and close connections,
    # we begin by cleaning up any previous invocations.
    # This fixture is marked 'autouse' to ensure that cleanup happens at the start of every test, whether
    # or not it has an explicit database dependency.
    db.session.rollback()
    try:
        db.session.get_bind().close()
    # The session bind will close only if it was provided a specific connection via this fixture.
    except AttributeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)
    db.session = _session

    return _session


@pytest.fixture(scope='function')
def authorized_user_id():
    return User.query.first().id


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """Shortcut to start an authenticated session."""
    return FakeAuth(app, client)


@pytest.fixture(scope='session', autouse=True)
def fake_sts(app):
    """Fake the AWS security token service used to deliver S3 content (photos, note attachments)."""
    mock_sts().start()
    yield
    mock_sts().stop()


@pytest.fixture(scope='function')
def mock_asset(db):
    category = mock_category(db)
    course = Course.query.order_by(Course.name).all()[0]
    unique_token = datetime.now().isoformat()
    asset = Asset.create(
        asset_type='link',
        categories=[category],
        course_id=course.id,
        description=None,
        title=f'Mock Asset created at {unique_token}',
        url=f'https://en.wikipedia.org/wiki/{unique_token}',
    )
    std_commit(allow_test_environment=True)
    return asset


@pytest.fixture(scope='function')
def mock_category(db):
    return Category.create(
        canvas_assignment_name='Linger on your pale blue eyes',
        course_id=1,
        title='Thought of you as my mountain top',
        canvas_assignment_id=98765,
        visible=True,
    )
