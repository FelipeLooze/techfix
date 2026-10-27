import os
import re
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).with_name('.env'), encoding='utf-8-sig')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
STATUS = ['Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue']


def validar_cliente(nome, endereco, email, celular):
    nome, endereco = nome.strip(), endereco.strip()
    email, celular = email.strip().lower(), celular.strip()
    if not all([nome, endereco, email, celular]):
        raise ValueError('Preencha todos os dados do cliente.')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise ValueError('Informe um e-mail válido.')
    if not re.fullmatch(r'[0-9]{10,13}', celular):
        raise ValueError('O celular deve ter somente números, de 10 a 13 dígitos.')
    return {'nome': nome, 'endereco': endereco, 'email': email, 'celular_whatsapp': celular}


def validar_ordem(modelo, problema):
    if not modelo.strip() or not problema.strip():
        raise ValueError('Preencha o modelo do computador e o problema apresentado.')
    return {'modelo_computador': modelo.strip(), 'problema_relatado': problema.strip()}


def executar(consulta):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError('Configure SUPABASE_URL e SUPABASE_KEY no .env ou secrets.toml.')
    # Todo acesso ao banco passa por este tratamento de erros.
    try:
        banco = create_client(SUPABASE_URL, SUPABASE_KEY)
        return consulta(banco).execute().data
    except Exception as erro:
        codigo = str(getattr(erro, 'code', ''))
        if codigo == '23505':
            mensagem = 'Já existe um cliente com esse e-mail.'
        elif codigo == '23503':
            mensagem = 'Verifique o cliente vinculado. Clientes com OS não podem ser excluídos.'
        elif codigo in ('23514', '23502'):
            mensagem = 'Dados inválidos. Confira os campos obrigatórios, e-mail, celular e status.'
        else:
            mensagem = 'Não foi possível acessar o Supabase. Confira a conexão, as credenciais e o schema.sql.'
        raise RuntimeError(mensagem) from None


def listar(tabela, campos='*'):
    registros = []
    inicio = 0
    while True:
        pagina = executar(lambda banco: banco.table(tabela).select(campos)
                          .order('id').range(inicio, inicio + 499))
        registros.extend(pagina)
        if len(pagina) < 500:
            return registros
        inicio += 500


def consultar_ordens():
    registros = listar('ordens_servico', '*, clientes(nome,endereco,email,celular_whatsapp)')
    for registro in registros:
        cliente = registro.pop('clientes') or {}
        registro.update(cliente)
    return registros


def cadastrar_os(nome, endereco, email, celular, modelo, problema):
    cliente = validar_cliente(nome, endereco, email, celular)
    ordem = validar_ordem(modelo, problema)
    numero = executar(lambda banco: banco.rpc('cadastrar_os', {
        'p_nome': cliente['nome'], 'p_endereco': cliente['endereco'],
        'p_email': cliente['email'], 'p_celular': cliente['celular_whatsapp'],
        'p_modelo': ordem['modelo_computador'], 'p_problema': ordem['problema_relatado'],
    }))
    return numero


def editar_cliente(numero, nome, endereco, email, celular):
    dados = validar_cliente(nome, endereco, email, celular)
    resposta = executar(lambda banco: banco.table('clientes').update(dados).eq('id', numero))
    if not resposta:
        raise ValueError('Cliente não encontrado. Atualize o painel.')


def editar_os(numero, modelo, problema, status):
    dados = validar_ordem(modelo, problema)
    if status not in STATUS:
        raise ValueError('Selecione um status válido.')
    dados['status'] = status
    resposta = executar(lambda banco: banco.table('ordens_servico').update(dados).eq('id', numero))
    if not resposta:
        raise ValueError('OS não encontrada. Atualize o painel.')


def excluir_os(numero):
    resposta = executar(lambda banco: banco.table('ordens_servico').delete().eq('id', numero))
    if not resposta:
        raise ValueError('OS não encontrada. Atualize o painel.')


def excluir_cliente(numero):
    resposta = executar(lambda banco: banco.table('clientes').delete().eq('id', numero))
    if not resposta:
        raise ValueError('Cliente não encontrado. Atualize o painel.')
