# db.py
import sqlite3
import os

DB_PATH = "agente_dl.db"

def criar_conexao():
    return sqlite3.connect(DB_PATH)

def criar_tabela_se_nao_existir():
    conn = criar_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS info_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT,
            ip TEXT,
            versao_windows TEXT,
            arquitetura TEXT,
            tamanho_disco_gb REAL,
            espaco_livre_gb REAL,
            tipo_dispositivo TEXT,
            firewall TEXT,
            defender TEXT,
            uso_cpu REAL,
            uso_ram REAL,
            status_atualizacoes TEXT,
            ultima_reinicio TEXT,
            servicos_ativos TEXT,
            fabricante TEXT,
            modelo TEXT,
            versao_bios TEXT,
            fqdn TEXT,
            usuario_logado TEXT,
            nucleos_fisicos INTEGER,
            nucleos_logicos INTEGER,
            frequencia_cpu_ghz REAL,
            tipo_armazenamento TEXT,
            antivirus TEXT,
            windows_atualizado TEXT,
            processo_1 TEXT,
            processo_2 TEXT,
            processo_3 TEXT,
            processo_4 TEXT,
            processo_5 TEXT,
            servicos_inicio TEXT,
            agendamentos_ativos TEXT,
            percentual_disco_livre REAL,
            data_registro TEXT
        )
    """)
    conn.commit()
    conn.close()


def garantir_colunas_adicionais():
    conn = criar_conexao()
    cursor = conn.cursor()
    colunas = {
    "fabricante": "TEXT",
    "modelo": "TEXT",
    "versao_bios": "TEXT",
    "fqdn": "TEXT",
    "usuario_logado": "TEXT",
    "nucleos_fisicos": "INTEGER",
    "nucleos_logicos": "INTEGER",
    "frequencia_cpu_ghz": "REAL",
    "tipo_armazenamento": "TEXT",
    "antivirus": "TEXT",
    "windows_atualizado": "TEXT",
    "processo_1": "TEXT",
    "processo_2": "TEXT",
    "processo_3": "TEXT",
    "processo_4": "TEXT",
    "processo_5": "TEXT",
    "servicos_inicio": "TEXT",
    "agendamentos_ativos": "TEXT",
    "percentual_disco_livre": "REAL",
    "data_registro": "TEXT"
}

    for coluna, tipo in colunas.items():
        try:
            cursor.execute(f"ALTER TABLE info_sistema ADD COLUMN {coluna} {tipo}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
    conn.commit()
    conn.close()

