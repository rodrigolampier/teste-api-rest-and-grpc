# Script para testar conexão ao TensorFlow Serving

# Imports
import grpc
import base64
import argparse
import requests
import tensorflow as tf
from datetime import datetime
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

# Verifica a versão do TF
tf_v = 2
if tf.__version__.startswith('2'):
  import tensorflow.compat.v1 as tf
  tf.disable_v2_behavior()
else:
  tf_v = 1

# Leitura e parse dos argumentos
parser = argparse.ArgumentParser(description = '')
parser.add_argument('-p','--port', help = 'Porta de conexão', default = '8500')
parser.add_argument('-ip','--ipaddress', help = 'Endereço ip', default = 'localhost')
args = vars(parser.parse_args())

# Variáveis
SERVER_URL = 'http://ipaddress:port/v1/models/resnet:predict'
IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'

# Leitura da imagem de teste do modelo
dl_request = requests.get(IMAGE_URL, stream = True)
dl_request.raise_for_status()
data = dl_request.content
jpeg_bytes = base64.b64encode(data).decode('utf-8')

# Função para chamada REST-API
def restapi_call(ip_address):
  server_url = SERVER_URL.replace('ipaddress', str(ip_address))
  server_url = server_url.replace('port', '8501')

  predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes

  for _ in range(2):
    response = requests.post(server_url, data=predict_request)
    response.raise_for_status()

  num_requests = 10
  time_taken_list = []
  print("*"*30)
  print("Chamada RESTAPI: ")
  print("*"*30)

  # Loop por 10 requisições para calcular o tempo médio
  for i in range(num_requests):
    start = datetime.now()
    response = requests.post(server_url, data = predict_request)
    time_taken = (datetime.now() - start).total_seconds()
    print(f"{i}. Tempo Gasto: {time_taken}")
    time_taken_list.append(time_taken)
  total_time = sum(time_taken_list)
  avg_time = total_time / len(time_taken_list)
  print('Tempo Médio de Processamento: ', avg_time)

# Função para chamada gRPC
def grpc_call(ip_address):
  channel = grpc.insecure_channel(f'{ip_address}:8500')
  stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
  request = predict_pb2.PredictRequest()
  request.model_spec.name = 'resnet'
  request.model_spec.signature_name = 'serving_default'
  if tf_v == 1:
    request.inputs['image_bytes'].CopyFrom(
        tf.contrib.util.make_tensor_proto(data, shape=[1]))
  if tf_v == 2:
    request.inputs['image_bytes'].CopyFrom(
        tf.make_tensor_proto(data, shape=[1]))

  for i in range(2):
    result = stub.Predict(request, 10.0)  

  num_requests = 10
  time_taken_list = []
  print("*"*30)
  print('Chamada GRPC:')
  print("*"*30)
  for i in range(num_requests):
    start = datetime.now()
    result = stub.Predict(request, 10.0) 
    time_taken = (datetime.now() - start).total_seconds()
    print(f"{i}. Tempo Gasto: {time_taken}")
    time_taken_list.append(time_taken)
  total_time = sum(time_taken_list)
  avg_time = total_time / len(time_taken_list)
  print('Tempo Médio de Processamento: ', avg_time)

# Execução do programa
if __name__ == '__main__':
  ip_address = args['ipaddress']
  port = args['port']

  if port == '8500':
    grpc_call(ip_address)
  else:
    restapi_call(ip_address)

    