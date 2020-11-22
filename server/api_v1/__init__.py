"""API v1"""
from collections import UserString
from datetime import datetime

from flask import Blueprint, jsonify, request

from core import db

bp = Blueprint('api_v1', __name__, url_prefix='/api_v1')


class NonEmptyString(UserString):  # pylint: disable=too-many-ancestors
    """Not empty string"""

    def __init__(self, *args):
        super().__init__(*args)
        if len(self) == 0:
            raise ValueError('string must be not empty')


# Stupid simple data converterts/validators
ADD_MODEL = [
    ('dev_type', NonEmptyString),
    ('operator', NonEmptyString),
    ('dt', datetime.fromisoformat),
    ('success', lambda x: bool(int(x))),
]


def api_error(description, code=400):
    """Build API error"""
    resp = jsonify({'message': description})
    resp.status_code = code
    return resp


@bp.route('/stat', methods=['GET'])
def stat():
    """Generate statistic"""

    # prepare
    where = ['TRUE']
    args = []

    # process where
    operator = request.args.get('operator')
    if operator:
        where.append('operator = ?')
        args.append(operator)

    # build query
    query = """
       SELECT
             dev_type,
             count(success) as count,
             sum(CASE success WHEN TRUE THEN 1 ELSE 0 END) as successful,
             sum(CASE success WHEN FALSE THEN 1 ELSE 0 END) as failed
        FROM
            test_results
        WHERE
            {0}
        GROUP BY
            dev_type
    """.format(' AND '.join(where))

    # fetch and return results
    with db.get_conn() as conn:
        return jsonify([dict(item) for item in conn.execute(query, args).fetchall()])


@bp.route('/test_result', methods=['POST'])
def test_result_add():
    """Add test result"""

    query = """
        INSERT INTO
            test_results(dev_type, operator, dt, success)
        VALUES
            (?, ?, ?, ?)
    """

    # conv
    try:
        args = [str(conv(request.form[field])) for field, conv in ADD_MODEL]
    except ValueError as exc:
        return api_error(str(exc))

    # add to db
    with db.get_conn() as conn:
        inserted_id = conn.execute(query, args).lastrowid

    return jsonify({'id': inserted_id})


@bp.route('/test_result/<int:id>', methods=['DELETE'])
def test_result_remove(id):  # pylint: disable=invalid-name,redefined-builtin
    """Remove test result"""
    query = 'DELETE FROM test_results WHERE id = ?'
    args = [id]
    with db.get_conn() as cur:
        rowcount = cur.execute(query, args).rowcount

    if rowcount == 0:
        return api_error('Item not found', 404)
    return '1'
