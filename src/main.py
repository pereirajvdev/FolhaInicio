
import time
import subprocess
from pathlib import Path

import pyautogui


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_BAT = Path(r"\\192.168.0.14\el\scripts\el_folha.bat")

# C:\Users\Joao Castro\Documents\FolhaInicio\src\main.py
DIRETORIO_PROJETO = Path(__file__).resolve().parent.parent

# Arquivo localizado em Documents\credencial.txt
ARQUIVO_CREDENCIAL = Path.home() / "Documents" / "credencial.txt"

TEMPO_ABERTURA = 5


def ler_credenciais():
    """
    Lê o usuário na primeira linha e a senha na segunda linha.
    """

    if not ARQUIVO_CREDENCIAL.exists():
        raise FileNotFoundError(
            f"Arquivo de credenciais não encontrado: {ARQUIVO_CREDENCIAL}"
        )

    linhas = ARQUIVO_CREDENCIAL.read_text(
        encoding="utf-8-sig"
    ).splitlines()

    if len(linhas) < 2:
        raise ValueError(
            "O arquivo credencial.txt deve conter o usuário "
            "na primeira linha e a senha na segunda."
        )

    usuario = linhas[0].strip()
    senha = linhas[1].strip()

    if not usuario or not senha:
        raise ValueError(
            "O usuário e a senha não podem estar vazios."
        )

    return usuario, senha


def abrir_folha():
    """
    Abre o sistema da folha e preenche as credenciais.
    """

    if not ARQUIVO_BAT.exists():
        raise FileNotFoundError(
            f"Arquivo BAT não encontrado: {ARQUIVO_BAT}"
        )

    usuario, senha = ler_credenciais()

    print("[INFO] Abrindo o sistema da folha...")

    subprocess.Popen(
        ["cmd.exe", "/c", str(ARQUIVO_BAT)],
        cwd=str(DIRETORIO_PROJETO)
    )

    print(
        f"[INFO] Aguardando {TEMPO_ABERTURA} segundos "
        "para a abertura do sistema..."
    )

    time.sleep(TEMPO_ABERTURA)

    print("[INFO] Preenchendo o usuário...")

    pyautogui.write(usuario, interval=0.05)
    pyautogui.press("tab")

    print("[INFO] Preenchendo a senha...")

    pyautogui.write(senha, interval=0.05)
    pyautogui.press("enter")

    print("[OK] Credenciais enviadas ao sistema.")


def main():
    try:
        abrir_folha()

    except Exception as erro:
        print(f"[ERRO] {erro}")
        raise


if __name__ == "__main__":
    main()
