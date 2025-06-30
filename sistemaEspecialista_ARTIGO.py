print('Olá! Seja bem-vindo ao Sistema Especialista para Identificação de Vulnerabilidades IIoT')
print('Responda a avaliação a seguir e verifique o nível de criticidade do seu dispositivo IIoT\n')

# Dicionário com as perguntas
perguntas = {
    1: {
        'pergunta': "A senha padrão foi trocada?",
        'resposta_vulneravel': "nao"
    },
    2: {
        'pergunta': "O dispositivo está atualizado com os patches de segurança mais recentes?",
        'resposta_vulneravel': "nao"
    },
    3: {
        'pergunta': "Há criptografia nos dados em trânsito e nos dados armazenados?",
        'resposta_vulneravel': "nao"
    },
    4: {
        'pergunta': "Há alguma ferramenta de monitoramento das atividades do seu dispositivo?",
        'resposta_vulneravel': "nao"  
    },
    5: {
        'pergunta': "Há credenciais embutidas no código?",
        'resposta_vulneravel': "sim"
    },
    6: {
        'pergunta': "Seu dispositivo está desnecessariamente exposto na internet?",
        'resposta_vulneravel': "sim"
    }
}

contador_vulnerabilidade = 0

# Verifica resposta do usuário
def validar_resposta(resposta):
    return resposta.lower() in ['sim', 'nao', 'não']

# Força a resposder pergunta somente com sim/nao
for num, pergunta_data in perguntas.items():
    while True:
        resposta = input(f"{num}. {pergunta_data['pergunta']} (sim/nao): ").lower()
        if validar_resposta(resposta):
            break
        print("Por favor, responda apenas com 'sim' ou 'nao'.")
    
    if resposta == pergunta_data['resposta_vulneravel']:
        contador_vulnerabilidade += 1
        print("⚠️ Vulnerabilidade identificada!\n")

# Classificação de risco com pesos diferentes para cada vulnerabilidade
def classificar_risco(total_vulnerabilidades, total_perguntas):
    percentual = (total_vulnerabilidades / total_perguntas) * 100
    
    if percentual == 0:
        return "Baixo", "✅ Dispositivo seguro"
    elif percentual <= 30:
        return "Baixo", "ℹ️ Algumas melhorias recomendadas"
    elif percentual <= 60:
        return "Médio", "⚠️ Atenção necessária - risco moderado"
    elif percentual <= 80:
        return "Alto", "🔴 Ação imediata recomendada - risco elevado"
    else:
        return "Crítico", "❌ Risco extremo - medidas urgentes necessárias"

# Obter classificação
nivel_risco, recomendacao = classificar_risco(contador_vulnerabilidade, len(perguntas))

# Exibição dos resultados
print("\n" + "="*50)
print(f"\nTotal de vulnerabilidades identificadas: {contador_vulnerabilidade} de {len(perguntas)}")
print(f"Nível de risco: {nivel_risco}")
print(f"Recomendação: {recomendacao}")

# Sugestões de mitigação baseadas nas vulnerabilidades encontradas
if contador_vulnerabilidade > 0:
    print("\nSugestões de mitigação:")
    if contador_vulnerabilidade >= 3:
        print("- Considere realizar uma auditoria de segurança completa")
    print("- Atualize regularmente o firmware e software do dispositivo")
    print("- Implemente políticas de senhas fortes e autenticação multifator")
    print("- Restrinja o acesso à internet apenas quando necessário")
    print("- Implemente soluções de monitoramento contínuo")