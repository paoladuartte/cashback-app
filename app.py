from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def conectar_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

def criar_tabela():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS consultas (
        id SERIAL PRIMARY KEY,
        ip VARCHAR(50),
        tipo_cliente VARCHAR(10),
        valor NUMERIC,
        cashback NUMERIC
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

#função de cálculo de cashback
def calcular_cashback(valor_compra, desconto, cliente_vip=False):
    
    valor_final = valor_compra * (1 - desconto)

    cashback = valor_final * 0.05

    if cliente_vip:
        cashback += cashback * 0.10 

    if valor_final > 500:
        cashback *= 2

    return round(cashback, 2)

#rota para calcular cashback
@app.route("/cashback", methods=["POST"])
def cashback():
    data = request.json

    valor = data["valor"]
    desconto = data["desconto"]
    cliente_vip = data["vip"]

    resultado = calcular_cashback(valor, desconto, cliente_vip)

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO consultas (ip, tipo_cliente, valor, cashback) VALUES (%s, %s, %s, %s)",
        (request.remote_addr, "VIP" if cliente_vip else "NORMAL", valor, resultado)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "mensagem": "Compra registrada com sucesso! 🎉",
        "cashback": resultado
    })

# rota de histórico
@app.route("/historico", methods=["GET"])
def historico():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT tipo_cliente, valor, cashback FROM consultas WHERE ip = %s",
        (request.remote_addr,)
    )

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(dados)

# inicia servidor
if __name__ == "__main__":
    criar_tabela() 

    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
