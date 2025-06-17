# agente.py (versão completa com todos os campos solicitados)
import platform
import socket
import getpass
from datetime import datetime
import psutil
import time
import subprocess
from flask import Flask, request, jsonify
from db import criar_tabela_se_nao_existir, criar_conexao, garantir_colunas_adicionais

app = Flask(__name__)

def formatar_duracao(segundos):
    minutos, _ = divmod(segundos, 60)
    horas, minutos = divmod(minutos, 60)
    dias, horas = divmod(horas, 24)
    if dias > 0:
        return f"{dias}d {horas}h"
    return f"{horas}h {minutos}min"

def detectar_tipo_dispositivo():
    try:
        output = subprocess.check_output(
            'wmic computersystem get PCSystemType', shell=True
        ).decode().splitlines()
        tipo_valor = next((l.strip() for l in output if l.strip().isdigit()), None)
        return {"1": "Desktop", "2": "Laptop", "3": "Servidor"}.get(tipo_valor, "Desconhecido")
    except: return "Desconhecido"

def verificar_firewall():
    try:
        res = subprocess.check_output(
            'netsh advfirewall show allprofiles', shell=True
        ).decode()
        return "Ativo" if "ON" in res.upper() else "Inativo"
    except: return "Desconhecido"

def verificar_defender():
    try:
        res = subprocess.check_output(
            'powershell "(Get-MpComputerStatus).RealTimeProtectionEnabled"', shell=True
        ).decode().strip()
        return "Ativo" if res == "True" else "Inativo"
    except: return "Desconhecido"

def verificar_status_atualizacoes():
    try:
        result = subprocess.check_output(
            'powershell "(New-Object -Com Microsoft.Update.AutoUpdate).Results"', shell=True
        ).decode()
        return "Pendentes" if "Pending" in result else "Atualizado"
    except: return "Desconhecido"

def obter_ultima_reinicio():
    try:
        return formatar_duracao(time.time() - psutil.boot_time())
    except: return "Desconhecido"

def verificar_servicos_inicio():
    try:
        return ", ".join(
            f"{svc.name()} ({svc.status()})"
            for svc in psutil.win_service_iter()
            if svc.start_type.lower() in ['auto', 'automatic']
        )
    except Exception as e:
        return f"Erro: {e}"


def obter_agendamentos():
    try:
        output = subprocess.check_output(
            'schtasks /query /fo csv /nh', shell=True
        ).decode(errors='ignore').splitlines()
        tarefas = [linha.split(',')[0].strip('"') for linha in output]
        return ", ".join(tarefas[:10])
    except Exception as e:
        return f"Erro: {e}"


def obter_fabricante_modelo():
    try:
        output = subprocess.check_output('wmic csproduct get vendor,name', shell=True).decode().splitlines()
        linhas = [l.strip() for l in output if l.strip()]
        if len(linhas) >= 2:
            valores = linhas[1].split()
            return valores[0], " ".join(valores[1:]) if len(valores) > 1 else "Desconhecido"
        return "Desconhecido", "Desconhecido"
    except: return "Desconhecido", "Desconhecido"

def obter_versao_bios():
    try:
        output = subprocess.check_output('wmic bios get smbiosbiosversion', shell=True).decode().splitlines()
        linhas = [l.strip() for l in output if l.strip()]
        return linhas[1] if len(linhas) > 1 else "Desconhecido"
    except: return "Desconhecido"


def obter_top_processos_cpu():
    try:
        processos = [(p.info['name'], p.cpu_percent()) for p in psutil.process_iter(['name', 'cpu_percent'])]
        top5 = sorted(processos, key=lambda x: x[1], reverse=True)[:5]
        return [f"{nome} ({cpu:.1f}%)" for nome, cpu in top5]
    except: return ["Erro"] * 5

def detectar_tipo_armazenamento():
    try:
        output = subprocess.check_output(
            'powershell "Get-PhysicalDisk | Select MediaType"', shell=True
        ).decode()
        if 'SSD' in output: return 'SSD'
        if 'HDD' in output: return 'HDD'
        return "Desconhecido"
    except: return "Desconhecido"

def obter_info_completa():
    hostname = socket.gethostname()
    fqdn = socket.getfqdn()
    ip = socket.gethostbyname(hostname) if hostname else "Desconhecido"
    versao_windows = platform.platform()
    arquitetura = platform.architecture()[0]
    usuario = getpass.getuser()

    disco = psutil.disk_usage('/')
    tamanho_disco = round(disco.total / (1024**3), 2)
    espaco_livre = round(disco.free / (1024**3), 2)
    percentual_livre = round((disco.free / disco.total) * 100, 1)

    tipo_dispositivo = detectar_tipo_dispositivo()
    firewall = verificar_firewall()
    defender = verificar_defender()
    uso_cpu = psutil.cpu_percent(interval=1)
    uso_ram = psutil.virtual_memory().percent
    tempo_desde_reinicio = obter_ultima_reinicio()
    fabricante, modelo = obter_fabricante_modelo()
    bios = obter_versao_bios()
    tipo_armazenamento = detectar_tipo_armazenamento()
    antivirus = defender  # já capturado
    nucleos_fisicos = psutil.cpu_count(logical=False)
    nucleos_logicos = psutil.cpu_count(logical=True)
    freq = round(psutil.cpu_freq().max / 1000, 2) if psutil.cpu_freq() else 0
    processos = obter_top_processos_cpu()
    servicos_ativos = verificar_servicos_inicio()

    return (
        hostname, fqdn, ip, versao_windows, arquitetura, usuario,
        tamanho_disco, espaco_livre, percentual_livre,
        tipo_dispositivo, firewall, defender,
        uso_cpu, uso_ram, tempo_desde_reinicio,
        fabricante, modelo, bios,
        nucleos_fisicos, nucleos_logicos, freq,
        tipo_armazenamento, antivirus,
        *processos,
        servicos_ativos
    )



def salvar_info_no_banco(*dados):
    conn = criar_conexao()
    cursor = conn.cursor()

    campos = """
        hostname, fqdn, ip, versao_windows, arquitetura, usuario_logado,
        tamanho_disco_gb, espaco_livre_gb, percentual_disco_livre,
        tipo_dispositivo, firewall, defender,
        uso_cpu, uso_ram, ultima_reinicio,
        fabricante, modelo, versao_bios,
        nucleos_fisicos, nucleos_logicos, frequencia_cpu_ghz,
        tipo_armazenamento, antivirus,
        processo_1, processo_2, processo_3, processo_4, processo_5,
        servicos_ativos
    """

    placeholders = ', '.join(['?'] * 29)
    data_local = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print("Total de campos declarados:", len([c.strip() for c in campos.split(',')]))
    print("Total de dados fornecidos:", len(dados))

    cursor.execute(f"""
    INSERT INTO info_sistema ({campos}, data_registro)
    VALUES ({placeholders}, ?)
    """, (*dados, data_local))

    conn.commit()
    conn.close()


def main():
    while True:
        print("Executando coleta...")
        criar_tabela_se_nao_existir()
        garantir_colunas_adicionais()
        dados = obter_info_completa()
        salvar_info_no_banco(*dados)
        print("Aguardando 5 minutos...")
        time.sleep(300)  # 300 segundos = 5 minutos

if __name__ == "__main__":
    main()
