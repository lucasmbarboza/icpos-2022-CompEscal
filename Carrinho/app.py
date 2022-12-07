from flask import Flask, jsonify, request
import requests
import redis
import json


app = Flask(__name__)


item = [{'color': 'blue', 'size': 'P', 'Quantity': 3}, {'color': 'blue', 'size': 'M', 'Quantity': 3}, {'color': 'blue', 'size': 'G', 'Quantity': 3},
        {'color': 'red', 'size': 'P', 'Quantity': 3}, {'color': 'red', 'size': 'M', 'Quantity': 3}, {'color': 'red', 'size': 'G', 'Quantity': 3}]

cart = [{'id': 0, 'items': [], 'frete':0}]


def searchAll(dict, *args):
    t = []
    aux = 0
    args = args[0]
    for i in dict:
        if i[args[1]] == args[2]:
            t.append(i)
    return t


def searchIndex(dict, *args):
    aux = 0
    args = args[0].pop(0)
    if len(args) > 3:
        for i in dict:
            if i[args[0]] == args[1] and i[args[2]] == args[3]:
                return aux
            elif aux <= len(dict):
                aux = aux + 1
            else:
                return None
    elif len(args) > 1:
        for i in dict:
            if i[args[0]] == args[1]:
                return aux
            elif aux <= len(dict):
                aux = aux + 1
            else:
                return None
    else:
        return None


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = 'password'


red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def search(dict, *args):  # blusa, azul, size, p
    searchType = args[0]
    values = list(args)
    if searchType == 'index':  # retorna o index de um item especifico
        return searchIndex(dict, values)
    elif searchType == 'all':  # Retorna todos os items com a mesma caracteristica
        return searchAll(dict, values)
    else:
        return None


# AddToCard - Adiciona item ao carrinho -> Trigga CalcFrete
# RemoveToCart - Remove item do carrinho -> Trigga CalcFrete
# SendToPayment - Limpa o carrinho -> Trigga  Payment -> Trigga GenNF
# GenNF - Gera Nota Fiscal -> Trigga RmStoque
# UpdateEstoque - Remove o item comprado no Estoque -> Trigga updateCatalogo

@ app.route('/cart/<string:id>', methods=['GET', 'POST', 'DELETE'])
def getCart(id=None):
    args = request.args
    color = args.get('color')
    size = args.get('size')

    if request.method == 'GET':
        if id == None:
            return jsonify({'Error': 'Specify a cart'})
        else:
            return jsonify(search(cart, 'all', 'id', int(id)))

    elif request.method == 'POST':
        response = request.get_json()
        for i in cart:
            if i['id'] == int(id):
                i['items'].append(response)
                red.publish(
                    "event", json.dumps({"event": "AddToCart", "Data": i},
                                        indent=2).encode('utf-8'))
            return jsonify(i)

    elif request.method == 'DELETE':
        for i in cart:
            if i['id'] == int(id):
                for j in i['items']:
                    if j['color'] == color.lower() and j['size'] == size.upper():
                        i['items'].remove(j)
                red.publish(
                    "event", json.dumps({"event": "RemoveToCart", "Data": i},
                                        indent=2).encode('utf-8'))
                return jsonify(i)
        return {'Error': 'Cart or Item not found'}


@ app.route('/setfrete', methods=['POST'])
def setFrete():
    response = request.get_json()  # {'id':0 ,'frete': 1}
    for i in cart:
        if i['id'] == response['id']:
            i['frete'] = response['frete']


@ app.route('/submit/<string:id>', methods=['GET'])
def subPurchase(id=None):
    global cart
    if id != None:
        for i in cart:
            if i['id'] == int(id):
                red.rpush("event", json.dumps(
                    {"event": "SendToPayment", "Data": i}, indent=2).encode('utf-8'))
                cart = [{'id': 0, 'items': [], 'frete':0}]
                return 'Waiting for payment'
    else:
        return 'Provide a cart Id'


@ app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass
