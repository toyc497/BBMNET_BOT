import asyncio
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from BotScraping.BBMNET_Scraping import BBMNET_Scraping
from WebsocketConnect.Websockets_Connection import Websockets_Connection
from environment.environment import Environment
from models.CredencialEntity import CredencialEntity
from models.EditalEntity import EditalEntity
import requests


class Main:

    editaisBBMNET_Entity = []
    credencialBBMNET_Entity = None
    accessToken = ''
    accesTokenKeycloak = ''
    refreshTokenKeycloak = ''

    def getKeycloakAcessToken(self):

        urlToken = Environment.keycloakUriLogin
        headersToken = {'Content-Type': 'application/x-www-form-urlencoded'}
        bodyToken = {
            'client_id': Environment.keycloak_clientId,
            'username': Environment.keycloak_username,
            'password': Environment.keycloak_password,
            'grant_type': Environment.keycloak_grantType
        }

        requestAuthToken = requests.post(urlToken, headers=headersToken, data=bodyToken)

        if requestAuthToken.status_code == 200:
            tokenPayload = requestAuthToken.json()
            getAccessToken = tokenPayload['access_token']
            getRefreshToken = tokenPayload['refresh_token']
            self.accesTokenKeycloak = f'Bearer {getAccessToken}'
            self.refreshTokenKeycloak = f'{getRefreshToken}'

    def logoutKeycloak(self):
        headersToken = {'Authorization': f'{self.accesTokenKeycloak}', 'Content-Type': 'application/x-www-form-urlencoded'}
        bodyToken = {
            'client_id': Environment.keycloak_clientId,
            'refresh_token': self.refreshTokenKeycloak
        }
        requests.post(Environment.keycloakUriLogout, headers=headersToken, data=bodyToken)

    def getToken(self):
        urlToken = 'https://bbmnet-cad-participantes-prd.rj.r.appspot.com/auth/realms/BBM/protocol/openid-connect/token'
        headersToken = {'Content-Type': 'application/x-www-form-urlencoded'}
        bodyToken = {
            'grant_type': 'password',
            'client_id': 'cadastro-participantes-admin-site',
            'username': f'{self.credencialBBMNET_Entity.usuario}',
            'password': f'{self.credencialBBMNET_Entity.senha}'
        }

        requestAuthToken = requests.post(urlToken, headers=headersToken, data=bodyToken)

        if requestAuthToken.status_code == 200:
            tokenContent = requestAuthToken.json()
            tokenCode = tokenContent['access_token']
            tokenBearer = f'Bearer {tokenCode}'
            self.accessToken = tokenBearer

    def pregoes_API_DATA(self):
        print('Running')
        urlAPI = 'http://127.0.0.1:8085/bot/editais_to_scraping'
        headersToken = {'Authorization': f'{self.accesTokenKeycloak}'}
        credenciaisObjectsResponse = None
        editaisObjectsResponse = None
        responseAPI_plataform = requests.get(urlAPI, headers=headersToken)

        if responseAPI_plataform.status_code == 200:
            responseObjectsAPI = responseAPI_plataform.json()
            editaisObjectsResponse = responseObjectsAPI['edital']
            credenciaisObjectsResponse = responseObjectsAPI['credencial']

        for edital in editaisObjectsResponse:
            editalObject = EditalEntity(edital['id'], edital['chaveEdital'], edital['numeroPregao'], edital['orgao'],
                                        edital['lote'], edital['lastMessageDate'])
            self.editaisBBMNET_Entity.append(editalObject)

        for credencial in credenciaisObjectsResponse:
            credencialObject = CredencialEntity(credencial['id'], credencial['usuario'], credencial['senha'],
                                                credencial['sistema'])
            self.credencialBBMNET_Entity = credencialObject

    def searchPregaoAba(self, editalAtual_Entity):
        uniqueIdOrgao = ''
        abaNumber = 0

        headersRequests = {
            'Content-Type': 'application/json',
            'Usuario-Id': '69f72adf-bb81-48b5-ae79-a937f4f0bcd2',
            'Participante-Id': '9c73820f-0700-477b-b151-bbb7d9fcbe27',
            'Authorization': self.accessToken
        }
        urlOrgaosPromotores = 'https://cadastro-participantes-backend-fm2e4c7u4q-rj.a.run.app/api/Licitacoes/orgaospromotores'
        responseOrgaos = requests.get(urlOrgaosPromotores, headers=headersRequests)

        if responseOrgaos.status_code == 200:
            orgaosList = responseOrgaos.json()
            for orgao in orgaosList:
                if orgao['nomeFantasia'] == f'{editalAtual_Entity.orgao}':
                    uniqueIdOrgao = orgao['uniqueId']

        urlAbaPregao = 'https://southamerica-east1-bbmnet-licitacoes-prd-377317.cloudfunctions.net/fastRoutes/lotes/getTabAmountCostumQuery/3'
        bodyPregaoInfo = [
            {
                'description': 'Edital.NumeroEdital',
                'value': f'{editalAtual_Entity.chaveEdital}', 'clausula': '=='
            },
            {
                'description': 'Edital.OrgaoPromotor.Id',
                'value': uniqueIdOrgao,
                'clausula': '=='
            },
            {
                'description': 'Numero',
                'value': editalAtual_Entity.lote, 'clausula': '=='
            }
        ]

        responseAbaPregao = requests.post(urlAbaPregao, json=bodyPregaoInfo, headers=headersRequests)
        if responseAbaPregao.status_code == 200:
            listaAbas = responseAbaPregao.json()
            counter = 1
            while counter <= len(listaAbas):
                if listaAbas[f'{counter}'] == 1:
                    abaNumber = counter
                counter += 1

        return abaNumber

    def websocket_client(self, messagesList):

        urlPostMessage_API = 'http://127.0.0.1:8085/mensagem/save'

        counter = 0
        while counter < len(messagesList):
            mensagem_scraping = None

            mensagemToDatabase_API = {
                "origem": messagesList[counter]['origem'].split(" -")[0],
                "dataHora": messagesList[counter]['dataHora'],
                "conteudo": messagesList[counter]['conteudo'].strip(),
                "idEdital": messagesList[counter]['idEdital']
            }
            headers = {'Content-Type': 'application/json', 'Authorization': f'{self.accesTokenKeycloak}'}
            responsePost_API = requests.post(urlPostMessage_API, json=mensagemToDatabase_API, headers=headers)

            if responsePost_API.status_code == 200 or responsePost_API.status_code == 201:
                mensagem_scraping = responsePost_API.json()
                print('Inserted: ',responsePost_API.text)
            else:
                print('erro: ',responsePost_API.text)

            mensagem_converted = json.dumps(mensagem_scraping, ensure_ascii=False)
            asyncio.get_event_loop().run_until_complete(Websockets_Connection().listen([self.accesTokenKeycloak, mensagem_converted]))
            counter += 1

    def compareDates(self, messagesList, editalAtual):
        messagesToSendList = []

        for mensagem in messagesList:
            lastDataHoraAPI = None
            dataHoraSeparada = mensagem['dataHora'].strip().split(" ")
            dataSeparada = dataHoraSeparada[0].split("/")
            dtHrToConvert = f'{dataSeparada[2]}-{dataSeparada[1]}-{dataSeparada[0]} {dataHoraSeparada[1]}'

            dataHoraBBMNET = datetime.strptime(dtHrToConvert, '%Y-%m-%d %H:%M:%S')

            if editalAtual.lastMessageDate != None:
                lastDataHoraAPI = datetime.strptime(editalAtual.lastMessageDate, '%Y-%m-%d %H:%M:%S')

            if lastDataHoraAPI == None or dataHoraBBMNET > lastDataHoraAPI:
                mensagem['dataHora'] = f"{dataHoraBBMNET}"
                messagesToSendList.append(mensagem)
                editalAtual.lastMessageDate = f"{dataHoraBBMNET}"

        return messagesToSendList

    def webscraping_execute(self):
        scraping_client = BBMNET_Scraping()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')

        service = Service()
        #options = webdriver.ChromeOptions()
        navegador = webdriver.Chrome(options=chrome_options, service=service)
        #chrome_options
        navegador.implicitly_wait(10)
        scraping_client.loginToGuiaPage(navegador, self.credencialBBMNET_Entity)

        editaisEntitySize = len(self.editaisBBMNET_Entity)
        counter = 0
        while counter < editaisEntitySize:
            try:
                print('Running')
                scraping_client.linkToHomePage(navegador)
                guiaPage_window_handles = navegador.window_handles

                editalAtual_Entity = self.editaisBBMNET_Entity[counter]
                navegador.switch_to.window(guiaPage_window_handles[1])

                abaIndexBBMNET = self.searchPregaoAba(editalAtual_Entity)

                scraping_client.setFiltrosPage(navegador, editalAtual_Entity)

                messagesList = scraping_client.findChatAba(navegador, editalAtual_Entity, abaIndexBBMNET)

                navegador.close()
                navegador.switch_to.window(guiaPage_window_handles[0])

                if messagesList != None:
                    messagesToSend = self.compareDates(messagesList, editalAtual_Entity)
                    self.websocket_client(messagesToSend)
                counter += 1
            except:
                print("Erro ao fazer scraping no pregão: "+editalAtual_Entity.chaveEdital)
                navegador.close()
                navegador.switch_to.window(guiaPage_window_handles[0])
                counter += 1

if __name__ == '__main__':
    main = Main()
    while True:
        main.getKeycloakAcessToken()
        main.pregoes_API_DATA()
        main.getToken()
        main.webscraping_execute()
        main.editaisBBMNET_Entity = []
        main.credencialBBMNET_Entity = None
        main.accessToken = ''
        main.logoutKeycloak()
        main.accesTokenKeycloak = ''
        main.refreshTokenKeycloak = ''
