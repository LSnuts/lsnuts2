from flask import jsonify


def ok(data=None, msg='success'):
    return jsonify({'code': 200, 'msg': msg, 'data': data})


def fail(msg, code=400):
    return jsonify({'code': code, 'msg': msg}), code
