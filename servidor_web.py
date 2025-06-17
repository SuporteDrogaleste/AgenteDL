# servidor_web.py
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
DB_PATH = "agente_dl.db"

def obter_dados():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, hostname, fqdn, ip, versao_windows, arquitetura, usuario_logado,
               tamanho_disco_gb, espaco_livre_gb, percentual_disco_livre,
               tipo_dispositivo, firewall, defender,
               uso_cpu, uso_ram,
               ultima_reinicio,
               fabricante, modelo, versao_bios,
               nucleos_fisicos, nucleos_logicos, frequencia_cpu_ghz,
               tipo_armazenamento, antivirus, windows_atualizado,
               processo_1, processo_2, processo_3, processo_4, processo_5,
               data_registro
        FROM info_sistema
        ORDER BY data_registro DESC
    """)

    registros = [row for row in cursor.fetchall()]
    conn.close()
    return registros


@app.route("/")
def index():
    registros = obter_dados()
    return render_template("index.html", registros=registros)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
