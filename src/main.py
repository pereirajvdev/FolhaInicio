
import subprocess
import time
from pathlib import Path

import pyautogui
from pywinauto import Desktop


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_BAT = Path(r"\\192.168.0.14\el\scripts\el_folha.bat")

DIRETORIO_PROJETO = Path(__file__).resolve().parent.parent

ARQUIVO_CREDENCIAL = (
    Path.home() / "Documents" / "credencial.txt"
)

TITULO_JANELA_LOGIN = (
    "03 - Recursos Humanos e Folha de Pagamento ( Login )"
)

TITULO_JANELA_AVISO = "E&L - Aviso"

TEMPO_LIMITE = 60
INTERVALO_VERIFICACAO = 1


def ler_credenciais():
    """Lê o usuário na primeira linha e a senha na segunda."""

    if not ARQUIVO_CREDENCIAL.is_file():
        raise FileNotFoundError(
            f"Arquivo de credenciais não encontrado: {ARQUIVO_CREDENCIAL}"
        )

    linhas = ARQUIVO_CREDENCIAL.read_text(
        encoding="utf-8-sig"
    ).splitlines()

    if len(linhas) < 2:
        raise ValueError(
            "O credencial.txt deve conter o usuário na primeira "
            "linha e a senha na segunda."
        )

    usuario = linhas[0].strip()
    senha = linhas[1].strip()

    if not usuario or not senha:
        raise ValueError("O usuário e a senha não podem estar vazios.")

    return usuario, senha


def localizar_janela_login():
    """
    Aguarda até identificar a janela de login pelo título.
    Retorna o objeto da janela quando encontrado.
    """

    print(
        f"[INFO] Aguardando a janela: {TITULO_JANELA_LOGIN}"
    )

    inicio = time.monotonic()

    while time.monotonic() - inicio < TEMPO_LIMITE:
        try:
            janelas = Desktop(backend="win32").windows()

            for janela in janelas:
                try:
                    titulo = janela.window_text().strip()

                    if titulo == TITULO_JANELA_LOGIN:
                        print(f"[OK] Janela identificada: {titulo}")
                        return janela

                except Exception:
                    continue

        except Exception as erro:
            print(f"[AVISO] Erro ao listar janelas: {erro}")

        time.sleep(INTERVALO_VERIFICACAO)

    raise TimeoutError(
        f"A janela '{TITULO_JANELA_LOGIN}' não foi encontrada "
        f"em {TEMPO_LIMITE} segundos."
    )


def preencher_login(janela, usuario, senha):
    """Ativa a janela identificada e preenche as credenciais."""

    try:
        janela.set_focus()
    except Exception as erro:
        raise RuntimeError(
            f"Não foi possível ativar a janela de login: {erro}"
        ) from erro

    time.sleep(0.5)

    print("[INFO] Preenchendo o usuário...")
    pyautogui.write(usuario, interval=0.05)
    pyautogui.press("tab")

    print("[INFO] Preenchendo a senha...")
    pyautogui.write(senha, interval=0.05)
    pyautogui.press("enter")
    time.sleep(0.1)
    pyautogui.press("enter")
    print("[OK] Credenciais enviadas ao sistema.")


def abrir_folha():
    """Abre a folha e só preenche após localizar a janela de login."""

    if not ARQUIVO_BAT.is_file():
        raise FileNotFoundError(
            f"Arquivo BAT não encontrado: {ARQUIVO_BAT}"
        )

    usuario, senha = ler_credenciais()

    print("[INFO] Abrindo o sistema da folha...")

    subprocess.Popen(
        ["cmd.exe", "/c", str(ARQUIVO_BAT)],
        cwd=str(DIRETORIO_PROJETO),
    )

    janela = localizar_janela_login()

    preencher_login(janela, usuario, senha)

    localizar_janela_aviso()


def localizar_janela_aviso():
    """
    Aguarda até identificar a janela E&L - Aviso.
    Quando encontrada, ativa a janela e pressiona Enter.
    """

    print(f"[INFO] Aguardando a janela: {TITULO_JANELA_AVISO}")

    inicio = time.monotonic()

    while time.monotonic() - inicio < TEMPO_LIMITE:
        try:
            for janela in Desktop(backend="win32").windows():
                try:
                    titulo = janela.window_text().strip()

                    if titulo == TITULO_JANELA_AVISO:
                        print(f"[OK] Janela identificada: {titulo}")

                        janela.set_focus()
                        time.sleep(0.3)

                        pyautogui.press("enter")

                        print("[OK] Enter enviado para a janela de aviso.")
                        return

                except Exception:
                    continue

        except Exception as erro:
            print(f"[AVISO] Erro ao listar janelas: {erro}")

        time.sleep(INTERVALO_VERIFICACAO)

    raise TimeoutError(
        f"A janela '{TITULO_JANELA_AVISO}' não foi encontrada "
        f"em {TEMPO_LIMITE} segundos."
    )


def main():
    try:
        abrir_folha()
    except Exception as erro:
        print(f"[ERRO] {erro}")
        raise


if __name__ == "__main__":
    main()
