from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

#função calculos dos descontos
def calcular_cashback(valor_compra, desconto, cliente_vip=False):
    
    valor_final = valor_compra * (1 - desconto)  # aplicação do desconto

    cashback = valor_final * 0.05  # cálculo cashback base

    if cliente_vip:  # Bônus VIP (10% sobre o cashback base)
        cashback += cashback * 0.10 

    if valor_final > 500:  # Promoção dobro de cashback se valor > 500
        cashback *= 2

    return round(cashback, 2)


#conexão com banco
def conectar_db():
    return psycopg2.connect(os.environ.get("postgresql://postgres:ApryEkuaIyVDppyDsYVEbviKkAhhBscK@yamanote.proxy.rlwy.net:48507/railway"))


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

    return jsonify({"cashback": resultado})

#rota de histórico

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


if __name__ == "__main__":
    app.run()
