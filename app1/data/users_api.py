import flask
from flask import jsonify, make_response, request

from . import db_session
from .users import User



user_blueprint = flask.Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@user_blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users': [user.to_dict(only=('id', 'surname', 'name', 'age', 'position',
                                         'speciality', 'address', 'email', 'modified_date'))
                      for user in users]
        }
    )


@user_blueprint.route('/api/users/<user_id>', methods=['GET'])
def get_one_user(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return make_response(jsonify({"error": "Bad Request"}), 400)

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return jsonify({
        'users': user.to_dict(only=('id', 'surname', 'name', 'age', 'position',
                                     'speciality', 'address', 'email', 'modified_date'))
    })


@user_blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'password']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()
    user = User(
        surname=request.json['surname'],
        name=request.json['name'],
        age=request.json['age'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        email=request.json['email']
    )
    user.set_password(request.json['password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'id': user.id})


@user_blueprint.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return make_response(jsonify({"error": "Bad Request"}), 400)

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@user_blueprint.route('/api/users/<user_id>', methods=['PUT'])
def edit_user(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)

    data = request.json
    if not data:
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    user.surname = data.get('surname', user.surname)
    user.name = data.get('name', user.name)
    user.age = data.get('age', user.age)
    user.position = data.get('position', user.position)
    user.speciality = data.get('speciality', user.speciality)
    user.address = data.get('address', user.address)
    user.email = data.get('email', user.email)

    db_sess.commit()

    return jsonify({'success': 'OK'})
