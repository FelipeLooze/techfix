import pandas as pd
import streamlit as st

import banco

st.set_page_config(page_title='TechFix - Gerência', layout='wide')
st.title('TechFix Informática - Gerência')
st.caption('Use apenas dados fictícios.')

try:
    url, chave = st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY']
    banco.SUPABASE_URL, banco.SUPABASE_KEY = url, chave
except (FileNotFoundError, KeyError):
    pass

if 'mensagem' in st.session_state:
    st.success(st.session_state.pop('mensagem'))

try:
    registros = banco.consultar_ordens()
    clientes = banco.listar('clientes')
except (ValueError, RuntimeError) as erro:
    st.error(str(erro))
    st.stop()

COLUNAS = ['id', 'cliente_id', 'nome', 'endereco', 'email', 'celular_whatsapp',
           'modelo_computador', 'problema_relatado', 'status', 'data_abertura', 'data_atualizacao']
ROTULOS = {'id': 'Nº OS', 'nome': 'Cliente', 'endereco': 'Endereço', 'email': 'E-mail',
           'celular_whatsapp': 'Celular/WhatsApp', 'modelo_computador': 'Modelo',
           'problema_relatado': 'Problema', 'status': 'Status',
           'data_abertura': 'Abertura', 'data_atualizacao': 'Atualização'}
dados = pd.DataFrame(registros, columns=COLUNAS)

st.sidebar.header('Filtros de OS')
filtro_nome = st.sidebar.text_input('Nome do cliente')
filtro_email = st.sidebar.text_input('E-mail')
filtro_status = st.sidebar.multiselect('Status', banco.STATUS, default=banco.STATUS)
st.sidebar.button('Atualizar dados')

filtradas = dados[
    dados['nome'].str.contains(filtro_nome.strip(), case=False, regex=False, na=False)
    & dados['email'].str.contains(filtro_email.strip(), case=False, regex=False, na=False)
    & dados['status'].isin(filtro_status)
]
exibicao = filtradas.drop(columns='cliente_id').rename(columns=ROTULOS)
consultar, cadastrar, editar, indicadores = st.tabs(
    ['Consultar', 'Cadastrar', 'Editar/Excluir', 'Indicadores']
)

with consultar:
    st.subheader('Ordens de serviço')
    st.caption(f'{len(filtradas)} OS encontrada(s)')
    st.dataframe(exibicao, hide_index=True, width='stretch')
    st.download_button('Exportar CSV', exibicao.to_csv(index=False).encode('utf-8-sig'),
                       'ordens_servico.csv', 'text/csv', on_click='ignore')

with cadastrar:
    st.subheader('Nova ordem de serviço')
    with st.form('nova_os'):
        nome = st.text_input('Nome do Cliente', placeholder='Ana Exemplo')
        endereco = st.text_input('Endereço', placeholder='Rua Exemplo, 100')
        email = st.text_input('E-mail', placeholder='ana@example.com')
        celular = st.text_input('Celular/WhatsApp', placeholder='11999990001')
        modelo = st.text_input('Modelo do Computador', placeholder='Notebook de teste')
        problema = st.text_area('Problema Apresentado', placeholder='Descreva o defeito.')
        enviar = st.form_submit_button('Cadastrar')
    if enviar:
        try:
            numero = banco.cadastrar_os(nome, endereco, email, celular, modelo, problema)
            st.session_state.mensagem = f'OS nº {numero} cadastrada com status Aberto.'
            st.rerun()
        except (ValueError, RuntimeError) as erro:
            st.error(str(erro))

with editar:
    st.subheader('Editar ou excluir OS')
    if filtradas.empty:
        st.info('Nenhuma OS disponível com os filtros selecionados.')
    else:
        ordens = {int(linha['id']): linha for linha in filtradas.to_dict('records')}
        numero = st.selectbox('Selecione a OS', list(ordens),
                              format_func=lambda n: f"OS {n} - {ordens[n]['nome']}")
        ordem = ordens[numero]
        with st.form(f'editar_os_{numero}'):
            novo_modelo = st.text_input('Modelo', ordem['modelo_computador'])
            novo_problema = st.text_area('Problema', ordem['problema_relatado'])
            novo_status = st.selectbox('Status da OS', banco.STATUS,
                                       index=banco.STATUS.index(ordem['status']))
            salvar_os = st.form_submit_button('Salvar OS')
        if salvar_os:
            try:
                banco.editar_os(numero, novo_modelo, novo_problema, novo_status)
                st.session_state.mensagem = f'OS nº {numero} atualizada.'
                st.rerun()
            except (ValueError, RuntimeError) as erro:
                st.error(str(erro))

        confirmar_os = st.checkbox(f'Confirmo a exclusão da OS nº {numero}', key=f'confirmar_os_{numero}')
        if st.button('Excluir OS', disabled=not confirmar_os):
            try:
                banco.excluir_os(numero)
                st.session_state.mensagem = f'OS nº {numero} excluída.'
                st.rerun()
            except (ValueError, RuntimeError) as erro:
                st.error(str(erro))

    st.subheader('Dados dos clientes')
    if not clientes:
        st.info('Nenhum cliente cadastrado.')
    else:
        por_id = {cliente['id']: cliente for cliente in clientes}
        numero_cliente = st.selectbox('Selecione o cliente', list(por_id),
            format_func=lambda n: f"{n} - {por_id[n]['nome']} ({por_id[n]['email']})")
        cliente = por_id[numero_cliente]
        with st.form(f'editar_cliente_{numero_cliente}'):
            nome_cliente = st.text_input('Nome do cliente', cliente['nome'])
            endereco_cliente = st.text_input('Endereço do cliente', cliente['endereco'])
            email_cliente = st.text_input('E-mail do cliente', cliente['email'])
            celular_cliente = st.text_input('Celular do cliente', cliente['celular_whatsapp'])
            salvar_cliente = st.form_submit_button('Salvar cliente')
        if salvar_cliente:
            try:
                banco.editar_cliente(numero_cliente, nome_cliente, endereco_cliente,
                                      email_cliente, celular_cliente)
                st.session_state.mensagem = 'Cliente atualizado.'
                st.rerun()
            except (ValueError, RuntimeError) as erro:
                st.error(str(erro))

        st.caption('Clientes com OS vinculadas só podem ser excluídos depois das suas ordens.')
        confirmar_cliente = st.checkbox(f'Confirmo a exclusão do cliente nº {numero_cliente}',
                                         key=f'confirmar_cliente_{numero_cliente}')
        if st.button('Excluir cliente', disabled=not confirmar_cliente):
            try:
                banco.excluir_cliente(numero_cliente)
                st.session_state.mensagem = 'Cliente excluído.'
                st.rerun()
            except (ValueError, RuntimeError) as erro:
                st.error(str(erro))

with indicadores:
    st.subheader('Indicadores das OS filtradas')
    contagem = filtradas['status'].value_counts().reindex(banco.STATUS, fill_value=0)
    metricas = [('Total de OS', len(filtradas))] + [(status, int(contagem[status])) for status in banco.STATUS]
    for inicio in range(0, len(metricas), 3):
        for coluna, (titulo, valor) in zip(st.columns(3), metricas[inicio:inicio + 3]):
            coluna.metric(titulo, valor)
    st.bar_chart(contagem.rename('Quantidade'), sort=False)
