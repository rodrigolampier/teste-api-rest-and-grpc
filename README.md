# teste-api-rest-and-grpc

Veremos que GRPC tem tempo de resposta mais rápido do que RESTAPI.


## Para permitir a execução desse script. Abra um terminal no Ubuntu e execute:
sudo apt install python3-pip
pip3 install grpcio tensorflow tensorflow-serving-api


# Teste usando GRPC
python cliente_cls.py -p 8500 -ip localhost

# Teste usando RESTAPI
python cliente_cls.py -p 8501 -ip localhost
