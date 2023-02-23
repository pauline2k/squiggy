"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from flask import current_app as app
import pytz
from sqlalchemy import and_, func
from sqlalchemy.dialects.postgresql import ENUM, JSON
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text
from squiggy import db, std_commit
from squiggy.lib.util import isoformat, utc_now
from squiggy.models.activity_type import activities_type, ActivityType
from squiggy.models.base import Base
from squiggy.models.course import Course
from squiggy.models.user import User


activities_object_type = ENUM(
    'asset',
    'canvas_discussion',
    'canvas_submission',
    'comment',
    'whiteboard',
    name='enum_activities_object_type',
    create_type=False,
)


class Activity(Base):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    activity_type = db.Column('type', activities_type, nullable=False)
    object_id = db.Column(db.Integer)
    object_type = db.Column('object_type', activities_object_type, nullable=False)
    activity_metadata = db.Column('metadata', JSON)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    course_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reciprocal_id = db.Column(db.Integer)

    user = db.relationship('User', primaryjoin='Activity.user_id==User.id')
    actor = db.relationship('User', primaryjoin='Activity.actor_id==User.id')
    asset = db.relationship('Asset')
    comment = db.relationship(
        'Comment',
        primaryjoin='and_(foreign(Activity.object_id)==remote(Comment.id), Activity.object_type==\'comment\')',
    )

    def __init__(
        self,
        activity_type,
        course_id,
        user_id,
        object_type,
        object_id=None,
        asset_id=None,
        actor_id=None,
        reciprocal_id=None,
        activity_metadata=None,
    ):
        self.activity_type = activity_type
        self.course_id = course_id
        self.user_id = user_id
        self.object_type = object_type
        self.object_id = object_id
        self.asset_id = asset_id
        self.actor_id = actor_id
        self.reciprocal_id = reciprocal_id
        self.activity_metadata = activity_metadata

    def __repr__(self):
        return f"""<Activity
                    id={self.id},
                    type={self.activity_type},
                    course_id={self.course_id},
                    user_id={self.user_id},
                    object_type={self.object_type}
                    object_id={self.object_id}
                    asset_id={self.asset_id}
                    actor_id={self.actor_id}
                    reciprocal_id={self.reciprocal_id}
                    metadata={self.activity_metadata}>
                """

    @classmethod
    def create(
        cls,
        activity_type,
        course_id,
        user_id,
        object_type,
        object_id=None,
        asset_id=None,
        actor_id=None,
        reciprocal_id=None,
        activity_metadata=None,
    ):
        activity = cls(
            activity_type=activity_type,
            course_id=course_id,
            user_id=user_id,
            object_type=object_type,
            object_id=object_id,
            asset_id=asset_id,
            actor_id=actor_id,
            reciprocal_id=reciprocal_id,
            activity_metadata=activity_metadata,
        )
        db.session.add(activity)
        user = User.find_by_id(user_id)
        if user:
            user.last_activity = utc_now()
            db.session.add(user)
        cls.recalculate_points(course_id=course_id, user_ids=[user_id])
        std_commit()
        return activity

    @classmethod
    def create_unless_exists(cls, **kwargs):
        if cls.query.filter_by(**kwargs).count() == 0:
            return cls.create(**kwargs)

    @classmethod
    def delete_by_object_id(cls, object_type, object_id, course_id, user_ids):
        cls.query.filter(and_(cls.object_type == object_type, cls.object_id == object_id)).delete()
        cls.recalculate_points(course_id=course_id, user_ids=user_ids)

    @classmethod
    def find_by_object_id(cls, object_type, object_id):
        return cls.query.filter(and_(cls.object_type == object_type, cls.object_id == object_id)).all()

    @classmethod
    def get_activities_as_csv(cls, course_id):
        configuration = ActivityType.get_activity_type_configuration(course_id=course_id)
        configuration_by_type = {c['type']: c for c in configuration}
        course = Course.find_by_id(course_id)
        rows = []
        total_scores = {}
        headers = ('course_sections', 'user_id', 'user_name', 'action', 'date', 'score', 'running_total') if course.protects_assets_per_section \
            else ('user_id', 'user_name', 'action', 'date', 'score', 'running_total')
        results = cls.query.filter_by(course_id=course_id).order_by(cls.created_at).options(joinedload(cls.user)).all()

        for activity in results:
            if configuration_by_type.get(activity.activity_type, {}).get('enabled', None):
                score = configuration_by_type[activity.activity_type]['points']
                total_scores[activity.user_id] = total_scores.get(activity.user_id, 0) + score
                row = {'course_sections': ', '.join(activity.user.canvas_course_sections or [])} if course.protects_assets_per_section else {}
                row.update({
                    'user_id': activity.user_id,
                    'user_name': activity.user.canvas_full_name,
                    'action': activity.activity_type,
                    'date': activity.created_at.astimezone(pytz.timezone(app.config['TIMEZONE'])),
                    'score': score,
                    'running_total': total_scores[activity.user_id],
                })
                rows.append(row)
        return headers, rows

    @classmethod
    def get_activities_for_user_id(cls, user_id, sections=None):
        params = {'user_id': user_id}
        query = """
            SELECT
                a.type AS activity_type,
                a.created_at,
                a.id AS activity_id,
                a.object_id,
                a.object_type,
                a.asset_id,
                a.course_id,
                a.user_id,
                a.actor_id,
                u.canvas_full_name AS user_name,
                u.canvas_image AS user_image,
                u.canvas_course_sections AS user_sections,
                actor.canvas_full_name AS actor_name,
                actor.canvas_image AS actor_image,
                actor.canvas_course_sections AS actor_sections,
                assets.title AS asset_title,
                assets.thumbnail_url AS asset_thumbnail_url,
                c.id AS comment_id,
                c.body AS comment_body
            FROM activities a
            JOIN users u ON a.user_id = u.id
            LEFT JOIN users actor ON a.actor_id = actor.id
            LEFT JOIN assets ON assets.id = a.asset_id
            LEFT JOIN comments c ON c.id = a.object_id AND a.object_type = 'comment'
            WHERE a.user_id = :user_id
                AND assets.deleted_at IS NULL"""
        if sections:
            params['user_course_sections'] = sections
            query += """
                AND (
                    to_jsonb(actor.canvas_course_sections) ?| :user_course_sections
                    OR a.actor_id IS NULL
                )
                AND to_jsonb(u.canvas_course_sections) ?| :user_course_sections"""
        activities = db.session.execute(text(query), params)
        return _to_api_json_by_type(activities)

    @classmethod
    def get_last_activity_for_course(cls, course_id):
        # Rather than querying activities directly, perform a more lightweight query against the last_activity attribute
        # for course users.
        return db.session.query(func.max(User.last_activity)).filter_by(course_id=course_id).scalar()

    @classmethod
    def get_interactions_for_course(cls, course_id, sections=None):
        params = {'course_id': course_id}
        interactions_where_clause = """WHERE a.course_id = :course_id
            AND a.reciprocal_id IS NOT NULL
            AND assets.deleted_at IS NULL"""
        whiteboards_where_clause = """WHERE a.course_id = :course_id
            AND a.type = 'whiteboard'"""
        if sections:
            params['user_course_sections'] = sections
            interactions_where_clause += """
            AND to_jsonb(act.canvas_course_sections) ?| :user_course_sections
            AND to_jsonb(u.canvas_course_sections) ?| :user_course_sections"""
            whiteboards_where_clause += """
            AND to_jsonb(u1.canvas_course_sections) ?| :user_course_sections
            AND to_jsonb(u2.canvas_course_sections) ?| :user_course_sections"""

        interactions_query = text(f"""
        SELECT a.type AS type, a.actor_id as source, a.user_id as target, COUNT(a.type)::int AS count
        FROM activities a
            LEFT JOIN assets ON a.asset_id = assets.id
            JOIN users AS u ON
                (a.user_id = u.id AND u.canvas_course_role IN ('Learner', 'Student') AND u.canvas_enrollment_state != 'inactive')
            JOIN users AS act ON
                (a.actor_id = act.id AND act.canvas_course_role IN ('Learner', 'Student') AND act.canvas_enrollment_state != 'inactive')
        {interactions_where_clause}
        GROUP BY a.type, a.user_id, a.actor_id""")

        # Co-creation of whiteboards is a special "activity" type, not captured in the activities table but extractable
        # from the assets table.
        whiteboard_co_creation_query = text(f"""
        SELECT 'co_create_whiteboard' AS type, au1.user_id AS source, au2.user_id AS target, count(*)::int AS count
        FROM assets a
            JOIN (
                asset_users au1 JOIN users u1 ON au1.user_id = u1.id
                AND u1.canvas_course_role IN ('Learner', 'Student') AND u1.canvas_enrollment_state != 'inactive'
            ) ON a.id = au1.asset_id
            JOIN (
                asset_users au2 JOIN users u2 ON au2.user_id = u2.id
                AND u2.canvas_course_role IN ('Learner', 'Student') AND u2.canvas_enrollment_state != 'inactive'
            ) ON a.id = au2.asset_id AND au1.user_id < au2.user_id
        {whiteboards_where_clause}
        GROUP BY au1.user_id, au2.user_id""")
        return list(db.session.execute(interactions_query, params)) + list(db.session.execute(whiteboard_co_creation_query, params))

    @classmethod
    def recalculate_points(cls, course_id=None, user_ids=None):
        if not course_id and not user_ids:
            return
        user_query = User.query
        if course_id:
            user_query = user_query.filter_by(course_id=course_id)
        if user_ids:
            user_query = user_query.filter(User.id.in_(user_ids))
        users = user_query.all()
        if not users:
            return
        if not course_id:
            course_id = users[0].course_id

        configuration = ActivityType.get_activity_type_configuration(course_id=course_id)
        configuration_by_type = {c['type']: c for c in configuration}
        total_scores = {}

        activity_query = cls.query.filter_by(course_id=course_id)
        if user_ids:
            activity_query = activity_query.filter(cls.user_id.in_(user_ids))
        for activity in activity_query.all():
            if configuration_by_type.get(activity.activity_type, {}).get('enabled', None):
                score = configuration_by_type[activity.activity_type]['points']
                total_scores[activity.user_id] = total_scores.get(activity.user_id, 0) + score
        for user in users:
            if user.id in total_scores:
                user.points = total_scores[user.id]
            else:
                user.points = 0
            db.session.add(user)
        std_commit()

    def to_api_json(self):
        return {
            'id': self.id,
            'activityType': self.activity_type,
            'courseId': self.course_id,
            'userId': self.user_id,
            'objectType': self.object_type,
            'objectId': self.object_id,
            'assetId': self.asset_id,
            'actorId': self.actor_id,
            'reciprocalId': self.reciprocal_id,
            'metadata': self.activity_metadata,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }


def _to_api_json_by_type(activities):
    activities_by_type = {
        'actions': {
            'engagements': [],
            'interactions': [],
            'creations': [],
        },
        'impacts': {
            'engagements': [],
            'interactions': [],
            'creations': [],
        },
    }
    for activity in activities:
        activity_json = {
            'id': activity['activity_id'],
            'type': activity['activity_type'],
            'date': isoformat(activity['created_at']),
            'user': {},
        }

        if activity['asset_id']:
            activity_json['asset'] = {
                'id': activity['asset_id'],
                'title': activity['asset_title'],
                'thumbnailUrl': activity['asset_thumbnail_url'],
            }
        if activity['comment_id']:
            activity_json['comment'] = {
                'id': activity['comment_id'],
                'body': activity['comment_body'],
            }
        if activity['actor_id']:
            activity_json['actorId'] = activity['actor_id']
            activity_json['user']['id'] = activity['actor_id']
            activity_json['user']['name'] = activity['actor_name']
            activity_json['user']['image'] = activity['actor_image']
            activity_json['user']['sections'] = activity['actor_sections']
        else:
            activity_json['user']['id'] = activity['user_id']
            activity_json['user']['name'] = activity['user_name']
            activity_json['user']['image'] = activity['user_image']
            activity_json['user']['sections'] = activity['user_sections']

        if activity['activity_type'] in {'asset_like', 'asset_view'}:
            activities_by_type['actions']['engagements'].append(activity_json)
        elif activity['activity_type'] in {'asset_comment', 'discussion_entry', 'discussion_topic'}:
            activities_by_type['actions']['interactions'].append(activity_json)
        elif activity['activity_type'] in {'asset_add', 'whiteboard_add_asset', 'whiteboard_export', 'whiteboard_remix'}:
            activities_by_type['actions']['creations'].append(activity_json)
        elif activity['activity_type'] in {'get_asset_view', 'get_asset_like'}:
            activities_by_type['impacts']['engagements'].append(activity_json)
        elif activity['activity_type'] in {'get_asset_comment', 'get_asset_comment_reply', 'get_discussion_entry_reply'}:
            activities_by_type['impacts']['interactions'].append(activity_json)
        elif activity['activity_type'] in {'get_whiteboard_add_asset', 'get_whiteboard_remix'}:
            activities_by_type['impacts']['creations'].append(activity_json)
    return activities_by_type
