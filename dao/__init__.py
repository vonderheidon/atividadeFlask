import psycopg2
from psycopg2 import pool


db_pool = psycopg2.pool.SimpleConnectionPool(
    1,
    10,
    host='localhost',
    database='atvd1bcc',
    user='postgres',
    password='12345678'
)

def get_connection():
    return db_pool.getconn()

def put_connection(conn):
    db_pool.putconn(conn)

def verificarLogin(login, senha):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM usuario WHERE loginuser = %s AND senha = %s'
        cursor.execute(query, (login, senha))
        usuario = cursor.fetchone()
        return usuario is not None
    except Exception as ex:
        print(f"Erro ao verificar login: {ex}")
        return False
    finally:
        cursor.close()
        put_connection(conn)

def verificarSeLoginExiste(login):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM usuario WHERE loginuser = %s'
        cursor.execute(query, (login,))
        usuario = cursor.fetchone()
        return usuario is not None
    except Exception as ex:
        print(f"Erro ao verificar se o login existe: {ex}")
        return False
    finally:
        cursor.close()
        put_connection(conn)

def criarUsuario(login, senha, tipo_user):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'INSERT INTO usuario (loginuser, senha, tipouser) VALUES (%s, %s, %s)'
        cursor.execute(query, (login, senha, tipo_user))
        conn.commit()
        print("Usuário criado com sucesso.")
    except Exception as ex:
        print(f"Erro ao criar usuário: {ex}")
    finally:
        cursor.close()
        put_connection(conn)

def buscarUsuarios():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM usuario'
        cursor.execute(query)
        usuarios = cursor.fetchall()
        return usuarios
    except Exception as ex:
        print(f"Erro ao buscar usuários: {ex}")
        return None
    finally:
        cursor.close()
        put_connection(conn)

def buscarUsuarioPorLogin(login):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM usuario WHERE loginuser = %s'
        cursor.execute(query, (login,))
        usuarios = cursor.fetchone()
        return usuarios
    except Exception as ex:
        print(f"Erro ao buscar usuário: {ex}")
        return None
    finally:
        cursor.close()
        put_connection(conn)

def atualizarUsuario(login, nova_senha, novo_tipo):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'UPDATE usuario SET senha = %s, tipouser = %s WHERE loginuser = %s'
        cursor.execute(query, (nova_senha, novo_tipo, login))
        conn.commit()
        registros = cursor.rowcount
        print(f'Registros atualizados: {registros}')
    except Exception as ex:
        print(f"Erro ao atualizar usuário: {ex}")
    finally:
        cursor.close()
        put_connection(conn)

def atualizarTipoUsuario(login, novo_tipo):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'UPDATE usuario SET tipouser = %s WHERE loginuser = %s'
        cursor.execute(query, (novo_tipo, login))
        conn.commit()
        registros = cursor.rowcount
        print(f'Registros atualizados: {registros}')
    except Exception as ex:
        print(f"Erro ao atualizar usuário: {ex}")
    finally:
        cursor.close()
        put_connection(conn)

def buscarProdutos():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM produtos'
        cursor.execute(query)
        produtos = cursor.fetchall()
        return produtos
    except Exception as ex:
        print(f"Erro ao buscar produtos: {ex}")
        return None
    finally:
        cursor.close()
        put_connection(conn)

def buscarProdutoPorId(produto_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM produtos WHERE id = %s'
        cursor.execute(query, (produto_id,))
        produto = cursor.fetchone()
        return produto
    except Exception as ex:
        print(f"Erro ao buscar produto: {ex}")
        return None
    finally:
        cursor.close()
        put_connection(conn)

def contarProdutos(loginuser):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'SELECT COUNT(*) FROM produtos WHERE loginuser = %s'
        cursor.execute(query, (loginuser,))
        count = cursor.fetchone()[0]
        return count
    except Exception as ex:
        print(f"Erro ao contar produtos: {ex}")
        return 0
    finally:
        cursor.close()
        put_connection(conn)

def adicionarProduto(nome, loginuser, qtde, preco):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'INSERT INTO produtos (nome, loginuser, qtde, preco) VALUES (%s, %s, %s, %s)'
        cursor.execute(query, (nome, loginuser, qtde, preco))
        conn.commit()
        print("Produto adicionado com sucesso.")
    except Exception as ex:
        print(f"Erro ao adicionar produto: {ex}")
    finally:
        cursor.close()
        put_connection(conn)

def atualizarProduto(id, nome, qtde, preco):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'UPDATE produtos SET nome = %s, qtde = %s, preco = %s WHERE id = %s'
        cursor.execute(query, (nome, qtde, preco, id))
        conn.commit()
        print("Produto atualizado com sucesso.")
    except Exception as ex:
        print(f"Erro ao atualizar produto: {ex}")
    finally:
        cursor.close()
        put_connection(conn)

def excluirProduto(id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = 'DELETE FROM produtos WHERE id = %s'
        cursor.execute(query, (id,))
        conn.commit()
        print("Produto excluído com sucesso.")
    except Exception as ex:
        print(f"Erro ao excluir produto: {ex}")
    finally:
        cursor.close()
        put_connection(conn)


