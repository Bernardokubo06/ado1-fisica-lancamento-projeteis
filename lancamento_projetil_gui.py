"""
ADO 1 - Física: Lançamento de Projéteis com Interface Gráfica

Como executar:
1. Instale Python 3.10+.
2. Instale a dependência:
       pip install matplotlib
3. Execute:
       python lancamento_projetil_gui.py

Bibliotecas usadas:
- tkinter: interface gráfica, disponível normalmente com Python no Windows.
- matplotlib: gráfico da trajetória.

O programa considera o lançamento ideal, sem resistência do ar, usando as
fórmulas analíticas fornecidas no enunciado da atividade.
"""

import math
import tkinter as tk
from tkinter import messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# -----------------------------
# Física do lançamento
# -----------------------------

def calcular_tempo_voo(v0: float, theta_graus: float, y0: float, g: float) -> float:
    """Calcula o tempo total até o projétil atingir o solo (y = 0)."""
    theta = math.radians(theta_graus)
    vy0 = v0 * math.sin(theta)
    return (vy0 + math.sqrt(vy0**2 + 2 * g * y0)) / g


def calcular_altura_maxima(v0: float, theta_graus: float, y0: float, g: float) -> float:
    """Calcula a altura máxima do lançamento."""
    theta = math.radians(theta_graus)
    vy0 = v0 * math.sin(theta)
    return y0 + (vy0**2) / (2 * g)


def calcular_trajectoria(v0: float, theta_graus: float, y0: float, g: float,
                         quantidade_pontos: int = 500):
    """Calcula os pontos (x, y) da trajetória usando as fórmulas analíticas."""
    theta = math.radians(theta_graus)
    tempo_voo = calcular_tempo_voo(v0, theta_graus, y0, g)

    tempos = [tempo_voo * i / (quantidade_pontos - 1) for i in range(quantidade_pontos)]
    xs = []
    ys = []

    for t in tempos:
        x = v0 * math.cos(theta) * t
        y = y0 + v0 * math.sin(theta) * t - 0.5 * g * t**2
        # Pequenos erros numéricos podem gerar y negativo próximo ao solo.
        ys.append(max(0.0, y))
        xs.append(x)

    return xs, ys, tempos


def calcular_resultados(v0: float, theta_graus: float, y0: float, g: float):
    """Retorna alcance, altura máxima e tempo de voo."""
    theta = math.radians(theta_graus)
    tempo_voo = calcular_tempo_voo(v0, theta_graus, y0, g)
    altura_maxima = calcular_altura_maxima(v0, theta_graus, y0, g)
    alcance = v0 * math.cos(theta) * tempo_voo
    return alcance, altura_maxima, tempo_voo


# -----------------------------
# Interface gráfica
# -----------------------------

class ProjetilApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ADO 1 - Lançamento de Projéteis")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 680)

        # Estado da animação.
        self.animando = False
        self.after_id = None
        self.frame_animacao = 0
        self.frames_animacao = 180
        self.tempos_animacao = []
        self.xs_animacao = []
        self.ys_animacao = []

        # Trajetórias armazenadas para a funcionalidade extra.
        self.trajetorias_salvas = []

        # Valores padrão válidos.
        self.valores_padrao = {
            "v0": 30.0,
            "theta": 45.0,
            "y0": 5.0,
            "g": 9.81,
        }

        self._criar_widgets()
        self.atualizar_grafico()

    def _criar_widgets(self):
        # Layout principal: controles à esquerda e gráfico à direita.
        painel = tk.Frame(self.root, padx=12, pady=12)
        painel.pack(side=tk.LEFT, fill=tk.Y)

        grafico_frame = tk.Frame(self.root, padx=8, pady=8)
        grafico_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        titulo = tk.Label(
            painel,
            text="Lançamento de Projéteis",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=(0, 15))

        subtitulo = tk.Label(
            painel,
            text="Modelo ideal, sem resistência do ar",
            font=("Arial", 10)
        )
        subtitulo.pack(pady=(0, 18))

        self.entries = {}
        configuracoes = [
            ("Velocidade inicial v₀ (m/s)", "v0"),
            ("Ângulo θ (graus)", "theta"),
            ("Altura inicial y₀ (m)", "y0"),
            ("Gravidade g (m/s²)", "g"),
        ]

        for texto, chave in configuracoes:
            tk.Label(painel, text=texto, anchor="w").pack(fill=tk.X, pady=(5, 2))
            entrada = tk.Entry(painel, width=18, font=("Arial", 11))
            entrada.insert(0, str(self.valores_padrao[chave]))
            entrada.pack(fill=tk.X, pady=(0, 4))
            entrada.bind("<Return>", lambda _event: self.atualizar_grafico())
            self.entries[chave] = entrada

        tk.Label(
            painel,
            text="Faixas sugeridas: v₀ 5–150 | θ 1–89 | y₀ 0–50 | g 1,6–24,8",
            wraplength=245,
            justify="left",
            fg="#555555"
        ).pack(anchor="w", pady=(4, 12))

        self.botao_atualizar = tk.Button(
            painel,
            text="Atualizar trajetória",
            command=self.atualizar_grafico,
            width=22,
            height=2
        )
        self.botao_atualizar.pack(pady=4)

        self.botao_lancar = tk.Button(
            painel,
            text="Lançar",
            command=self.alternar_animacao,
            width=22,
            height=2
        )
        self.botao_lancar.pack(pady=4)

        self.botao_salvar = tk.Button(
            painel,
            text="Guardar trajetória",
            command=self.guardar_trajetoria,
            width=22
        )
        self.botao_salvar.pack(pady=4)

        self.botao_limpar = tk.Button(
            painel,
            text="Limpar trajetórias salvas",
            command=self.limpar_trajetorias,
            width=22
        )
        self.botao_limpar.pack(pady=4)

        self.mensagem = tk.Label(
            painel,
            text="",
            fg="#b00020",
            wraplength=245,
            justify="left"
        )
        self.mensagem.pack(anchor="w", pady=(12, 10))

        # Caixa de resultados.
        resultados = tk.LabelFrame(painel, text="Resultados", padx=10, pady=10)
        resultados.pack(fill=tk.X, pady=(8, 8))

        self.resultados_labels = {}
        for chave, texto in [
            ("R", "Alcance R:"),
            ("ymax", "Altura máxima:"),
            ("tvoo", "Tempo de voo:"),
        ]:
            linha = tk.Frame(resultados)
            linha.pack(fill=tk.X, pady=3)
            tk.Label(linha, text=texto).pack(side=tk.LEFT)
            valor = tk.Label(linha, text="-", font=("Arial", 10, "bold"))
            valor.pack(side=tk.RIGHT)
            self.resultados_labels[chave] = valor

        self.tempo_animacao_label = tk.Label(
            painel,
            text="t = 0,00 s",
            font=("Arial", 11, "bold")
        )
        self.tempo_animacao_label.pack(pady=8)

        # Figura Matplotlib.
        self.figura = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figura.add_subplot(111)
        self.ax.set_title("Trajetória do projétil")
        self.ax.set_xlabel("Posição horizontal x (m)")
        self.ax.set_ylabel("Altura y (m)")
        self.ax.grid(True, alpha=0.25)
        self.ax.axhline(0, linewidth=1)
        self.ax.set_aspect("equal", adjustable="box")

        self.linha_atual, = self.ax.plot([], [], linewidth=2, label="Trajetória atual")
        self.ponto_projetil, = self.ax.plot([], [], "o", markersize=8, label="Projétil")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.figura, master=grafico_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def obter_parametros(self):
        """Lê e valida os valores da interface sem permitir que o programa trave."""
        try:
            v0 = float(self.entries["v0"].get().replace(",", "."))
            theta = float(self.entries["theta"].get().replace(",", "."))
            y0 = float(self.entries["y0"].get().replace(",", "."))
            g = float(self.entries["g"].get().replace(",", "."))
        except ValueError:
            raise ValueError("Digite apenas valores numéricos. Ex.: 30 ou 9,81.")

        if v0 <= 0:
            raise ValueError("A velocidade inicial deve ser maior que zero.")
        if not 0 < theta < 90:
            raise ValueError("O ângulo deve estar entre 0° e 90° (sem incluir os extremos).")
        if y0 < 0:
            raise ValueError("A altura inicial não pode ser negativa.")
        if g <= 0:
            raise ValueError("A aceleração da gravidade deve ser maior que zero.")

        return v0, theta, y0, g

    def atualizar_grafico(self):
        """Atualiza o gráfico e os resultados quando os parâmetros mudam."""
        try:
            v0, theta, y0, g = self.obter_parametros()
            alcance, ymax, tempo_voo = calcular_resultados(v0, theta, y0, g)
            xs, ys, _tempos = calcular_trajectoria(v0, theta, y0, g)
        except ValueError as erro:
            self.mensagem.config(text=f"Entrada inválida: {erro}")
            return

        self.mensagem.config(text="")

        # Se estava animando, interrompe a animação para recalcular a curva.
        self.parar_animacao()

        self.linha_atual.set_data(xs, ys)
        self.ponto_projetil.set_data([xs[0]], [ys[0]])

        self.resultados_labels["R"].config(text=f"{alcance:.2f} m")
        self.resultados_labels["ymax"].config(text=f"{ymax:.2f} m")
        self.resultados_labels["tvoo"].config(text=f"{tempo_voo:.2f} s")
        self.tempo_animacao_label.config(text="t = 0,00 s")

        # Mantém os limites adequados e a mesma escala para x e y.
        margem_x = max(1.0, alcance * 0.08)
        margem_y = max(1.0, ymax * 0.08)
        self.ax.set_xlim(-margem_x, max(1.0, alcance + margem_x))
        self.ax.set_ylim(-margem_y * 0.15, max(1.0, ymax + margem_y))
        self.ax.set_aspect("equal", adjustable="box")
        self.canvas.draw_idle()

        # Guarda os dados atuais para a animação.
        self.xs_animacao = xs
        self.ys_animacao = ys
        self.tempos_animacao = _tempos

    def alternar_animacao(self):
        if self.animando:
            self.parar_animacao()
        else:
            self.iniciar_animacao()

    def iniciar_animacao(self):
        try:
            # Validação antes de iniciar.
            self.obter_parametros()
        except ValueError as erro:
            self.mensagem.config(text=f"Entrada inválida: {erro}")
            return

        if not self.xs_animacao:
            self.atualizar_grafico()
            if not self.xs_animacao:
                return

        self.animando = True
        self.frame_animacao = 0
        self.botao_lancar.config(text="Pausar")
        self._animar_frame()

    def _animar_frame(self):
        if not self.animando:
            return

        ultimo = len(self.xs_animacao) - 1
        proporcao = self.frame_animacao / ultimo if ultimo > 0 else 1.0
        indice = min(int(proporcao * ultimo), ultimo)

        self.ponto_projetil.set_data(
            [self.xs_animacao[indice]],
            [self.ys_animacao[indice]],
        )
        self.tempo_animacao_label.config(
            text=f"t = {self.tempos_animacao[indice]:.2f} s"
        )
        self.canvas.draw_idle()

        if indice >= ultimo:
            self.parar_animacao()
            return

        self.frame_animacao += 1
        self.after_id = self.root.after(25, self._animar_frame)

    def parar_animacao(self):
        self.animando = False
        self.botao_lancar.config(text="Lançar")
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

    def guardar_trajetoria(self):
        """Guarda a curva atual para comparação com outros lançamentos."""
        try:
            v0, theta, y0, g = self.obter_parametros()
            alcance, ymax, _tempo_voo = calcular_resultados(v0, theta, y0, g)
            xs, ys, _ = calcular_trajectoria(v0, theta, y0, g)
        except ValueError as erro:
            self.mensagem.config(text=f"Entrada inválida: {erro}")
            return

        self.trajetorias_salvas.append((xs, ys, theta, v0))

        # Remove e redesenha as trajetórias anteriores antes de desenhar a atual.
        self.ax.cla()
        self.ax.set_title("Trajetórias do projétil")
        self.ax.set_xlabel("Posição horizontal x (m)")
        self.ax.set_ylabel("Altura y (m)")
        self.ax.grid(True, alpha=0.25)
        self.ax.axhline(0, linewidth=1)

        for xs_salva, ys_salva, theta_salva, v0_salva in self.trajetorias_salvas:
            self.ax.plot(
                xs_salva,
                ys_salva,
                linewidth=1.8,
                label=f"θ={theta_salva:.1f}°, v₀={v0_salva:.1f} m/s"
            )

        self.linha_atual, = self.ax.plot(xs, ys, linewidth=2.5, label="Trajetória atual")
        self.ponto_projetil, = self.ax.plot([xs[0]], [ys[0]], "o", markersize=8, label="Projétil")
        self.ax.legend(loc="upper right", fontsize=8)
        self.ax.set_aspect("equal", adjustable="box")

        margem_x = max(1.0, alcance * 0.08)
        margem_y = max(1.0, ymax * 0.08)
        self.ax.set_xlim(-margem_x, max(1.0, alcance + margem_x))
        self.ax.set_ylim(-margem_y * 0.15, max(1.0, ymax + margem_y))
        self.canvas.draw_idle()

        # Atualiza os resultados, mantendo a interface sincronizada.
        self.mensagem.config(text="Trajetória adicionada à comparação.")
        self.atualizar_resultados_sem_limpar_curva(v0, theta, y0, g)
        self.xs_animacao = xs
        self.ys_animacao = ys
        self.tempos_animacao = [
            calcular_tempo_voo(v0, theta, y0, g) * i / (len(xs) - 1)
            for i in range(len(xs))
        ]

    def atualizar_resultados_sem_limpar_curva(self, v0, theta, y0, g):
        alcance, ymax, tempo_voo = calcular_resultados(v0, theta, y0, g)
        self.resultados_labels["R"].config(text=f"{alcance:.2f} m")
        self.resultados_labels["ymax"].config(text=f"{ymax:.2f} m")
        self.resultados_labels["tvoo"].config(text=f"{tempo_voo:.2f} s")

    def limpar_trajetorias(self):
        self.trajetorias_salvas.clear()
        self.atualizar_grafico()
        self.mensagem.config(text="Trajetórias salvas foram removidas.")


def main():
    root = tk.Tk()
    app = ProjetilApp(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
