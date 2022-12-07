# AddToCard - Adiciona item ao carrinho -> Trigga CalcFrete
# RemoveToCart - Remove item do carrinho -> Trigga CalcFrete
# SendToPayment - Limpa o carrinho -> Trigga  Payment -> Trigga GenNF
# GenNF - Gera Nota Fiscal -> Trigga UpdateEstoque
# UpdateEstoque - Remove o item comprado no Estoque -> Trigga updateCatalogo
import requests
import redis
import json
#from flask import jsonify
import logging
import os

FISSION = '127.0.0.1:8089'  # os.getenv('FISSION')
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
logging.getLogger().setLevel(logging.DEBUG)

print(FISSION)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
try:
    pub = r.pubsub()
    pub.subscribe('event')
    aux = 0
    while True:
        data = pub.get_message()

        if data != None:
            if data['data'] != 1:
                data = data['data'].decode('UTF-8')
                d = json.loads(data)
                print(d)
                aux = aux+1
                print(aux)
                event = d['event']
                payload = d['Data']

                match event:
                    case 'AddToCart':
                        print(event)
                        logging.info(
                            'INFO: Event: {}, Data: {}'.format(event, payload))
                        req = requests.post(
                            url='http://'+FISSION+'/calc', data=payload)
                        req.content
                        if 500 == req.status_code or 404 == req.status_code:
                            r.publish(
                                "Error", json.dumps({"Error": "CalcFrete Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                        else:
                            logging.info(
                                msg='Event: FUNCTION_RESPONSE, Data: {}'.format(req.content.decode('UTF-8')))

                    case 'RemoveToCart':
                        logging.info(
                            msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        req = requests.post(
                            'http://'+FISSION+'/calc', data=payload)
                        if 500 == req.status_code or 404 == req.status_code:
                            r.publish(
                                "Error", json.dumps({"Error": "CalcFrete Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.error(
                                msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        else:
                            logging.info(
                                msg='Event: FUNCTION_RESPONSE, Data: {}'.format(req.content.decode('UTF-8')))
                    case 'SendToPayment':
                        logging.info(
                            msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        req = requests.post(
                            'http://'+FISSION+'/payment', data=payload)
                        if 500 == req.status_code == 404 in req.status_code:
                            r.publish(
                                "event", json.dumps({"Error": "Payment Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.error(
                                msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        else:
                            r.publish(
                                "event", json.dumps({"event": "GenNF", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.info(
                                msg='Event: FUNCTION_RESPONSE, Data: {}'.format(req.content.decode('UTF-8')))
                    case 'GenNF':
                        logging.info(
                            msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        req = requests.post(
                            'http://'+FISSION+'/gennf', data=(payload))
                        if 500 == req.status_code or 404 == req.status_code:
                            r.publish(
                                "event", json.dumps({"Error": "GenNF Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.error(
                                msg='INFO:Error: {}, Data: {}'.format(event, payload))
                        else:
                            r.publish(
                                "event", json.dumps({"event": "UpdateEstoque Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.info(
                                msg='Event: FUNCTION_RESPONSE, Data: {}'.format(req.content.decode('UTF-8')))
                    case 'UpdateEstoque':
                        logging.info(
                            msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        req = requests.post(
                            'http://'+FISSION+'/updateestoque', data=(payload))
                        if 500 == req.status_code or 404 == req.status_code:
                            r.publish(
                                "Error", json.dumps({"Error": "UpdateEstoque Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.error(
                                msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        else:
                            r.publish(
                                "event", json.dumps({"event": "UpdateEstoque", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.info(
                                msg='Event: FUNCTION_RESPONSE, Data: {}'.format(req.content.decode('UTF-8')))
                    case 'UpdateCatalogo':
                        logging.info(
                            msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        req = requests.post(
                            'http://'+FISSION+'/updatecatalog', data=(payload))
                        if 500 == req.status_code or 404 == req.status_code:
                            r.publish(
                                "event", json.dumps({"Error": "UpdateCatalogo Error", "Data": payload},
                                                    indent=2).encode('utf-8'))
                            logging.error(
                                msg='INFO: Event: {}, Data: {}'.format(event, payload))
                        else:
                            logging.info(
                                msg='Event: FUNCTION_RESPONSE, Data: {}'.format(req.content.decode('UTF-8')))
except NameError:
    print('Error: ', NameError)
