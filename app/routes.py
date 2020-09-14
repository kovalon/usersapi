import uuid
from jsonschema import Draft7Validator
from app import app
from flask import jsonify, make_response, request
from flask import abort
import json
from .schemes import user_schema


# Предварительно распишем базовые ответы для ошибок 400, 404 и 500
# При их обнаружении в ответ при вызове abort() будут выдаваться именно такие
# их представления (в json формате)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(500)
def bad_request(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)


# Распишем обработчики для запросов

# Обработчик для GET запроса, выдающий всех имеющихся пользователей
@app.route('/api/users', methods=['GET'])
def get_users():
    # открываем json файл с записями пользователей
    # и выдаем его в ответ
    with open('sources/users.json', 'r') as file:
        users = json.load(file)
    return jsonify({'users': users})


# Обработчик для запроса нахождения пользователя по id
@app.route('/api/users/<uuid:id>', methods=['GET'])
def get_user(id):
    # открываем json файл с записями пользователей
    with open('sources/users.json', 'r') as file:
        users = json.load(file)
    # ищем пользователя по id
    user = list(filter(lambda t: t['id'] == str(id), users))
    # если не найден, то выдаем 404 ошибку, иначе выдаем пользователя
    if len(user) == 0:
        abort(404)
    return jsonify({'user': user[0]})


# Обработчик для запроса создания пользователя
@app.route('/api/users', methods=['POST'])
def create_user():
    # загружаем схему валидации
    v = Draft7Validator(user_schema)
    # через схему валидации проверяем, что тело запроса соотвествует нашим требованиям
    # если имеютя ошибки, возвращаем их описание назад с кодом 400
    errors = [error.message for error in sorted(v.iter_errors(request.json), key=lambda e: e.path)]
    if len(errors) > 0:
        return make_response(jsonify({'errors': errors}), 400)
    # если все корректно, открываем наш файл с записями
    with open('sources/users.json', 'r', encoding='utf-8') as file:
        users = json.load(file)
    # добавляем новую запись
    id = uuid.uuid4()
    users.append({
        "id": str(id),
        "name": request.json['name']
    })
    # перезаписываем наш файл
    with open('sources/users.json', 'w', encoding='utf-8') as file:
        json.dump(users, file)
    # и после этого берем из него по id нашу запись и выдаем в отает
    with open('sources/users.json', 'r', encoding='utf-8') as file:
        users = json.load(file)
    user = list(filter(lambda t: str(t['id']) == str(id), users))
    return jsonify({'user': user[0]}), 201


# Обработчик для запроса изменения пользователя
@app.route('/api/users/<uuid:id>', methods=['PUT'])
def update_user(id):
    # ищем в json файле пользователя с id из запроса
    with open('sources/users.json', 'r') as file:
        users = json.load(file)
    user = list(filter(lambda t: t['id'] == str(id), users))
    # если не найден, выдаем 404 ошибку
    if len(user) == 0:
        abort(404)
    # загружаем схему валидации
    v = Draft7Validator(user_schema)
    # проверяем тело запроса на ошибки
    errors = [error.message for error in sorted(v.iter_errors(request.json), key=lambda e: e.path)]
    if len(errors) > 0:
        return make_response(jsonify({'errors': errors}), 400)
    # изменяем данные пользователя
    user[0]['name'] = request.json.get('name', user[0]['name'])
    # перезписываем файл
    with open('sources/users.json', 'w', encoding='utf-8') as file:
        json.dump(users, file)
    # берем из перезаписанного файла данные пользователя по id из запроса
    with open('sources/users.json', 'r', encoding='utf-8') as file:
        users = json.load(file)
    user = list(filter(lambda t: str(t['id']) == str(id), users))
    # выдаем его в ответ
    return jsonify({'user': user[0]})


# Обработчик для запроса удаления пользователя
@app.route('/api/users/<uuid:id>', methods=['DELETE'])
def delete_user(id):
    # ищем пользователя с id из запроса
    with open('sources/users.json', 'r') as file:
        users = json.load(file)
    user = list(filter(lambda t: t['id'] == str(id), users))
    # если нет, выдаем 404 ошибку
    if len(user) == 0:
        abort(404)
    # удаляем его из существующих записей
    users.remove(user[0])
    # перезаписываем файл
    with open('sources/users.json', 'w', encoding='utf-8') as file:
        json.dump(users, file)
    # в ответ выдаем сообщение об успешном удалении
    return jsonify({'result': "user {} deleted".format(id)})
