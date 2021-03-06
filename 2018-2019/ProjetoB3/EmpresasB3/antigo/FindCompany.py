from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import html
import requests
import time
import random
import json
import re
import mongoConnect

def mongoConection():
    conexão, mydb = mongoConnect.connect()
    cursor = mydb['empresas_link_b3']
    return cursor

def TirarRepetidosMongo():
    cursor = mongoConection()
    array= []
    arrayTratado = []
    for content in cursor.find():
        array.append(content['link_b3_empresa']) 
    for i in range(0,len(array)):
        if array[i] == (array[i-1]):
            pass
        else:
            arrayTratado.append(array[i])
    return list(arrayTratado)

def findAllCompanies():
    # driver.get('http://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/empresas-listadas.htm')
    conexão, mydb = mongoConnect.connect()
    cursor = mydb['empresas_link_b3']
    arrayLinks = []
    arrayEmpresas = []
    subXpath= ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','X','Z','5']
    for i in range(0,len(subXpath)):
        url = requests.get('http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/BuscaEmpresaListada.aspx?Letra='+str(subXpath[i])+'&idioma=pt-br')        
        pageContent = BeautifulSoup(url.content, 'lxml')
        for tagA in pageContent.find_all('a', href=True):
            nomeEmpresa = (tagA.text)
            LinkEmpresa = (tagA['href'])
            if not 'http://www.b3.com.br/' in LinkEmpresa:
                arrayLinks.append(LinkEmpresa)
                arrayEmpresas.append(nomeEmpresa)
                print(tagA['href'] + ' ; '+tagA.text)
        
    for insert in range(0,len(arrayLinks)):
        print('Inseridos banco: '+str(insert+1))
        mydb.empresas_link_b3.insert_one({
            "nome_empresa": arrayEmpresas[insert] , "link_b3_empresa": arrayLinks[insert]
        })

# linkBase na segunda pesquisa = http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/
def find_details_in_all_companies():
    url = ('http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/')
    conexão, mydb = mongoConnect.connect()
    cursor = mydb['empresas_link_b3']
    
    ConcLinks = TirarRepetidosMongo()
    for i in range(0, len(ConcLinks)):
        linkSplit = (ConcLinks[i])
        link = linkSplit.split('=')
        codigo = (link[1])
        ArrayTDs = []
        url = requests.get('http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp?CodCVM='+str(codigo)+'&ViewDoc=1&AnoDoc=2019&VersaoDoc=1&NumSeqDoc=80335')
        pageContent = BeautifulSoup(url.content, 'lxml')                                  
        for tbody in pageContent.findAll('div',{'class':'content active'}):
            arrayCodBolsa = []
            for codigoBolsa in tbody.findAll('a'):
                conteudoCodigo = (codigoBolsa.text)
                conteudoCodigo = conteudoCodigo.split('\\n')
                arrayCodBolsa.append(conteudoCodigo)
            
            print('Códigos de Negociação: %s'%(arrayCodBolsa[1]))
            for td in tbody.findAll('td'):
                td = (td.text)
                try:
                    ArrayTDs.append(td)
                except:
                    print('Erro no append')
                    ArrayTDs.append('False')

        pInfos = [1, 5,11]
        for i in range(0,len(pInfos)):
            
            arrayNomePregao = []
            arrayCNPJ = []
            arraySite = []
            
            if i == 0:
                nome = (ArrayTDs[pInfos[i]])
                print('Nome de Pregão: %s'%nome)
                if nome:
                    arrayNomePregao.append(nome)
                else:
                    arrayNomePregao.append('False')

            elif i == 1:
                CNPJ = (ArrayTDs[pInfos[i]])
                print('CNPJ: %s'% CNPJ)
                if CNPJ:
                    arrayCNPJ.append(CNPJ)
                else:
                    arrayCNPJ.append('False')

            elif i == 2:
                site = (ArrayTDs[pInfos[i]])
                print('Site: %s'% site)
                if site:
                    arraySite.append(site)
                else:
                    arraySite.append('False')
        
        for x in range(0,len(arrayCNPJ)):
            conc = str(arrayNomePregao[x])+' ; '+str(arrayCNPJ[x])+' ; '+str(arraySite[x])+' ; '+str(arrayCodBolsa[x])
            print(conc)
        print('+===========')  
                
find_details_in_all_companies()
# TirarRepetidosMongo()

