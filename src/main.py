
import subprocess
import time
from pathlib import Path

import psutil
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

TITULO_JANELA_INTERMEDIARIA = "Folha Atual de Trabalho"

TITULO_JANELA_AVISO = "E&L - Aviso"

TITULO_JANELA_PRINCIPAL = (
    "Recursos Humanos e Folha de Pagamento "
    "[ Versão 3.02 - 17/06/2026 ]"
)

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


def preencher_login(janela, usuario, senha):
    """Preenche as credenciais e confirma a tela intermediária."""

    try:
        janela.set_focus()
    except Exception as erro:
        raise RuntimeError(
            f"Não foi possível ativar a janela de login: {erro}"
        ) from erro

    print("[INFO] Preenchendo o usuário...")
    pyautogui.write(usuario, interval=0.01)
    pyautogui.press("tab")

    print("[INFO] Preenchendo a senha...")
    pyautogui.write(senha, interval=0.01)
    pyautogui.press("enter")

    print("[OK] Credenciais enviadas ao sistema.")

    janela = aguardar_janela(TITULO_JANELA_INTERMEDIARIA)

    janela.set_focus()
    pyautogui.press("enter")

    print("[OK] Tela intermediária confirmada.")


def abrir_folha():
    """Fecha a instância anterior, abre a folha e realiza o login."""

    if not ARQUIVO_BAT.is_file():
        raise FileNotFoundError(
            f"Arquivo BAT não encontrado: {ARQUIVO_BAT}"
        )

    usuario, senha = ler_credenciais()

    fechar_folha_aberta()

    print("[INFO] Abrindo o sistema da folha...")

    subprocess.Popen(
        ["cmd.exe", "/c", str(ARQUIVO_BAT)],
        cwd=str(DIRETORIO_PROJETO),
    )

    janela = aguardar_janela(TITULO_JANELA_LOGIN)

    preencher_login(janela, usuario, senha)

    janela_aviso = aguardar_janela(TITULO_JANELA_AVISO)

    janela_aviso.set_focus()
    pyautogui.press("enter")

    posicionar_janela_inferior_esquerda()
    input("Verificar... ")
    print("[OK] Aviso confirmado.")

    posicionar_janela_inferior_esquerda()
   

def localizar_janela(titulo_esperado):
    """
    Localiza uma janela pelo título ou por um trecho dele.
    Retorna o objeto da janela ou None se não encontrar.
    """

    for janela in Desktop(backend="win32").windows():
        try:
            titulo = janela.window_text().strip()

            if titulo_esperado.lower() in titulo.lower():
                print(f"[OK] Janela identificada: {titulo}")
                return janela

        except Exception:
            continue

    return None


def fechar_folha_aberta():
    """Encerra o processo associado à janela principal, se estiver aberto."""

    print("[INFO] Verificando se a folha já está aberta...")

    janela = localizar_janela(TITULO_JANELA_PRINCIPAL)

    if janela is None:
        print("[INFO] Nenhuma instância anterior encontrada.")
        return

    try:
        pid = janela.process_id()
        processo = psutil.Process(pid)

        print(
            f"[INFO] Encerrando {processo.name()} "
            f"(PID {pid})..."
        )

        processo.terminate()

        try:
            processo.wait(timeout=1)
        except psutil.TimeoutExpired:
            processo.kill()
            processo.wait(timeout=1)

        print("[OK] Instância anterior encerrada.")

    except psutil.NoSuchProcess:
        print("[INFO] O processo já foi encerrado.")

    except psutil.AccessDenied:
        raise RuntimeError(
            "Acesso negado ao processo da folha. "
            "Verifique as permissões do Windows."
        )


def posicionar_janela_inferior_esquerda():
    """Redimensiona a janela para metade do monitor e a posiciona
    no canto inferior esquerdo, respeitando o padding."""

    janela = localizar_janela(TITULO_JANELA_PRINCIPAL)

    if janela is None:
        print("[AVISO] Janela principal da folha não encontrada.")
        return

    try:
        janela.restore()

        largura_tela, altura_tela = pyautogui.size()

        largura_janela = largura_tela // 2
        altura_janela = altura_tela // 2

        padding = 12

        x = padding
        y = (altura_tela - altura_janela) // 2 + padding

        janela.move_window(
            x=int(x),
            y=int(y),
            width=int(largura_janela - padding * 2),
            height=int(altura_janela - padding * 2),
            repaint=True,
        )

        print(
            "[OK] Janela redimensionada para metade do monitor "
            "e posicionada no canto inferior esquerdo."
        )

    except Exception as erro:
        raise RuntimeError(
            f"Não foi possível reposicionar a janela: {erro}"
        ) from erro


def aguardar_janela(titulo_esperado):
    """Aguarda até a janela aparecer ou atingir o tempo limite."""

    print(f"[INFO] Aguardando a janela: {titulo_esperado}")

    inicio = time.monotonic()

    while time.monotonic() - inicio < TEMPO_LIMITE:
        janela = localizar_janela(titulo_esperado)

        if janela is not None:
            return janela

        time.sleep(INTERVALO_VERIFICACAO)

    raise TimeoutError(
        f"A janela '{titulo_esperado}' não apareceu "
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
