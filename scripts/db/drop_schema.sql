/**
 * Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--

ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_actor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_course_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_reciprocal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.activity_types DROP CONSTRAINT IF EXISTS activity_types_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.asset_categories DROP CONSTRAINT IF EXISTS asset_categories_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asset_categories DROP CONSTRAINT IF EXISTS asset_categories_category_id_fkey;

ALTER TABLE IF EXISTS ONLY public.asset_users DROP CONSTRAINT IF EXISTS asset_users_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asset_users DROP CONSTRAINT IF EXISTS asset_users_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.asset_whiteboard_elements DROP CONSTRAINT IF EXISTS asset_whiteboard_elements_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asset_whiteboard_elements DROP CONSTRAINT IF EXISTS asset_whiteboard_elements_element_asset_id_fkey;

ALTER TABLE IF EXISTS ONLY public.assets DROP CONSTRAINT IF EXISTS assets_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.course_group_memberships DROP CONSTRAINT IF EXISTS course_group_memberships_course_id_fkey;
ALTER TABLE IF EXISTS ONLY public.course_group_memberships DROP CONSTRAINT IF EXISTS course_group_memberships_course_group_id_fkey;

ALTER TABLE IF EXISTS ONLY public.course_groups DROP CONSTRAINT IF EXISTS course_groups_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.courses DROP CONSTRAINT IF EXISTS courses_canvas_api_domain_fkey;

ALTER TABLE IF EXISTS ONLY public.canvas_poller_api_keys
  DROP CONSTRAINT IF EXISTS canvas_poller_api_keys_canvas_api_domain_fkey;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.whiteboard_elements DROP CONSTRAINT IF EXISTS whiteboard_elements_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.whiteboard_elements DROP CONSTRAINT IF EXISTS whiteboard_elements_whiteboard_id_fkey;

ALTER TABLE IF EXISTS ONLY public.whiteboard_sessions DROP CONSTRAINT IF EXISTS whiteboard_sessions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.whiteboard_sessions DROP CONSTRAINT IF EXISTS whiteboard_sessions_whiteboard_id_fkey;

ALTER TABLE IF EXISTS ONLY public.whiteboard_users DROP CONSTRAINT IF EXISTS whiteboard_users_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.whiteboard_users DROP CONSTRAINT IF EXISTS whiteboard_users_whiteboard_id_fkey;

ALTER TABLE IF EXISTS ONLY public.whiteboards DROP CONSTRAINT IF EXISTS whiteboards_course_id_fkey;

--

ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_pkey;
ALTER TABLE IF EXISTS public.activities ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.activity_types DROP CONSTRAINT IF EXISTS activity_types_pkey;
ALTER TABLE IF EXISTS public.activity_types ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.asset_categories DROP CONSTRAINT IF EXISTS asset_categories_pkey;

ALTER TABLE IF EXISTS ONLY public.asset_users DROP CONSTRAINT IF EXISTS asset_users_pkey;

ALTER TABLE IF EXISTS ONLY public.asset_whiteboard_elements DROP CONSTRAINT IF EXISTS asset_whiteboard_elements_pkey;

ALTER TABLE IF EXISTS ONLY public.assets DROP CONSTRAINT IF EXISTS assets_pkey;
ALTER TABLE IF EXISTS public.assets ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS background_jobs_pkey;

ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS canvas_lti_key_key;
ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS canvas_lti_secret_key;
ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS canvas_pkey;

ALTER TABLE IF EXISTS ONLY public.canvas_poller_api_keys
  DROP CONSTRAINT IF EXISTS canvas_poller_api_keys_pkey;

ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS public.categories ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_pkey;
ALTER TABLE IF EXISTS public.comments ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.course_groups DROP CONSTRAINT IF EXISTS courses_pkey;
ALTER TABLE IF EXISTS public.course_groups ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.courses DROP CONSTRAINT IF EXISTS courses_pkey;
ALTER TABLE IF EXISTS public.courses ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.whiteboard_sessions DROP CONSTRAINT IF EXISTS whiteboard_sessions_pkey;

ALTER TABLE IF EXISTS ONLY public.whiteboard_users DROP CONSTRAINT IF EXISTS whiteboard_users_pkey;

ALTER TABLE IF EXISTS ONLY public.whiteboards DROP CONSTRAINT IF EXISTS whiteboards_pkey;
ALTER TABLE IF EXISTS public.whiteboards ALTER COLUMN id DROP DEFAULT;

--

DROP INDEX IF EXISTS activities_actor_id_idx;
DROP INDEX IF EXISTS activities_asset_id_idx;
DROP INDEX IF EXISTS activities_created_at_idx;
DROP INDEX IF EXISTS activities_object_id_idx;
DROP INDEX IF EXISTS activities_object_type_idx;

DROP INDEX IF EXISTS activity_types_type_course_id_idx;

DROP INDEX IF EXISTS asset_categories_asset_id_idx;
DROP INDEX IF EXISTS asset_categories_category_id_idx;

DROP INDEX IF EXISTS asset_users_asset_id_idx;
DROP INDEX IF EXISTS asset_users_user_id_idx;

DROP INDEX IF EXISTS course_group_memberships_canvas_user_id_idx;

DROP INDEX IF EXISTS whiteboard_elements_created_at_uuid_whiteboard_id_idx;
DROP INDEX IF EXISTS whiteboard_elements_id_idx;

DROP INDEX IF EXISTS whiteboard_sessions_user_id_idx;
DROP INDEX IF EXISTS whiteboard_sessions_whiteboard_id_idx;

--

DROP SEQUENCE IF EXISTS public.activities_id_seq;
DROP TABLE IF EXISTS public.activities;
DROP SEQUENCE IF EXISTS public.activity_types_id_seq;
DROP TABLE IF EXISTS public.activity_types;
DROP TABLE IF EXISTS public.asset_categories;
DROP TABLE IF EXISTS public.asset_users;
DROP TABLE IF EXISTS public.asset_whiteboard_elements;
DROP SEQUENCE IF EXISTS public.assets_id_seq;
DROP TABLE IF EXISTS public.assets;
DROP TABLE IF EXISTS public.background_jobs;
DROP TABLE IF EXISTS public.canvas;
DROP TABLE IF EXISTS public.canvas_poller_api_keys;
DROP SEQUENCE IF EXISTS public.categories_id_seq;
DROP TABLE IF EXISTS public.categories;
DROP SEQUENCE IF EXISTS public.comments_id_seq;
DROP TABLE IF EXISTS public.comments;
DROP TABLE IF EXISTS public.course_group_memberships;
DROP SEQUENCE IF EXISTS public.course_groups_id_seq;
DROP TABLE IF EXISTS public.course_groups;
DROP SEQUENCE IF EXISTS public.courses_id_seq;
DROP TABLE IF EXISTS public.courses;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.whiteboard_elements;
DROP SEQUENCE IF EXISTS public.whiteboard_elements_id_seq;
DROP TABLE IF EXISTS public.whiteboard_sessions;
DROP TABLE IF EXISTS public.whiteboard_users;
DROP SEQUENCE IF EXISTS public.whiteboards_id_seq;
DROP TABLE IF EXISTS public.whiteboards;

--

DROP TYPE IF EXISTS public.enum_activities_object_type;
DROP TYPE IF EXISTS public.enum_activities_type;
DROP TYPE IF EXISTS public.enum_assets_type;
DROP TYPE IF EXISTS public.enum_users_canvas_enrollment_state;

--
