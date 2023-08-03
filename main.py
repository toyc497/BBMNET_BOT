import asyncio
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from BotScraping.BBMNET_Scraping import BBMNET_Scraping
from WebsocketConnect.Websockets_Connection import Websockets_Connection
from models.CredencialEntity import CredencialEntity
from models.EditalEntity import EditalEntity
import requests


class Main:

    editaisObjectsResponse = None
    credenciaisObjectsResponse = None
    editaisBBMNET_Entity = []
    credencialBBMNET_Entity = []
    urlAPI = 'http://127.0.0.1:8085/bot/editais_to_scraping'
    lastMessagesDates = []
    lastDataHoraRegistered = None

    def pregoes_API_DATA(self):
        print('Running')
        responseAPI_plataform = requests.get(self.urlAPI)

        if responseAPI_plataform.status_code == 200:
            responseObjectsAPI = responseAPI_plataform.json()
            self.editaisObjectsResponse = responseObjectsAPI['edital']
            self.credenciaisObjectsResponse = responseObjectsAPI['credencial']

        for edital in self.editaisObjectsResponse:
            editalObject = EditalEntity(edital['id'], edital['chaveEdital'], edital['numeroPregao'], edital['orgao'],
                                        edital['lote'])
            self.editaisBBMNET_Entity.append(editalObject)

        for editalDate in self.editaisObjectsResponse:
            self.lastMessagesDates.append(editalDate['lastMessageDate'])

        for credencial in self.credenciaisObjectsResponse:
            credencialObject = CredencialEntity(credencial['id'], credencial['usuario'], credencial['senha'],
                                                credencial['sistema'])
            self.credencialBBMNET_Entity.append(credencialObject)

    def websocket_client(self, messagesList, editalAtual_Entity, credencialAtual_Entity):

        urlPostMessage_API = 'http://127.0.0.1:8085/mensagem/save'

        counter = 0
        while counter < len(messagesList):

            mensagemToDatabase_API = {
                "origem": messagesList[counter]['origem'],
                "dataHora": messagesList[counter]['dataHora'],
                "conteudo": messagesList[counter]['conteudo'],
                "idEdital": messagesList[counter]['idEdital']
            }
            headers = {'Content-Type': 'application/json'}
            responsePost_API = requests.post(urlPostMessage_API, json=mensagemToDatabase_API, headers=headers)

            if responsePost_API.status_code == 200 or responsePost_API.status_code == 201:
                print(responsePost_API.text)
            else:
                print('erro',responsePost_API.text)

            mensagem_scraping = {
                "idEdital": messagesList[counter]['idEdital'],
                "conteudo": messagesList[counter]['conteudo'],
                "origem": messagesList[counter]['origem'],
                "dataHora": messagesList[counter]['dataHora'],
                "orgao": editalAtual_Entity.orgao,
                "lote": editalAtual_Entity.lote,
                "chaveEdital": editalAtual_Entity.chaveEdital,
                "numeroPregao": editalAtual_Entity.numeroPregao,
                "sistema": {
                    "id": credencialAtual_Entity.sistema['id'],
                    "nome": credencialAtual_Entity.sistema['nome']
                }
            }
            mensagem_converted = json.dumps(mensagem_scraping, ensure_ascii=False)
            asyncio.get_event_loop().run_until_complete(Websockets_Connection().listen(mensagem_converted))
            counter += 1

    def compareDates(self, messagesList, indicePregaoList):
        dataDeComparacao = self.lastMessagesDates[indicePregaoList]
        messagesToSend_compared = []
        for mensagem in messagesList:
            dataHoraBBMNET = mensagem['dataHora']
            dataFormated = ""
            counter = 0
            while counter < len(dataHoraBBMNET):
                if dataHoraBBMNET[counter] != '-' and dataHoraBBMNET[counter] != ' ':
                    dataFormated += str(dataHoraBBMNET[counter])
                counter += 1
            dh_ObjectFormated = datetime.strptime(dataFormated, '%d/%m/%Y|%H:%M:%S')

            #dh_ObjectFormated -> data hora convertida da mensagem do robo
            #dataDeComparacao -> data e hora da ultima mensagem registrada
            if dataDeComparacao != None:
                self.lastDataHoraRegistered = datetime.strptime(dataDeComparacao, '%Y-%m-%d %H:%M:%S')

            if self.lastDataHoraRegistered == None or dh_ObjectFormated > self.lastDataHoraRegistered:
                mensagem['dataHora'] = f"{dh_ObjectFormated}"
                messagesToSend_compared.append(mensagem)
                convertDataToStringAgain = dh_ObjectFormated.strftime('%Y-%m-%d %H:%M:%S')
                self.lastMessagesDates[indicePregaoList] = convertDataToStringAgain

        return messagesToSend_compared

    def webscraping_execute(self):
        scraping_client = BBMNET_Scraping()
        credencialAtual_Entity = self.credencialBBMNET_Entity[0]

        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')

        navegador = webdriver.Chrome(options=chrome_options)
        navegador.implicitly_wait(10)
        scraping_client.loginToGuiaPage(navegador, credencialAtual_Entity)

        editaisEntitySize = len(self.editaisBBMNET_Entity)
        counter = 0

        while counter != (editaisEntitySize+1):
            if counter == editaisEntitySize:
                counter = 0

            print('Running')
            scraping_client.linkToHomePage(navegador)
            guiaPage_window_handles = navegador.window_handles

            editalAtual_Entity = self.editaisBBMNET_Entity[counter]
            navegador.switch_to.window(guiaPage_window_handles[1])

            scraping_client.setFiltrosPage(navegador, editalAtual_Entity)

            messagesList = scraping_client.findChatAba(navegador, editalAtual_Entity)

            navegador.close()
            navegador.switch_to.window(guiaPage_window_handles[0])
            messagesListInverted = messagesList[::-1]
            messagesToSend = self.compareDates(messagesListInverted, counter)
            self.websocket_client(messagesToSend, editalAtual_Entity, credencialAtual_Entity)
            counter += 1

if __name__ == '__main__':
    main = Main()
    main.pregoes_API_DATA()
    main.webscraping_execute()