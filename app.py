"""
1 - Alterar o método de login
2 - Adicionar temporizador 30s para renovação de token
3 - Criar mecanismo de reativação/criação de novo token
4 - Ler planilha
5 - Verificar se ramal existe
    5.1 - Se existir, alterar
    5.2 - Se não existir, criar
6 - Verificar se rota existe
    6.1 - Se existir, alterar
    6.2 - Se não existir, criar
7 - Atualizar tratativa de resposta
8 - Atualizar logs
9 - Atualizar chamada de script
10 - Atualizar leitura de templates
11 - Atualizar criação de payload
12 - Atualizar POST/PUT
13 - Atualizar GET
14 - Atualizar mecanismo de leitura de configuração - OK def config()
"""
# Passo a passo
"""
1. Criar Base relacionando Loja com Portal CFY. (Portal 2,3,8 - Validar Versão) (Portal 9 - Criar estrutura completa)
2. Identificar provider ID para SBC08 em cada Portal CFY.
3. Ignorar Ramais de vendas.
4. Validar usuário por email.
5. Criar regra de entra para cada user.
6. validar SBC de Saída. 
7. Inserir outbound caller.
8. Inserir usuário no grupo.
"""
# Criar seletor de portal e versão

from flask import Flask, jsonify, render_template, redirect, url_for, request
import json
import requests
import logging
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning # type: ignore

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

REQUESTDATA = {}

app = Flask(__name__)

# Função para executar POST
def postRequest(url:str, headers, payload):
    response = requests.post(url, headers=headers, data=payload, verify=False)
    return response

# Função para executar GET
def getRequest(url:str, cookies):
    response = requests.get(url, cookies=cookies, verify=False)
    if response.status_code == 200:
        return response
    else:
        logging.error(f"ERROR: ({response.status_code}) - {response.text}")
        return None

def api_login(version:str, portal:str, username:str, password:str):
    global REQUESTDATA
    domain = "https://" + portal + ".contactfy.cloud:8887"
    payload = {
        "username": username,
        "password": password
    }
    print(version)
    if version == 'v16':
        url = domain + "/api/login"
    elif version == 'v22':
        url = domain + "/api/auth/sign_in"
    print(url, payload)
    response = postRequest(url, {'Content-Type': 'application/json'}, json.dumps(payload, indent=4, ensure_ascii=False))
    if response is None or (response.status_code != 200 and response.status_code != 201):
        return "Sem resposta da API"
    else:
        if "access_token" in response.text:
            REQUESTDATA = response.json()
            return "Login v22 OK"
        else:
            cookies = response.cookies
            if cookies is None:
                return "Sem cookies"
            response = getRequest(url=str(url), cookies=cookies)
            if response is None:
                return "Sem resposta de consulta"
            try:
                REQUESTDATA = response.json()
            except json.JSONDecodeError as e:
                return
            return  "Login v16 OK"

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        portal = request.form['portal']
        version = request.form['version']
        api_login(version, portal, user, password)
        return render_template('selecao.html', user=user, portal=portal, version=version)
    return render_template('index.html')

if __name__ == '__main__':
    timestamp = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'log_ramal_{timestamp}.log'
    logging.basicConfig(
    filename=log_filename,  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode="a"
    )
    app.run(host='0.0.0.0', port=6543)