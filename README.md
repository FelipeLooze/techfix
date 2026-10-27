# TechFix Informática

Sistema de ordens de serviço com Gradio, Streamlit e Supabase.
Use somente dados fictícios.

## 1. Banco

Crie um projeto gratuito no Supabase e conecte o repositório GitHub da TechFix.
Na integração, use a branch main e Working directory `.`.
A migração em `supabase/migrations/` cria as tabelas e funções.

O arquivo `sql/schema.sql` contém o mesmo SQL exigido na entrega.
Se preferir usar o SQL Editor, execute esse arquivo uma vez e não aplique a migração novamente.
O e-mail é salvo em letras minúsculas. Um cliente pode ter várias OS.
Clientes com OS vinculadas não podem ser excluídos antes das ordens.

## 2. Configuração

Na pasta do projeto:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha o arquivo `.env` localmente:

```text
SUPABASE_URL=URL do projeto
SUPABASE_KEY=chave service_role do projeto
```

No Supabase, a URL fica em Connect ou nas configurações de Data API.
A chave service_role fica em Settings > API Keys > Legacy API Keys.
Ela é usada apenas pelo servidor Python, com as tabelas protegidas por RLS.
Não compartilhe a chave nem envie o .env ao GitHub.

Para usar secrets.toml, copie `.streamlit/secrets.toml.example` para
`.streamlit/secrets.toml` e preencha as mesmas variáveis.
O Streamlit aceita secrets.toml ou .env; o Gradio usa .env ou variáveis de ambiente.
Use Python 3.12 e execute os comandos a partir desta pasta.

## 3. Gradio

```powershell
python app_gradio.py
```

Abra o endereço exibido no terminal. O share=True também gera um link temporário
para testar no celular. Se a porta 7860 estiver ocupada:

```powershell
$env:GRADIO_SERVER_PORT=7862
python app_gradio.py
```

Preencha os seis campos e clique em Cadastrar. O e-mail existente reaproveita o cliente,
sem alterar seus dados; o gerente pode corrigi-los no painel. Toda nova OS começa como Aberto.
O botão Limpar esvazia os campos.

## 4. Streamlit

Em outro terminal:

```powershell
python -m streamlit run app_streamlit.py --server.port=8502
```

- Consultar: tabela, filtros por nome, e-mail e status, e exportação CSV.
- Cadastrar: nova OS, com a mesma regra de reaproveitamento de cliente.
- Editar/Excluir: altera a OS e os dados do cliente; exclusões exigem confirmação.
- Indicadores: totais e gráfico por status, respeitando os filtros.

O painel é administrativo: execute-o localmente para esta atividade.
Os dois aplicativos precisam apontar para o mesmo projeto Supabase.

## Evidências

A pasta evidencias/ contém os prints do Gradio, das tabelas do Supabase e das
abas Consultar, Editar/Excluir e Indicadores do Streamlit.

O print gradio_mobile.jpg foi feito em uma visualização de 390 px de largura.
Após testar no celular físico, substitua-o pela captura do aparelho.

Os testes usam apenas dados fictícios. O banco tem exemplos nos cinco status.
Não inclua credenciais nos prints ou na entrega.
