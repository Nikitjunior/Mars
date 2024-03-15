import flask
from flask import jsonify, make_response, request

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(
                    only=('id', 'team_leader', 'job', 'work_size',
                          'collaborators', 'start_date', 'end_date', 'is_finished'))
                    for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<job_id>', methods=['GET'])
def get_one_job(job_id):
    try:
        job_id = int(job_id)
    except ValueError:
        return make_response(jsonify({"error": "Bad Request"}), 400)

    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)

    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return jsonify({
        'jobs': job.to_dict(only=('id', 'team_leader', 'job', 'work_size',
                                  'collaborators', 'start_date', 'end_date', 'is_finished'))
    })


@blueprint.route('/api/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    job = Jobs(
        team_leader=request.json['team_leader'],
        job=request.json['job'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        start_date=request.json['start_date'],
        end_date=request.json['end_date'],
        is_finished=request.json['is_finished'],

    )
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'id': job.id})


@blueprint.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        job_id = int(job_id)
    except ValueError:
        return make_response(jsonify({"error": "Bad Request"}), 400)

    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<job_id>', methods=['PUT'])
def edit_job(job_id):
    try:
        job_id = int(job_id)
    except ValueError:
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)

    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)

    data = request.json
    if not data:
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    job.team_leader = data.get('team_leader', job.team_leader)
    job.job = data.get('job', job.job)
    job.work_size = data.get('work_size', job.work_size)
    job.collaborators = data.get('collaborators', job.collaborators)
    job.is_finished = data.get('is_finished', job.is_finished)

    db_sess.commit()

    return jsonify({'success': 'OK'})
