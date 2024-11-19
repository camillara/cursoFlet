import flet as ft
import random
import threading
import time


def create_card(value, on_click):
    return ft.Container(
        height=100,
        width=100,
        border_radius=10,
        bgcolor=ft.colors.BLUE_GREY_900,
        alignment=ft.alignment.center,
        content=ft.Text(
            value="?",
            color=ft.colors.WHITE,
            size=30,
            weight=ft.FontWeight.BOLD
        ),
        data=value,
        on_click=on_click,
    )


def main(page: ft.Page):
    page.title = "Jogo da Memória"
    page.bgcolor = ft.colors.DEEP_PURPLE_200
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Texto inicial explicando o objetivo do jogo
    instructions = ft.Text(
        "Bem-vindo ao Jogo da Memória!\n"
        "O objetivo é encontrar todos os pares de cartas.\n"
        "Clique em duas cartas para revelá-las. Se formarem um par, elas permanecem viradas.\n"
        "Divirta-se!",
        size=18,
        color=ft.colors.WHITE,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    # Variáveis globais para o jogo
    flipped_cards = []
    matched_cards = set()
    start_time = 0
    attempts = 0

    # Contador de tempo exibido em tempo real
    time_text = ft.Text(f"Tempo: 0 segundos", size=16, color=ft.colors.WHITE)
    attempts_text = ft.Text(f"Tentativas: 0", size=16, color=ft.colors.WHITE)

    def update_timer():
        while len(matched_cards) < 16:  # 16 é o total de cartas no jogo
            elapsed_time = int(time.time() - start_time)
            time_text.value = f"Tempo: {elapsed_time} segundos"
            time_text.update()
            time.sleep(1)

    # Função para iniciar o jogo
    def start_game():
        nonlocal start_time, attempts

        # Reiniciar contadores
        attempts = 0
        start_time = time.time()  # Armazena o tempo de início
        flipped_cards.clear()
        matched_cards.clear()

        # Gerar valores para as cartas
        card_values = list(range(1, 9)) * 2  # Duas de cada valor
        random.shuffle(card_values)

        # Atualizar a interface
        page.controls.clear()

        # Iniciar o cronômetro em uma thread separada
        threading.Thread(target=update_timer, daemon=True).start()

        def card_click(e):
            nonlocal attempts
            card = e.control

            # Ignorar cliques inválidos
            if card in matched_cards or len(flipped_cards) == 2:
                return

            # Incrementar tentativas ao virar uma carta
            if len(flipped_cards) < 2:
                attempts += 1
                attempts_text.value = f"Tentativas: {attempts // 2}"
                attempts_text.update()

            # Revelar carta
            card.content.value = str(card.data)
            card.bgcolor = ft.colors.AMBER_400
            card.update()

            flipped_cards.append(card)

            # Verificar correspondência
            if len(flipped_cards) == 2:
                card1, card2 = flipped_cards
                if card1.data == card2.data:
                    matched_cards.add(card1)
                    matched_cards.add(card2)
                    flipped_cards.clear()
                else:
                    # Esconder as cartas novamente após 1 segundo
                    def hide_cards():
                        time.sleep(1)
                        for c in flipped_cards:
                            c.content.value = "?"
                            c.bgcolor = ft.colors.BLUE_GREY_900
                            c.update()
                        flipped_cards.clear()
                        page.update()

                    threading.Thread(target=hide_cards).start()

            # Verificar vitória
            if len(matched_cards) == len(card_values):
                elapsed_time = int(time.time() - start_time)

                def restart_game(e):
                    page.dialog.open = False  # Fecha o alerta de vitória
                    page.update()
                    start_game()

                def close_game(e):
                    page.window_close()

                # Diálogo de vitória
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Você venceu! 🎉"),
                    content=ft.Text(
                        f"Parabéns! Você completou o jogo em {elapsed_time} segundos "
                        f"com {attempts // 2} tentativas.\n\n"
                        "Deseja jogar novamente ou encerrar?"
                    ),
                    actions=[
                        ft.TextButton("Jogar Novamente", on_click=restart_game),
                        ft.TextButton("Encerrar", on_click=close_game),
                    ],
                    open=True,
                )
                page.update()

        # Criar tabuleiro
        board = ft.GridView(
            expand=True,
            max_extent=110,
            child_aspect_ratio=1,
            padding=10,
            spacing=10,
            controls=[
                create_card(value, card_click) for value in card_values
            ],
        )

        # Adicionar componentes à página
        page.add(instructions)
        page.add(ft.Row([time_text, attempts_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        page.add(board)
        page.update()

    # Iniciar o jogo
    start_game()


if __name__ == "__main__":
    ft.app(target=main)
