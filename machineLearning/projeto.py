from openai import OpenAI
import re
import os

#Configura a chave de API da OpenAI
client = OpenAI(
    api_key = "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",
)

def continuarExec():
    """
    Pergunta ao usuário se deseja continuar e retorna o chatbot se a resposta for 'S', caso contrário, se despede e encerra.
    """
    print("\nDeseja continuar? (S/N)")
    continuar = input().strip().upper()
    if continuar == 'S':
        chatbot()
    else:
        print("Encerrando o chat. Até mais!")

def lerArquivo(nome_arquivo, pasta=None):
    """
    Lê o conteúdo de um arquivo de texto txt presente em uma pasta.

    Args:
        nome_arquivo (str): O nome do arquivo a ser lido.
        pasta (str, opcional): A pasta onde o arquivo está localizado. Se não for fornecido, usa a pasta atual.

    Returns:
        str: O conteúdo do arquivo.
    """
    try:
        #Se um diretório for fornecido, combina o diretório com o nome do arquivo
        if pasta:
            caminho_arquivo = os.path.join(pasta, nome_arquivo)
        else:
            caminho_arquivo = nome_arquivo

        #Verifica se o arquivo existe no caminho especificado
        if os.path.isfile(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8') as file:
                conteudo = file.read()
            return conteudo
        #Se o arquivo não for encontrado, exibe uma mensagem de erro
        else:
            print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
            return None
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

def particionaTexto(texto, maximoPalavras=1300):
    """
    Divide o texto em partes com no máximo `maximoPalavras` palavras cada,
    garantindo que cada corte seja feito no final de uma sentença.

    Args:
        texto (str): O texto a ser dividido.
        maximoPalavras (int): Número máximo de palavras por parte.

    Returns:
        list: Uma lista contendo as partes do texto.
    """
    #Verifica as pontuações pra um melhor cortes de sentenças
    sentencas = re.split(r'(?<=[.!?])\s+', texto)
    partes = []
    parteAtual = ""
    contadorPalavras = 0

    for sentenca in sentencas:
        #Divide a sentença em palavras e conta o número de palavras
        palavrasSentenca = sentenca.split()
        numeroPalavras = len(palavrasSentenca)

        #Se a parte atual mais o número de palavras da sentença não exceder o limite,
        if contadorPalavras + numeroPalavras <= maximoPalavras:
            #Adiciona a sentença à parte atual e incrementa o contador de palavras
            parteAtual += sentenca + " "
            contadorPalavras += numeroPalavras
        #Se exceder o limite,
        else:
            #Adiciona a parte atual à lista de partes
            if parteAtual:
                partes.append(parteAtual.strip())
            parteAtual = sentenca + " "
            contadorPalavras = numeroPalavras

    #Adiciona a última parte do texto à lista de partes
    if parteAtual:
        partes.append(parteAtual.strip())

    return partes

def resumeTextoGrande(texto):
    """
    Resumo de texto grande, dividindo em partes menores para evitar estouro de tokens.

    """
    #Divide o texto em partes menores usando a função divideEmPartes, cada uma com no máximo 1300 palavras
    divideEmPartes = particionaTexto(texto, maximoPalavras=1300)

    #Itera sobre cada parte dividida do texto e envia para ser feito o resumo
    for idx, parte in enumerate(divideEmPartes, 1):
        #Isso aqui é para aparência, que aparece "Parte 1:", "Parte 2:", etc da divisão do texto grande
        #print(f"Parte {idx}:")
        #Envia o texto para ser resumido usando a API da OpenAI
        resposta = client.chat.completions.create(
        #Modelo de linguagem GPT-4o-mini
        model="gpt-4o-mini-2024-07-18",
        #Mensagens de sistema e do usuário. Sistema informa o propósito do assistente e o usuário fornece o texto a ser resumido
        messages=[
            {"role": "system", "content": "Você é um assistente útil que resume textos. Mantenha o texto pessoal e não use frases como 'o autor diz'."},
            {"role": "user", "content": f"Resuma o seguinte texto mantendo o estilo pessoal: {parte}"}
        ],
        #Número máximo de tokens para a resposta
        max_tokens=1800
        )
        #Extrai o texto resumido da resposta
        textoResumido = resposta.choices[0].message.content
        print(f"{textoResumido}\n")


def resumidor():
    """
    Processa e resume o texto, dividindo em blocos menores para evitar
    estouro de limites de tokens e reagrupando os resumos de uma forma coesa.

    A função permite duas formas de entrada:
    1. Texto inserido diretamente no prompt (até 550 palavras).
    2. Texto lido a partir de um arquivo (para textos maiores que 550 palavras).

    Retorna:
        None: A função imprime o resumo ou mensagens de erro diretamente.

    Exceções:
        Trata exceções gerais e exibe mensagens de erro apropriadas.

    Passos:
        1. Solicita ao usuário que escolha o método de entrada do texto.
        2. Se a escolha for inserir o texto diretamente no prompt:
            a. Solicita ao usuário que insira o texto.
            b. Verifica se o texto tem até 550 palavras.
            c. Envia o texto para a API da OpenAI para resumir.
            d. Imprime o resumo gerado.
        3. Se a escolha for processar o texto a partir de um arquivo:
            a. Solicita ao usuário que insira o nome do arquivo em txt.
            b. Lê o conteúdo do arquivo usando a função `lerArquivo`.
            c. Se o conteúdo for lido com sucesso, envia para ser resumido.
        4. Trata opções inválidas e exibe mensagens de erro apropriadas.
    """
    try:
        print("A sumarização pode ocorrer de duas formas:")
        print("1. Até 550 caracteres é possível sumarizar o texto enviado por imput do prompt.")
        print("2. Acima de 500 caracteres, o texto será processado a partir de arquivos.")
        print("Isso ocorre para evitar erro de armazenamento de String via imput do prompt.")

        escolha = input("Digite o número correspondente: ").strip()

        #Se a escolha for 1, o usuário pode inserir o texto diretamente no prompt com até 550 palavras
        if escolha == "1":
            texto = input("Digite o texto de até 550 palavras: ")
            comprimento = len(texto.split())
            if comprimento <= 550:
                #Envia o texto para ser resumido usando a API da OpenAI
                resposta = client.chat.completions.create(
                    #Modelo de linguagem GPT-4o-mini
                    model="gpt-4o-mini-2024-07-18",
                    #Mensagens de sistema e do usuário. Sistema informa o propósito do assistente e o usuário fornece o texto a ser resumido
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil que resume textos. Mantenha o texto pessoal e não use frases como 'o autor diz'."},
                        {"role": "user", "content": f"Resuma o seguinte texto mantendo o estilo pessoal: {texto}"}
                    ],
                    #Número máximo de tokens para a resposta
                    max_tokens=1800
                )
                #Extrai o texto resumido da resposta
                textoResumido = resposta.choices[0].message.content
                print("\n\nResumo do texto:")
                print(textoResumido)
            else:
                print(f"\nErro: O texto excede os 550 caracteres.")
                print(f"Falha em gerar um resumo.")
                
        #Se a escolha for 2, o usuário pode inserir o nome do arquivo dentro da pasta "Texto" para processar o texto
        elif escolha == "2":
            print('O texto será processado a partir do arquivo localizado dentro da pasta "Texto".')
            arquivo = input('Por favor, insira o nome do arquivo com a extensão .txt: ')
            #Lê o conteúdo do arquivo usando a função lerArquivo
            conteudo = lerArquivo(arquivo, pasta='Texto')
            #Se o conteúdo do arquivo for lido com sucesso, envia para ser resumido
            if conteudo:
                resumeTextoGrande(conteudo)
        else:
            print("Opção inválida. Por favor, tente novamente.")
            print(f"Falha em gerar um resumo.")

    except Exception as e:
        print("Erro ao processar os resumos:", e)
        print(f"Falha em gerar um resumo.")


def tradutor():
    """
    Traduz o texto entre idiomas com base na escolha do usuário.

    O usuário pode escolher entre traduzir de Português para Inglês, de Inglês para Português,
    ou inserir manualmente os idiomas de origem e destino. A função solicita o texto a ser traduzido
    e utiliza a API da OpenAI para realizar a tradução.

    Retorna:
        str: O texto traduzido, ou None se ocorrer um erro ou se a opção for inválida.

    Exceções:
        Trata exceções gerais e exibe mensagens de erro.

    Passos:
        1. Solicita ao usuário que selecione o idioma de origem.
        2. Define os idiomas de origem e destino com base na escolha do usuário.
        3. Solicita ao usuário que insira o texto a ser traduzido.
        4. Configura o prompt para a tradução.
        5. Envia o prompt para a API da OpenAI e obtém a tradução.
        6. Retorna o texto traduzido.
    """
    try:
        print("Selecione o idioma de origem:")
        print("1. De Português para Inglês")
        print("2. De Inglês para Português")
        print("3. Inserir manualmente o idioma (nome ou código)")

        escolha = input("Digite o número correspondente ou o nome do idioma: ").strip().lower()

        if escolha == "1":
            idiomaOrigem = "português"
            idiomaDestino = "inglês"
        elif escolha == "2":
            idiomaOrigem = "inglês"
            idiomaDestino = "português"
        elif escolha == "3":
            idiomaOrigem = input("Digite o nome do idioma de origem (ex: 'italiano', 'es', 'francês'): ").strip().lower()
            idiomaDestino = input("Digite o nome do idioma de destino (ex: 'italiano', 'es', 'francês'): ").strip().lower()
        else:
            print("Opção inválida. Por favor, tente novamente.")
            return None

        texto = input(f"Digite o texto para traduzir do {idiomaOrigem} para o {idiomaDestino}: ")

        #Configurando o prompt para a tradução
        mensagemSistema = f"Você é um assistente útil que traduz textos do {idiomaOrigem} para o {idiomaDestino}. Responda em português, exceto pela tradução, caso venha a informar algo a mais."
        promptUsuario = f"Traduza o seguinte texto do {idiomaOrigem} para o {idiomaDestino}:\n{texto}"

        #Envia o texto para ser traduzido usando a API da OpenAI
        resposta = client.chat.completions.create(
            #Modelo de linguagem GPT-4o-mini
            model="gpt-4o-mini-2024-07-18",
            #Mensagens de sistema e do usuário. Sistema informa o propósito do assistente e o usuário fornece o texto a ser traduzido
            messages=[
                {"role": "system", "content": mensagemSistema},
                {"role": "user", "content": promptUsuario}
            ],
            #Número máximo de tokens para a resposta
            max_tokens=1500
        )

        #Extrai o texto traduzido da resposta
        textoTraduzido = resposta.choices[0].message.content
        return textoTraduzido

    except AttributeError as e:
        print("Erro: Problema na estrutura retornada pela API:", e)
        return None
    except Exception as e:
        print("Erro inesperado:", e)
        return None


def geradorCodigo(texto):
    """
    Gera código com base no prompt fornecido, utilizando a API da OpenAI.

    Args:
        prompt (str): O prompt para a geração do código.

    Returns:
        str: O código gerado pela API.
    """
    try:
        #Envia o texto para ser codificado usando a API da OpenAI
        resposta = client.chat.completions.create(
            #Modelo de linguagem GPT-4o-mini
            model="gpt-4o-mini-2024-07-18",
            #Mensagens de sistema e do usuário. Sistema informa o propósito do assistente e o usuário fornece o texto a ser convertido em código de programação
            messages=[
                {"role": "system", "content": "Você é um assistente que gera código. Forneça apenas o código solicitado, de forma completa e sem explicações."},
                {"role": "user", "content": texto}
            ],
            #Número máximo de tokens para a resposta
            max_tokens=2500,
            #Temperature é um recurso que dita a criatividade do modelo, quanto mais próximo de 0, mais conservador/preciso o modelo é
            #Quanto mais próximo de 1, mais criativo ele é
            #Quando mais conservador, maiores a chances de gerar respostas repetitivas, contudo mais precisas
            temperature=0.2
        )
        #Extrai o código da resposta
        codigo = resposta.choices[0].message.content.lstrip()
        return codigo

    except Exception as e:
        print(f"Erro ao gerar código: {e}")
        return None


def GeradorImagem(texto):
    """
    Gera uma imagem baseada no prompt fornecido utilizando a API do DALL·E 2.

    Args:
        texto (str): O texto descritivo para a geração da imagem.

    Returns:
        str: URL da imagem gerada ou mensagem de erro.
    """
    try:
        #Envia o texto para ser transformado em imagem usando a API da OpenAI
        resposta = client.images.generate(
            #Modelo de imagem DALL·E 2
            model="dall-e-2",
            #Texto descritivo para a geração da imagem
            prompt=texto,
            #Tamanho da imagem
            size="1024x1024",
            #Número de imagens a serem geradas
            n=1,
            )

        #Extrai a URL da imagem gerada
        urlImagem = resposta.data[0].url
        return urlImagem
    except Exception as e:
        print(f"Erro ao gerar imagem: {e}")
        return None


#Função principal do ChatBot
def chatbot():
    print("Escolha uma opção: \n1. Traduzir Texto\n2. Sumarizar Texto\n3. Gerar Código\n4. Gerar Imagem\n5. Sair")
    
    escolha = input("Digite o número da opção desejada: ")
    
    if escolha == '1':
        traducao = tradutor()
        print("Tradução:", traducao if traducao else "Falha na tradução.")
        #Pergunta se deseja continuar
        continuarExec()
    
    elif escolha == '2':
        resumidor()
        continuarExec()
    
    elif escolha == '3':
        texto = input("Digite o prompt para gerar código: ")
        codigo = geradorCodigo(texto)
        print("Código Gerado:\n", codigo)
        continuarExec()
    
    elif escolha == '4':
        texto = input("Digite a descrição da imagem: ")
        urlImagem = GeradorImagem(texto)
        if urlImagem:
            print("Imagem Gerada. Acesse o URL para visualizar:", urlImagem)
        else:
            print("Erro ao gerar a imagem. Tente novamente.")
        continuarExec()
    
    elif escolha == '5':
        print("Encerrando o ChatBot. Até mais!")
    
    else:
        print("Opção inválida. Tente novamente.")
        chatbot()


#Inicia o chatbot
chatbot()
