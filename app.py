from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from markupsafe import Markup
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import pandas as pd
import os
import plotly.express as px
import dao

app = Flask(__name__)
app.secret_key = '123chave'
app.config["JWT_SECRET_KEY"] = app.secret_key
jwt = JWTManager(app)

#API routes

@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    login = dados.get("login")
    senha = dados.get("senha")

    if not dao.verificarLogin(login, senha):
        return jsonify({"erro": "Login ou senha incorretos"}), 401

    access_token = create_access_token(identity=login)
    return jsonify(access_token=access_token), 200

@app.route('/api/produtos', methods=['GET'])
@jwt_required()
def listar_produtos_api():
    produtos = dao.buscarProdutos()
    if produtos is None:
        return jsonify({"erro": "Nenhum produto encontrado"}), 404

    produtos_list = [
        {"id": p[0], "nome": p[1], "loginuser": p[2], "qtde": p[3], "preco": p[4]}
        for p in produtos
    ]
    return jsonify(produtos_list)

@app.route('/api/produtos/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_produto(id):
    dados = request.get_json()

    nome = dados.get("nome")
    qtde = dados.get("qtde")
    preco = dados.get("preco")

    if not all([nome, qtde, preco]):
        return jsonify({"erro": "Dados incompletos. Certifique-se de enviar nome, qtde e preco."}), 400

    try:
        produto = dao.buscarProdutoPorId(id)
        if produto is None:
            return jsonify({"erro": "Produto não encontrado"}), 404

        dao.atualizarProduto(id, nome, qtde, preco)
        return jsonify({"mensagem": "Produto atualizado com sucesso."}), 200
    except Exception as ex:
        return jsonify({"erro": f"Erro ao atualizar produto: {ex}"}), 500

@app.route('/api/produtos/<int:id>', methods=['GET'])
@jwt_required()
def buscar_produto_por_id(id):
    produto = dao.buscarProdutoPorId(id)
    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_dict = {
        "id": produto[0],
        "nome": produto[1],
        "loginuser": produto[2],
        "qtde": produto[3],
        "preco": produto[4]
    }
    return jsonify(produto_dict)

@app.route('/api/produtos', methods=['POST'])
@jwt_required()
def inserir_produto():
    dados = request.get_json()

    nome = dados.get("nome")
    loginuser = dados.get("loginuser")
    qtde = dados.get("qtde")
    preco = dados.get("preco")

    if not all([nome, loginuser, qtde, preco]):
        return jsonify({"erro": "Dados incompletos. Certifique-se de enviar nome, loginuser, qtde e preco."}), 400

    try:
        dao.adicionarProduto(nome, loginuser, qtde, preco)
        return jsonify({"mensagem": "Produto inserido com sucesso."}), 201
    except Exception as ex:
        return jsonify({"erro": f"Erro ao inserir produto: {ex}"}), 500

@app.route('/api/produtos/<int:id>', methods=['DELETE'])
@jwt_required()
def excluir_produto_api(id):
    try:
        dao.excluirProduto(id)
        return jsonify({"mensagem": "Produto excluído com sucesso."}), 200
    except Exception as ex:
        return jsonify({"erro": f"Erro ao excluir produto: {ex}"}), 500

@app.route('/api/cadastrarUsuario', methods=['POST'])
def criar_usuario_api():
    dados = request.get_json()
    login = dados.get("loginuser")
    senha = dados.get("senha")
    tipo_user = dados.get("tipouser", "normal")

    if not all([login, senha]):
        return jsonify({"erro": "Dados incompletos. Certifique-se de enviar login e senha."}), 400

    if dao.verificarSeLoginExiste(login):
        return jsonify({"erro": "Este login ja esta em uso. Tente outro."}), 400

    try:
        dao.criarUsuario(login, senha, tipo_user)
        return jsonify({"mensagem": "Usuario criado com sucesso."}), 201
    except Exception as ex:
        return jsonify({"erro": f"Erro ao criar usuario: {ex}"}), 500

@app.route('/api/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios_api():
    usuarios = dao.buscarUsuarios()
    if usuarios is None:
        return jsonify({"erro": "Nenhum usuário encontrado"}), 404

    usuarios_list = [
        {"loginuser": u[0], "senha": u[1], "tipouser": u[2]}
        for u in usuarios
    ]
    return jsonify(usuarios_list)

@app.route('/api/usuarios/<login>', methods=['GET'])
@jwt_required()
def buscar_usuario_por_login_api(login):
    usuario = dao.buscarUsuarioPorLogin(login)
    if usuario is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    usuario_dict = {
        "loginuser": usuario[0],
        "senha": usuario[1],
        "tipouser": usuario[2]
    }
    return jsonify(usuario_dict)

@app.route('/api/usuarios/<login>', methods=['PUT'])
@jwt_required()
def atualizar_usuario_api(login):
    dados = request.get_json()
    novo_tipo = dados.get("tipouser")

    if not novo_tipo:
        return jsonify({"erro": "Tipo de usuário não fornecido."}), 400

    try:
        dao.atualizarTipoUsuario(login, novo_tipo)
        return jsonify({"mensagem": "Usuário atualizado com sucesso."}), 200
    except Exception as ex:
        return jsonify({"erro": f"Erro ao atualizar usuário: {str(ex)}"}), 500


##################################################################################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario_logado' in session:
        return redirect(url_for('listar_produtos'))

    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        if dao.verificarLogin(login, senha):
            session['usuario_logado'] = login
            return redirect(url_for('listar_produtos'))
        else:
            flash("Login ou senha incorretos.")

    return render_template('index.html')

@app.route('/listarUsuarios')
def listar_usuarios():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    login = session['usuario_logado']
    usuario = dao.buscarUsuarioPorLogin(login)

    if usuario is None:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

    tipo_usuario = usuario[2]

    if tipo_usuario != 'super':
        flash("Você não tem permissão para acessar esta página.")
        return redirect(url_for('listar_produtos'))

    usuarios = dao.buscarUsuarios()
    return render_template('listarUsuarios.html', usuarios=usuarios)


@app.route('/editar/<login>', methods=['GET', 'POST'])
def editar_usuario(login):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        novo_tipo = request.form['tipo']
        dao.atualizarTipoUsuario(login, novo_tipo)
        flash("Usuário atualizado com sucesso.")
        return redirect(url_for('listar_usuarios'))

    usuario = dao.buscarUsuarioPorLogin(login)
    if usuario:
        return render_template('editarUsuario.html', usuario=usuario)
    else:
        flash("Usuário não encontrado.")
        return redirect(url_for('listar_usuarios'))


@app.route('/listarProdutos')
def listar_produtos():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    loginuser = session['usuario_logado']
    usuario = dao.buscarUsuarioPorLogin(loginuser)

    if not usuario:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

    tipo_usuario = usuario[2]
    produtos = dao.buscarProdutos()

    return render_template('listarProdutos.html', produtos=produtos, tipo_usuario=tipo_usuario)


@app.route('/adicionarProduto', methods=['GET', 'POST'])
def adicionar_produto():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    loginuser = session['usuario_logado']

    usuario = dao.buscarUsuarioPorLogin(loginuser)
    if not usuario:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

    tipo_usuario = usuario[2]
    num_produtos = dao.contarProdutos(loginuser)

    if tipo_usuario == 'normal' and num_produtos >= 3:
        flash("Você não pode adicionar mais produtos. O limite de 3 produtos foi atingido.")
        return redirect(url_for('listar_produtos'))

    if request.method == 'POST':
        nome = request.form['nome']
        qtde = request.form['qtde']
        preco = request.form['preco']

        dao.adicionarProduto(nome, loginuser, qtde, preco)
        flash("Produto adicionado com sucesso.")
        return redirect(url_for('listar_produtos'))

    return render_template('adicionarProduto.html')


@app.route('/detalhesProduto/<int:id>')
def detalhes_produto(id):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    produto = dao.buscarProdutoPorId(id)
    if produto:
        return render_template('detalhesProduto.html', produto=produto)
    else:
        flash("Produto não encontrado.")
        return redirect(url_for('listar_produtos'))


@app.route('/editarProduto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        qtde = request.form['qtde']
        preco = request.form['preco']
        dao.atualizarProduto(id, nome, qtde, preco)
        flash("Produto atualizado com sucesso.")
        return redirect(url_for('listar_produtos'))

    produto = dao.buscarProdutoPorId(id)
    if produto:
        return render_template('editarProduto.html', produto=produto)
    else:
        flash("Produto não encontrado.")
        return redirect(url_for('listar_produtos'))


@app.route('/excluirProduto/<int:id>', methods=['GET'])
def excluir_produto(id):
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    dao.excluirProduto(id)
    flash("Produto excluído com sucesso.")
    return redirect(url_for('listar_produtos'))


@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash("Você foi desconectado.")
    return redirect(url_for('index'))


@app.route('/cadastrarUsuario', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        tipo_usuario = 'super' if request.form.get('super') else 'normal'

        if dao.verificarSeLoginExiste(login):
            flash("Este login já está em uso. Tente outro.")
        else:
            dao.criarUsuario(login, senha, tipo_usuario)
            flash("Cadastro realizado com sucesso. Faça login para continuar.")
            return redirect(url_for('index'))

    return render_template('cadastrarUsuario.html')

@app.route('/grafico', methods=['GET'])
def visualizacao():
    if 'usuario_logado' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect(url_for('index'))

    produtos = dao.buscarProdutos()

    if not produtos:
        flash("Não há produtos cadastrados para serem exibidos ainda.")
        return redirect(url_for('listar_produtos'))

    df = pd.DataFrame(produtos, columns=["id", "nome", "loginuser", "qtde", "preco"])

    fig = px.bar(df, x="nome", y="qtde", title="Quantidade de Produtos por Nome",
                 labels={"qtde": "Quantidade", "nome": "Nome do Produto"})

    fig.update_traces(
        marker=dict(
            color='pink',
            line=dict(
                color='rgb(119,67,22)',
                width=1
            )
        )
    )

    fig.update_layout(
        title="Quantidade de Produtos por Nome",
        title_x=0.5,
        title_font=dict(size=32, color="rgb(119,67,22)", family="Dancing Script, cursive"),
        xaxis=dict(
            tickangle=45,
            title="Nome do Produto",
            title_font=dict(size=20, color="#703c15", family="Dancing Script, cursive"),
            tickfont=dict(size=20, color="#703c15", family="Dancing Script, cursive")
        ),
        yaxis=dict(
            title="Quantidade",
            title_font=dict(size=20, color="#703c15", family="Dancing Script, cursive"),
            tickfont=dict(size=20, color="#703c15", family="Dancing Script, cursive")
        ),
        plot_bgcolor="#c8f3f5",
        paper_bgcolor="#fd92c6",
        showlegend=False,
        images=[{
            'source': '/static/images/kitty.webp',
            'xref': 'paper',
            'yref': 'paper',
            'x': 0.3,
            'y': 1,
            'sizex': 1.0,
            'sizey': 1.0,
            'opacity': 0.5,
            'layer': 'below'
        }]
    )

    graph_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Dancing+Script&display=swap" rel="stylesheet">
    </head>
    <body>
        {Markup(graph_html)}
    </body>
    </html>
    """

if __name__ == '__main__':

    certificado = os.path.join('ssl', 'certificado.pem')
    chave = os.path.join('ssl', 'chave.pem')
    #app.run(ssl_context=(certificado, chave), debug=True)
    app.run(debug=True)
