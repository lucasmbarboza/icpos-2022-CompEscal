from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


item = [{'color': 'blue', 'size': 'P', 'Quantity': 3}, {'color': 'blue', 'size': 'M', 'Quantity': 3}, {'color': 'blue', 'size': 'G', 'Quantity': 3},
        {'color': 'red', 'size': 'P', 'Quantity': 3}, {'color': 'red', 'size': 'M', 'Quantity': 3}, {'color': 'red', 'size': 'G', 'Quantity': 3}]

cart = [{'id': 0, 'items': []}]


def searchColor(color):
    t = []
    aux = 0
    if color == 'all':
        return item
    for i in item:
        if i['color'] == color:
            t.append(i)
    return t


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


def search(dict, *args):  # blusa, azul, size, p
    searchType = args[0]
    values = list(args)
    if searchType == 'index':  # retorna o index de um item especifico
        return searchIndex(dict, values)
    elif searchType == 'all':  # Retorna todos os items com a mesma caracteristica
        return searchAll(dict, values)
    else:
        return None


def rmCatalogue(color, size):
    index = search(item, ['index', 'color', color, 'size', size])
    item[index]['Quantity'] = item[index]['Quantity'] - 1
    if item[index]['Quantity'] == 0:
        item.pop(index)
    return jsonify(item)


@ app.route('/catalogue', methods=['GET', 'DELETE'])
def getCatalogue(color=None, size=None):
    args = request.args
    if request.method == 'GET':
        color = args.get('color')
        size = args.get('size')
        if color != None:
            return jsonify(search(item, 'all', 'color', color.lower()))
        elif size != None:
            return jsonify(search(item, 'all', 'size', size.upper()))
        else:
            return jsonify(item)
    if request.method == 'DELETE':
        size = args.get('size').upper()
        color = args.get('color').lower()
        return rmCatalogue(size=size, color=color)


@ app.route('/cart/<string:id>', methods=['GET', 'POST', 'DELETE'])
def getCart(id=None):
    args = request.args
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
            return jsonify(i)
    elif request.method == 'DELETE':
        color = args.get('color')
        size = args.get('size')
        for i in cart:
            if i['id'] == int(id):
                for j in i['items']:
                    if j['color'] == color.lower() and j['size'] == size.upper():
                        i['items'].remove(j)
                return jsonify(i)
        return {'Error': 'Cart or Item not found'}


@app.route('/submit/<string:id>')
def subPurchase(id=None):
    for i in cart:
        if i['id'] == int(id):
            req = requests.post('$SHIPPING/shipping', data=jsonify(i))
    if 20 in req.status_code:
        return 200


@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass
