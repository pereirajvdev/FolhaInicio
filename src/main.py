import ctypes
import time
from ctypes import wintypes

from pywinauto import Desktop
from pywinauto.keyboard import send_keys


user32 = ctypes.windll.user32

GW_OWNER = 4
WM_CLOSE = 0x0010
SW_RESTORE = 9


# ============================================================
# FUNÇÕES
# ============================================================

def get_pid(hwnd):
    pid = wintypes.DWORD()

    user32.GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(pid)
    )

    return pid.value


def get_class(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def get_title(hwnd):
    tamanho = user32.GetWindowTextLengthW(hwnd)

    buffer = ctypes.create_unicode_buffer(tamanho + 1)

    user32.GetWindowTextW(
        hwnd,
        buffer,
        tamanho + 1
    )

    return buffer.value


def existe(hwnd):
    return bool(user32.IsWindow(hwnd))


def visivel(hwnd):
    return bool(user32.IsWindowVisible(hwnd))


# ============================================================
# LOCALIZA PRINCIPAL
# ============================================================

def localizar_principal():

    for janela in Desktop(backend="win32").windows():

        try:

            if (
                janela.class_name() == "TFormELGeral"
                and
                "Recursos Humanos e Folha de Pagamento"
                in janela.window_text()
            ):
                return janela.handle

        except Exception:
            pass

    return None


# ============================================================
# ENUMERA JANELAS
# ============================================================

def enumerar_janelas(pid_alvo):

    resultado = []

    @ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HWND,
        wintypes.LPARAM
    )
    def callback(hwnd, lparam):

        if get_pid(hwnd) != pid_alvo:
            return True

        if not visivel(hwnd):
            return True

        resultado.append(hwnd)

        return True

    user32.EnumWindows(callback, 0)

    return resultado


# ============================================================
# IDENTIFICA ERRO
# ============================================================

def eh_erro(hwnd):

    titulo = get_title(hwnd).lower()

    palavras = [
        "erro",
        "error",
        "não previsto",
        "nao previsto",
    ]

    return any(
        palavra in titulo
        for palavra in palavras
    )


# ============================================================
# FECHA ERRO COM TAB + ENTER
# ============================================================

def tratar_erros(pid_alvo):

    encontrou = False

    janelas = enumerar_janelas(pid_alvo)

    for hwnd in janelas:

        if not eh_erro(hwnd):
            continue

        encontrou = True

        print()
        print("=" * 80)
        print("ERRO ENCONTRADO")
        print("=" * 80)
        print(f"HWND   : {hwnd}")
        print(f"Classe : {get_class(hwnd)}")
        print(f"Título : {get_title(hwnd)!r}")
        print()

        try:

            janela = Desktop(
                backend="win32"
            ).window(
                handle=hwnd
            )

            janela.set_focus()

            time.sleep(0.3)

            print("Enviando TAB...")
            send_keys("{TAB}")

            time.sleep(0.2)

            print("Enviando ENTER...")
            send_keys("{ENTER}")

        except Exception as e:

            print(f"Erro ao tratar janela: {e}")

        # espera a janela desaparecer
        for _ in range(20):

            time.sleep(0.1)

            if not existe(hwnd):
                print("OK: erro fechado.")
                break

        else:
            print("ATENÇÃO: erro continua aberto.")

    return encontrou


# ============================================================
# IDENTIFICA FORM DO USUÁRIO
# ============================================================

def eh_form_usuario(hwnd, principal, app_hwnd):

    if hwnd == principal:
        return False

    if not visivel(hwnd):
        return False

    classe = get_class(hwnd)

    if not (
        classe.startswith("TForm")
        or classe.startswith("Tfm")
        or classe.startswith("Tfl")
    ):
        return False

    owner = user32.GetWindow(hwnd, GW_OWNER)

    if owner != app_hwnd:
        return False

    return True


# ============================================================
# FECHA FORM
# ============================================================

def fechar_form(hwnd):

    print()
    print("=" * 80)
    print("FECHANDO FORM")
    print("=" * 80)
    print(f"HWND   : {hwnd}")
    print(f"Classe : {get_class(hwnd)}")
    print(f"Título : {get_title(hwnd)!r}")

    user32.SetForegroundWindow(hwnd)

    time.sleep(0.3)

    user32.PostMessageW(
        hwnd,
        WM_CLOSE,
        0,
        0
    )

    # Não fica esperando indefinidamente.
    # O Delphi pode gerar o erro depois.
    time.sleep(0.5)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 100)
    print("FOLHA INÍCIO")
    print("=" * 100)

    principal = localizar_principal()

    if principal is None:

        print("TFormELGeral não encontrada.")
        return

    pid_alvo = get_pid(principal)

    app_hwnd = user32.GetWindow(
        principal,
        GW_OWNER
    )

    print(f"Principal    : {principal}")
    print(f"PID          : {pid_alvo}")
    print(f"TApplication : {app_hwnd}")

    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    while True:

        # ----------------------------------------------------
        # PRIMEIRO: verifica erros
        # ----------------------------------------------------

        if tratar_erros(pid_alvo):

            time.sleep(0.5)
            continue

        # ----------------------------------------------------
        # PROCURA UMA FORM
        # ----------------------------------------------------

        janelas = enumerar_janelas(pid_alvo)

        alvo = None

        for hwnd in janelas:

            if eh_form_usuario(
                hwnd,
                principal,
                app_hwnd
            ):

                alvo = hwnd
                break

        # ----------------------------------------------------
        # NADA MAIS PARA FECHAR
        # ----------------------------------------------------

        if alvo is None:
            break

        # ----------------------------------------------------
        # FECHA A FORM
        # ----------------------------------------------------

        fechar_form(alvo)

        # ----------------------------------------------------
        # DÁ TEMPO PARA O ERRO APARECER
        # ----------------------------------------------------

        time.sleep(0.5)

        # O loop volta para o início e chama
        # tratar_erros() novamente.

    # ========================================================
    # VOLTA PARA PRINCIPAL
    # ========================================================

    print()
    print("=" * 100)
    print("RETORNANDO À TELA PRINCIPAL")
    print("=" * 100)

    user32.ShowWindow(
        principal,
        SW_RESTORE
    )

    time.sleep(0.2)

    user32.SetForegroundWindow(
        principal
    )

    print("Concluído.")


if __name__ == "__main__":
    main()