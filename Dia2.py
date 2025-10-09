"""
Intermediário:

Gestor de empréstimo de equipamento de TI
Crie um sistema para gerenciar um empréstimo de equipamento da faculdade

o sistema deve cadastrar 
    equipamento, 
    alunos, 
    data de empréstimo,
    devolução (pegar detalhes)

impedir empréstimo de alunos que tenham pendências (quando não devolveu o equipamento dentro da data de devolução)

gerar relatório dos empréstimos ativos
listar empréstimos ativos

deve salvar em txt o json
"""

from datetime import datetime, timedelta
from json import dump, load, JSONDecodeError
from re import compile, findall, sub

padrao_status_pendencia = compile(r"\bSTATUS_PENDENCIA: \w*")
padrao_email = compile(r"\w*\@\w*\.\w*")

def gerar_log(nome, email):
    with open("log_emprestimos_ativos.txt", "a", encoding="UTF-8") as file:
        file.write(f"{nome} | '{email}' - STATUS_PENDENCIA: True\n")






def aluno_cadastrado(email):
    cadastrado = False
    email_cadastrado = ""

    with open("log_emprestimos_ativos.txt", "r") as file:
        for linha in file:
            email_cadastrado = ''.join(padrao_email.findall(linha)) # Verificando se o email já está no json (há uma conversão pra str com o .join)
            if email == email_cadastrado:
                cadastrado = True
                return cadastrado
            else:
                cadastrado = False

    return cadastrado
      






def cadastrar_aluno(lista_temp):
    """
        Cadastra novos alunos e seu equipamento

        recebe: lista_temp -> uma lista temporária que veio de menu() e será passada pra função database()
    """

    aluno = dict()

    # Coletando dados
    nome = input("→ Digite o nome do aluno: ").strip()
    email = input("→ Digite o email do aluno: ").strip()

    if not aluno_cadastrado(email):
        
        equipamento = input("→ Digite o nome do equipamento: ").strip()
        data_emprestimo = input("→ Digite a data de empréstimo (dd/mm/aaaa): ").strip()
        data_emprestimo = datetime.strptime(data_emprestimo, "%d/%m/%Y")
        data_devolucao = data_emprestimo + timedelta(days=30) # Calculando 30 dias de empréstimo
        data_devolucao = datetime.strftime(data_devolucao, "%d/%m/%Y")
        data_emprestimo = datetime.strftime(data_emprestimo, "%d/%m/%Y")
        # Gerando logs
        gerar_log(nome, email)

        aluno["nome"] = nome.capitalize()
        aluno["email"] = email.lower()
        aluno["equipamento"] = equipamento.capitalize()
        aluno["data_emprestimo"] = data_emprestimo
        aluno["data_devolucao"] = data_devolucao
        aluno["pendencia"] = True

        database(aluno, lista_temp)
    else:
        print(f"\n{email} já está cadastrado no sistema. Use a opção número 2\n")
        menu()





def database(aluno, lista_temp):

    try:
        with open("bd.json", "r") as file_r:
            dados_temp = load(file_r)
            if isinstance(dados_temp, dict): # Se for um dict no json
                lista_temp.append(dados_temp)
                lista_temp.append(aluno)
                # Gravando o lista_temp no json com o aluno novo que veio de cadastrar_aluno()
                with open("bd.json", "w", encoding="UTF-8") as file_w:
                    dump(lista_temp, file_w, indent=2)

     
            elif isinstance(dados_temp, list): # Se for uma lista de dict no json
                dados_temp.append(aluno)
                with open("bd.json", "w", encoding="UTF-8") as file_w:
                    dump(dados_temp, file_w, indent=2)

        
            print("===TRY===")
    except:
         with open("bd.json", "w", encoding="UTF-8") as file_w:
            dump(aluno, file_w, indent=2)
            print("===EXCEPT===")
    



def ver_relatorio():
    with open("log_emprestimos_ativos.txt", "r") as file:
        for linha in file:
            status = ''.join(padrao_status_pendencia.findall(linha))
            if status == "STATUS_PENDENCIA: True":
                print(linha)





def pendencias(email):
    status = False

    with open("log_emprestimos_ativos.txt", "r") as file:
        for linha in file:
            email_na_linha = ''.join(padrao_email.findall(linha))
            if email_na_linha == email:
                status_pendencia = ''.join(padrao_status_pendencia.findall(linha))
                if status_pendencia == 'STATUS_PENDENCIA: True':
                    print(f'{email}: Tem pendência\n')
                    status = True
                else:
                    print(f"✅ {email}: Não tem pendência\n")
    return status



def fazer_emprestimo():
    lista_temp = list()
    email = input("\nDigite o email do aluno: →  ").strip()
    if aluno_cadastrado(email) and not pendencias(email):
        print(f"✅ {email} pode pegar outro equipamento")
    else:
        print(f"❌ {email} não pode pegar outro equipamento antes de fazer devolução")
        





def devolver_equip():
    lista_temp = list()
    alunos_cadastrados = ""

    email = input("Digite o email do aluno: ").strip()
    if aluno_cadastrado(email): # Se o aluno estiver cadastrado
    
        try:
            with open("bd.json", "r") as file:
                # Quando só há uma pessoa no bd.json, o programa lê apenas 1 dicionário
                alunos_cadastrados = load(file)
                if alunos_cadastrados["email"] == email:
                    alunos_cadastrados["pendencia"] = False
                    lista_temp = alunos_cadastrados
                    print(lista_temp)  
            with open("bd.json", "w", encoding="UTF-8") as file_w:
                dump(lista_temp, file_w, indent=2)
                print(f"\n✅ Email: {email} está sem pendências no sistema")

        except: # Se houver uma lista de dicionários no bd.json (mais de uma pessoa) 
            with open("bd.json", "r") as file:
                alunos_cadastrados = load(file) # [{...},{...}]
       
                for dict in alunos_cadastrados:
                    if dict["email"] == email:
                        dict["pendencia"] = False
                        lista_temp.append(dict)
                    else:
                        lista_temp.append(dict)        

            with open("bd.json", "w", encoding="UTF-8") as file_w:
                dump(lista_temp, file_w, indent=2)
                print(f"\n✅ Email: {email} está sem pendências no sistema")

        novo_log = list()
        # Tirando O STATUS pendente do log
        with open("log_emprestimos_ativos.txt", "r") as file:
            for linha in file:
                email_na_linha = ''.join(padrao_email.findall(linha))
                if email_na_linha == email:
                    linha = sub(padrao_status_pendencia, "STATUS_PENDENCIA: False", linha)
                    novo_log.append(linha)
                else:
                    novo_log.append(linha)

        with open("log_emprestimos_ativos.txt", "w", encoding="UTF-8") as file:
            for item in novo_log:
                file.write(item)
               


                
    else: # Se o aluno não estiver cadastrado
        resposta = ""
        while resposta != 'S' or resposta != 'N':
            resposta = input("\nEsse email ainda não está no sistema, gostaria de voltar para o menu e fazer um empréstimo? (S/N)\n→  ")
            if resposta.upper() == 'S':
                menu()
                break
            elif resposta.upper() == 'N':
                break
            else:
                print("\n⚠️  ERRO: Responda com 'S' ou 'N'")




def menu():
    lista_temp = list()

    print("=== SISTEMA DE EMPRÉSTIMO DE EQUIPAMENTOS ===")
    print("1. Cadastrar aluno")
    print("2. Fazer empréstimo")
    print("3. Ver relatório de empréstimos ativos")
    print("4. Devolver equipamento")
    print("5. Sair do sistema")
    
    resposta = input("\n→  ")

    if resposta == '1':
        cadastrar_aluno(lista_temp)
    elif resposta == '2':
        fazer_emprestimo()
    elif resposta == '3':
        ver_relatorio()
    elif resposta == '4':
        devolver_equip()
    elif resposta == '5':
        print("Encerrando...")
    else:
        print("Opção inválida")
        menu()



if __name__ == "__main__":
    menu()
