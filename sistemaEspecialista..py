print ('Olá! Seja vem-vindo ao ajudante de identificação de vulnerabildade')

print ('Responda a avaliação a seguir e verifique o nível de criticidade do seu dispositivo IIoT')

contadorVulnerabilidade = 0

nivel = ""
resposta=""

#1. Credenciais padrão e senhas fracas
resposta = input("Senha padrão foi trocada?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

resposta = input("Há autorização baseada em funções para garantir que apenas dispositivos e usuários autorizados tenham acesso às redes IoT?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#2. Firmware desatualizado e falta de suporte
resposta = input("Dispositivo está atualizado com os patches de segurança mais recentes?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

resposta = input("Software utilizado está atualizado com os patches de segurança mais recentes?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#3. Falta de criptografia de dados
resposta = input("Há criptografia nos dados em trânsito?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

resposta = input("Há criptografia nos dados em repouso nos dados armazenados?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#4. APIs e interfaces inseguras
resposta = input("As APIs e interfaces conectadas, se houver, são de forncedores confiáveis?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#5. Falta de segmentação de rede
resposta = input("O dispositivo está isolado de sistemas críticos?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#6. Uso de protocolos inseguros
resposta = input("O fornecedor do protocolo é confiável?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

resposta = input("Há conformidade com regulamentações como LGPD, GDPR, Iot Cybersecurity Improvement Act, dentre outros?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#7. Falta de monitoramento e logging
resposta = input("Há alguma ferramenta de monitoramento das atividades do seu dispositivo?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#8. Credenciais embutidas no código (Hardcoded Credentials)
resposta = input("Há credenciais embutidas no código?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

resposta = input("Há dados sensíveis embutidos no código?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#9. Exposição desnecessária à internet
resposta = input("Seu dispositivo está desnecessariamente exposto na internet?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

#10. Vulnerabilidade a ataques DDoS
resposta = input("Há algum firewall de aplicação para mitigar ataques DDoS?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

resposta = input("Há limitação de taxa para mitigar ataques DDoS?")
if (resposta == "sim"):
    contadorVulnerabilidade +=1

print (contadorVulnerabilidade)
classificacao = ""

if (contadorVulnerabilidade == 0 and contadorVulnerabilidade == 0):
    classificacao = "baixo"
elif (contadorVulnerabilidade == 0 and contadorVulnerabilidade == 0):
    classificacao = "médio"
elif (contadorVulnerabilidade == 0 and contadorVulnerabilidade == 0):
    classificacao = "alto"
elif (contadorVulnerabilidade == 0 and contadorVulnerabilidade == 0):
    classificacao = "crítico"
