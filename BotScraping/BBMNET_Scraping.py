from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


class BBMNET_Scraping:

    def loginToGuiaPage(self, navegador, credencialAtual_Entity):
        LoginBBMNET_LINK = "https://bbmnet-cad-participantes-prd.rj.r.appspot.com/auth/realms/BBM/protocol/openid-connect/auth?client_id=cadastro-participantes-admin-site&redirect_uri=https%3A%2F%2Fsistema.novobbmnet.com.br%2Fcontroller&state=28ad03e6-7082-477a-8657-5650393d197b&response_mode=fragment&response_type=code&scope=openid&nonce=7ecd6732-027c-4465-8491-488369960fd1"

        navegador.get(LoginBBMNET_LINK)
        navegador.maximize_window()

        navegador.find_element('xpath', '/html/body/div/div[2]/div/div/div/div/form/div[1]/input').send_keys(credencialAtual_Entity.usuario)
        navegador.find_element('xpath', '/html/body/div/div[2]/div/div/div/div/form/div[2]/input').send_keys(credencialAtual_Entity.senha)
        navegador.find_element('xpath', '/html/body/div/div[2]/div/div/div/div/form/div[4]/input[2]').click()

    def linkToHomePage(self, navegador):
        navegador.execute_script("window.open('https://sala.novobbmnet.com.br/controller/9c73820f-0700-477b-b151-bbb7d9fcbe27?modalidade=3', '_blank');")

    def setFiltrosPage(self, navegador, editalAtual_Entity):
        tempo_espera = 10
        print('Pregão: ', editalAtual_Entity)
        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/nb-card-header/div/button"))).click()
        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/nb-accordion/nb-accordion-item/nb-accordion-item-body/div/div/form/div[2]/div[1]/nb-form-field/div/input"))).send_keys(editalAtual_Entity.orgao)
        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[2]/div/div/nb-option-list/ul/nb-option"))).click()

        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/nb-accordion/nb-accordion-item/nb-accordion-item-body/div/div/form/div[2]/div[2]/nb-form-field/div/input"))).send_keys(editalAtual_Entity.chaveEdital)
        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[2]/div/div/nb-option-list/ul/nb-option"))).click()

        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/nb-accordion/nb-accordion-item/nb-accordion-item-body/div/div/form/div[2]/div[3]/nb-form-field/div/input"))).send_keys(editalAtual_Entity.lote)
        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/nb-accordion/nb-accordion-item/nb-accordion-item-body/div/div/form/div[3]/div[1]/nb-form-field/div[2]/nb-select/button"))).click()
        WebDriverWait(navegador, tempo_espera).until(EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/nb-accordion/nb-accordion-item/nb-accordion-item-body/div/div/form/div[4]/div/button[2]"))).click()

    def findChatAba(self, navegador, editalAtual_Entity):
        tempo_espera = 10
        time.sleep(3)
        repeticoes = 1

        while repeticoes < 13:
            if repeticoes == 11:
                WebDriverWait(navegador, tempo_espera).until(
                    EC.presence_of_element_located((By.XPATH,f"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/div/nb-card-body/nb-tabset/ul/li[{12}]/a"))
                ).click()
                time.sleep(0.5)
                soup = BeautifulSoup(navegador.page_source, 'html.parser')
                time.sleep(0.5)
                class_name = "clickable"
                element = soup.find(class_=class_name)
                if element is not None:
                    WebDriverWait(navegador, tempo_espera).until(
                        EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/ngx-lista-itens/div[2]/div[2]/div"))
                    ).click()
                    time.sleep(2)
                    site = BeautifulSoup(navegador.page_source, 'html.parser')
                    time.sleep(0.5)
                    mensagens = site.find_all("span",
                                              class_=["chat_date", "chat_msg", "chat_perfil", "chat_perfil_Autoridade",
                                                      "chat_perfil_sistema"])
                    minha_lista = []
                    conjunto_atual = {}  # Dicionário para armazenar as informações do conjunto atual

                    for i, mensagem in enumerate(mensagens):
                        informacao = mensagem.text

                        if "chat_date" in mensagem["class"]:
                            conjunto_atual["dataHora"] = informacao
                        elif "chat_msg" in mensagem["class"]:
                            conjunto_atual["conteudo"] = informacao
                        elif any(c in mensagem["class"] for c in
                                 ["chat_perfil", "chat_perfil_Autoridade", "chat_perfil_sistema"]):
                            conjunto_atual["origem"] = informacao

                        conjunto_atual["idEdital"] = editalAtual_Entity.id

                        if (i + 1) % 3 == 0:
                            minha_lista.append(conjunto_atual)
                            conjunto_atual = {}  # Reinicia o dicionário para o próximo conjunto

                    return minha_lista
                repeticoes = 12
            if repeticoes == 12:
                WebDriverWait(navegador, tempo_espera).until(
                    EC.presence_of_element_located((By.XPATH,f"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/div/nb-card-body/nb-tabset/ul/li[{11}]/a"))
                ).click()
                time.sleep(0.5)
                soup = BeautifulSoup(navegador.page_source, 'html.parser')
                time.sleep(0.5)
                class_name = "clickable"
                element = soup.find(class_=class_name)
                if element is not None:
                    WebDriverWait(navegador, tempo_espera).until(
                        EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/ngx-lista-itens/div[2]/div[2]/div"))
                    ).click()
                    time.sleep(2)
                    site = BeautifulSoup(navegador.page_source, 'html.parser')
                    time.sleep(0.5)
                    mensagens = site.find_all("span",
                                              class_=["chat_date", "chat_msg", "chat_perfil", "chat_perfil_Autoridade",
                                                      "chat_perfil_sistema"])
                    minha_lista = []
                    conjunto_atual = {}  # Dicionário para armazenar as informações do conjunto atual

                    for i, mensagem in enumerate(mensagens):
                        informacao = mensagem.text

                        if "chat_date" in mensagem["class"]:
                            conjunto_atual["dataHora"] = informacao
                        elif "chat_msg" in mensagem["class"]:
                            conjunto_atual["conteudo"] = informacao
                        elif any(c in mensagem["class"] for c in
                                 ["chat_perfil", "chat_perfil_Autoridade", "chat_perfil_sistema"]):
                            conjunto_atual["origem"] = informacao

                        conjunto_atual["idEdital"] = editalAtual_Entity.id

                        if (i + 1) % 3 == 0:
                            minha_lista.append(conjunto_atual)
                            conjunto_atual = {}  # Reinicia o dicionário para o próximo conjunto

                    return minha_lista
                repeticoes += 1
            if repeticoes != 11 and 12:
                WebDriverWait(navegador, tempo_espera).until(
                    EC.presence_of_element_located((By.XPATH,f"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/div/nb-card-body/nb-tabset/ul/li[{repeticoes}]/a"))
                ).click()

                # navegador.find_element('xpath','/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/div/div/nb-card-body/nb-tabset/ul/li[1]/a').click()
                time.sleep(0.5)
                soup = BeautifulSoup(navegador.page_source, 'html.parser')
                time.sleep(0.5)
                class_name = "clickable"
                element = soup.find(class_=class_name)
                if element is not None:
                    WebDriverWait(navegador, tempo_espera).until(
                        EC.presence_of_element_located((By.XPATH,"/html/body/app-root/ngx-sala-disputa/ngx-sala-disputa-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/ngx-home/div[2]/div/nb-card/ngx-lista-itens/div[2]/div[2]/div"))
                    ).click()
                    time.sleep(2)
                    site = BeautifulSoup(navegador.page_source, 'html.parser')
                    time.sleep(0.5)
                    mensagens = site.find_all("span",
                                              class_=["chat_date", "chat_msg", "chat_perfil", "chat_perfil_Autoridade",
                                                      "chat_perfil_sistema"])
                    minha_lista = []
                    conjunto_atual = {}  # Dicionário para armazenar as informações do conjunto atual

                    for i, mensagem in enumerate(mensagens):
                        informacao = mensagem.text

                        if "chat_date" in mensagem["class"]:
                            conjunto_atual["dataHora"] = informacao
                        elif "chat_msg" in mensagem["class"]:
                            conjunto_atual["conteudo"] = informacao
                        elif any(c in mensagem["class"] for c in
                                 ["chat_perfil", "chat_perfil_Autoridade", "chat_perfil_sistema"]):
                            conjunto_atual["origem"] = informacao

                        conjunto_atual["idEdital"] = editalAtual_Entity.id

                        if (i + 1) % 3 == 0:
                            minha_lista.append(conjunto_atual)
                            conjunto_atual = {}  # Reinicia o dicionário para o próximo conjunto

                    return minha_lista
                repeticoes += 1