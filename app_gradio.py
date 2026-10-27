import gradio as gr

import banco


def cadastrar(nome, endereco, email, celular, modelo, problema):
    try:
        numero = banco.cadastrar_os(nome, endereco, email, celular, modelo, problema)
        return f'Cadastro realizado! OS nº {numero}, status Aberto.'
    except (ValueError, RuntimeError) as erro:
        return str(erro)


with gr.Blocks(title='TechFix Informática') as demo:
    gr.Markdown('# TechFix Informática')
    gr.Markdown('Preencha os dados para abrir uma ordem de serviço. Use apenas dados fictícios.')
    with gr.Column():
        nome = gr.Textbox(label='Nome do Cliente', placeholder='Ana Exemplo')
        endereco = gr.Textbox(label='Endereço', placeholder='Rua Exemplo, 100')
        email = gr.Textbox(label='E-mail', placeholder='ana@example.com')
        celular = gr.Textbox(label='Celular/WhatsApp', placeholder='11999990001')
        modelo = gr.Textbox(label='Modelo do Computador', placeholder='Notebook de teste')
        problema = gr.Textbox(label='Problema Apresentado', placeholder='Descreva o defeito.', lines=4)
        botao = gr.Button('Cadastrar', variant='primary')
        limpar = gr.Button('Limpar')
        mensagem = gr.Textbox(label='Resultado', interactive=False)

    campos = [nome, endereco, email, celular, modelo, problema]
    botao.click(cadastrar, inputs=campos, outputs=mensagem)
    limpar.click(lambda: [''] * 7, outputs=campos + [mensagem])

if __name__ == '__main__':
    demo.launch(share=True)
