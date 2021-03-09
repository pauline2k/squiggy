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

from flask import current_app as app, request
from flask_login import current_user, login_required, login_user, logout_user
from squiggy.api.errors import ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.login_session import LoginSession
from squiggy.lib.util import to_int


@app.route('/api/auth/dev_auth_login', methods=['POST'])
def dev_auth_login():
    params = request.get_json() or {}
    if app.config['DEVELOPER_AUTH_ENABLED']:
        user_id = to_int(params.get('userId'))
        password = params.get('password')
        logger = app.logger

        if password != app.config['DEVELOPER_AUTH_PASSWORD']:
            logger.error('Dev auth: Wrong password')
            return tolerant_jsonify({'message': 'Invalid credentials'}, 401)

        login_user(LoginSession(user_id), force=True, remember=True)
        if current_user.is_authenticated:
            return tolerant_jsonify(current_user.to_api_json())
        else:
            return tolerant_jsonify({'message': f'Dev auth: id {user_id} failed to authenticate.'}, 403)
    else:
        raise ResourceNotFoundError('Unknown path')


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return tolerant_jsonify(current_user.to_api_json())
