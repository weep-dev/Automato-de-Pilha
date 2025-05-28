from PyQt5.QtGui import QPainter, QPainterPath, QPolygonF
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsTextItem, QListWidget, QGraphicsLineItem, QGraphicsRectItem,
    QLineEdit, QLabel, QGraphicsPolygonItem
)
from PyQt5.QtGui import QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QPointF
import math

class AutomatonVisualizer(QWidget):
    def __init__(self, automaton):
        super().__init__()
        self.setWindowTitle("Visualizador de Autômato de Pilha")
        self.automaton = automaton
        self.scene = QGraphicsScene()
        self.state_items = {}
        self.stack_items = []
        self.positions = {
            'q0': QPointF(100, 150),
            'q1': QPointF(300, 150),
            # Adicione mais estados aqui, se necessário
        }

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Entrada
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Digite a cadeia (ex: aaabbb)")
        input_layout.addWidget(QLabel("Entrada:"))
        input_layout.addWidget(self.input_field)
        layout.addLayout(input_layout)

        # Visor gráfico
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.view)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar")
        self.btn_step = QPushButton("Passo")
        self.btn_run = QPushButton("Executar Tudo")
        self.btn_reset = QPushButton("Resetar")

        self.btn_step.setEnabled(False)
        self.btn_run.setEnabled(False)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_step)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_reset)
        layout.addLayout(btn_layout)

        # Log
        self.log = QListWidget()
        layout.addWidget(QLabel("Log de Execução:"))
        layout.addWidget(self.log)

        self.setLayout(layout)

        self.draw_states()
        self.draw_transitions()

        self.btn_start.clicked.connect(self.start_automaton)
        self.btn_step.clicked.connect(self.step_automaton)
        self.btn_run.clicked.connect(self.run_automaton)
        self.btn_reset.clicked.connect(self.reset_automaton)

    def draw_states(self):
        for state, pos in self.positions.items():
            item = QGraphicsEllipseItem(0, 0, 60, 60)
            item.setPos(pos)
            item.setBrush(QBrush(Qt.white))
            item.setPen(QPen(Qt.black, 2))
            self.scene.addItem(item)

            text = QGraphicsTextItem(state)
            text.setFont(QFont("Arial", 14))
            text.setPos(pos + QPointF(18, 18))
            self.scene.addItem(text)

            self.state_items[state] = item

            # Estado inicial: triângulo
            if state == self.automaton.start_state:
                triangle = QPolygonF([
                    QPointF(pos.x() - 10, pos.y() + 30),
                    QPointF(pos.x() - 30, pos.y() + 15),
                    QPointF(pos.x() - 30, pos.y() + 45),
                ])
                arrow_item = QGraphicsPolygonItem(triangle)
                arrow_item.setBrush(QBrush(Qt.black))
                arrow_item.setPen(QPen(Qt.black))
                self.scene.addItem(arrow_item)

            # Estado final: círculo interno
            if state in self.automaton.accept_states:
                inner_circle = QGraphicsEllipseItem(0, 0, 50, 50)
                inner_circle.setPos(pos + QPointF(5, 5))
                inner_circle.setPen(QPen(Qt.black, 2))
                inner_circle.setBrush(Qt.transparent)
                self.scene.addItem(inner_circle)

    def draw_transitions(self):
        radius = 30  # raio dos círculos dos estados

        for (from_state, symbol, stack_top), (to_state, stack_op) in self.automaton.transitions.items():
            start_center = self.positions[from_state] + QPointF(radius, radius)
            end_center = self.positions[to_state] + QPointF(radius, radius)

            if from_state == to_state:
                path = QPainterPath()
                cx = start_center.x()  # Coordenada X do centro do estado
                cy = start_center.y()  # Coordenada Y do centro do estado
                state_R = 30           # Raio do círculo do estado

                # Pontos de conexão do loop no círculo do estado
                # Ângulos em radianos (0 é à direita, positivo é anti-horário no Qt)
                # Ajuste esses ângulos para mudar onde o loop "toca" o estado
                start_angle_on_state_deg = 45  # Começa no lado superior direito do estado
                end_angle_on_state_deg = 135   # Termina no lado superior esquerdo do estado

                # No Qt, o eixo Y é invertido, então subtraímos para "subir"
                p_start_x = cx + state_R * math.cos(math.radians(start_angle_on_state_deg))
                p_start_y = cy - state_R * math.sin(math.radians(start_angle_on_state_deg))
                path.moveTo(p_start_x, p_start_y)

                p_end_x = cx + state_R * math.cos(math.radians(end_angle_on_state_deg))
                p_end_y = cy - state_R * math.sin(math.radians(end_angle_on_state_deg))

                # Ponto de controle para a curva de Bézier quadrática
                # Define o quão "alto" o loop vai. Ajuste loop_height_factor conforme necessário.
                loop_height_factor = 3.5 # Multiplicador da altura do loop em relação ao raio
                ctrl_x = cx
                ctrl_y = cy - state_R * loop_height_factor - 10 # O -10 é um pequeno espaçamento adicional

                path.quadTo(ctrl_x, ctrl_y, p_end_x, p_end_y)
                self.scene.addPath(path, QPen(Qt.black, 2))

                # --- Desenhar a ponta da seta para o loop ---
                arrow_size = 10
                # Vetor da tangente no ponto final (aproximado pelo vetor do ponto de controle ao ponto final)
                dx_tangent = p_end_x - ctrl_x
                dy_tangent = p_end_y - ctrl_y
                len_tangent = math.hypot(dx_tangent, dy_tangent)
                if len_tangent == 0: len_tangent = 1
                
                udx = dx_tangent / len_tangent # Componente x do vetor unitário da tangente
                udy = dy_tangent / len_tangent # Componente y do vetor unitário da tangente

                # Pontos do triângulo da seta
                # Ponto 1 é a ponta da seta, em p_end
                arrow_p1 = QPointF(p_end_x, p_end_y)
                
                # Base da seta (oposta à ponta)
                base_x = p_end_x - udx * arrow_size
                base_y = p_end_y - udy * arrow_size
                
                # Vetor perpendicular à tangente para as "asas" da seta
                # perp_dx = -udy
                # perp_dy = udx
                # Simplificado para rotação de 90 graus (pode precisar de ajuste fino se a curva for muito acentuada)
                # Para um resultado visual mais consistente, pode ser melhor usar um ângulo fixo para as asas da seta.
                # No entanto, vamos usar a perpendicular para simplicidade agora:
                
                angle_rad_tangent = math.atan2(-dy_tangent, dx_tangent) # Note o -dy_tangent para o sistema de coordenadas do Qt

                # Pontos para as "asas" da seta
                angle_offset = math.pi / 6 # 30 graus para cada lado da tangente

                arrow_p2 = QPointF(
                    p_end_x - arrow_size * math.cos(angle_rad_tangent - angle_offset),
                    p_end_y + arrow_size * math.sin(angle_rad_tangent - angle_offset)
                )
                arrow_p3 = QPointF(
                    p_end_x - arrow_size * math.cos(angle_rad_tangent + angle_offset),
                    p_end_y + arrow_size * math.sin(angle_rad_tangent + angle_offset)
                )
                
                arrow_head_poly = QPolygonF([arrow_p1, arrow_p2, arrow_p3])
                arrow_item = QGraphicsPolygonItem(arrow_head_poly)
                arrow_item.setBrush(QBrush(Qt.black))
                arrow_item.setPen(QPen(Qt.black, 1)) # Linha fina para o contorno da seta
                self.scene.addItem(arrow_item)

                # --- Rótulo para o loop ---
                # (Você já deve ter a lógica de formatação do label_text como discutimos antes)
                stack_top_display = "ε" if stack_top == "" else stack_top
                if stack_op == "POP":
                    stack_op_display = "ε"
                elif not stack_op : # Se stack_op for None ou string vazia (não POP e não um símbolo)
                    stack_op_display = "ε" # Ou como você preferir representar "não fazer nada"
                else:
                    stack_op_display = stack_op
                label_text = f"{symbol}, {stack_top_display} ; {stack_op_display}"
                
                label = QGraphicsTextItem(label_text)
                label.setFont(QFont("Arial", 10)) # Ou a fonte que estiver usando

                # Posicionar o rótulo acima do ponto mais alto do loop (ctrl_x, ctrl_y)
                # Para centralizar o texto, precisamos da largura e altura do texto.
                label_rect = label.boundingRect()
                label_x = ctrl_x - label_rect.width() / 2
                label_y = ctrl_y - label_rect.height() + 25 # 5px de espaço acima do ápice do loop
                label.setPos(label_x, label_y)
                self.scene.addItem(label)

            else:
                # Linha entre estados diferentes (ajustando para sair e entrar na borda)
                dx = end_center.x() - start_center.x()
                dy = end_center.y() - start_center.y()
                length = math.hypot(dx, dy)
                if length == 0:
                    length = 1

                ux = dx / length
                uy = dy / length

                # Ajusta para borda (começa e termina no raio do estado)
                start_pos = QPointF(start_center.x() + ux * radius, start_center.y() + uy * radius)
                end_pos = QPointF(end_center.x() - ux * radius, end_center.y() - uy * radius)

                line = QGraphicsLineItem(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
                line.setPen(QPen(Qt.black, 2))
                self.scene.addItem(line)

                # Desenha a seta na ponta
                arrow_size = 10

                base_x = end_pos.x() - ux * arrow_size
                base_y = end_pos.y() - uy * arrow_size

                left_x = base_x + uy * (arrow_size / 2)
                left_y = base_y - ux * (arrow_size / 2)

                right_x = base_x - uy * (arrow_size / 2)
                right_y = base_y + ux * (arrow_size / 2)

                arrow_head = QPolygonF([
                    QPointF(end_pos.x(), end_pos.y()),
                    QPointF(left_x, left_y),
                    QPointF(right_x, right_y)
                ])

                arrow_item = QGraphicsPolygonItem(arrow_head)
                arrow_item.setBrush(QBrush(Qt.black))
                arrow_item.setPen(QPen(Qt.black))
                self.scene.addItem(arrow_item)

                # Label no meio da linha, ligeiramente deslocado
                # Formata o topo da pilha para exibição
                stack_top_display = "ε" if stack_top == "" else stack_top

                # Formata a operação da pilha para exibição
                if stack_op == "POP":
                    stack_op_display = "ε"
                # Se você tiver uma representação para "não fazer nada" ou "manter topo", adicione aqui
                elif stack_op == "ε" or stack_op == "": # Exemplo, se '' significar não mudar pilha
                    stack_op_display = "ε" # Ou stack_top_display se for para "manter"
                else: # Assume que qualquer outra coisa é um símbolo para empilhar
                    stack_op_display = stack_op

                label_text = f"{symbol}, {stack_top_display} ; {stack_op_display}"
                label = QGraphicsTextItem(label_text)
                label.setFont(QFont("Arial", 10))
                mid_x = (start_pos.x() + end_pos.x()) / 2
                mid_y = (start_pos.y() + end_pos.y()) / 2
                label.setPos(mid_x - 20, mid_y - 20)
                self.scene.addItem(label)

    def highlight_state(self, state):
        for s, item in self.state_items.items():
            item.setBrush(QBrush(QColor("#ffffff")))
            if s == state:
                item.setBrush(QBrush(QColor("#aaffaa")))

    def update_stack_view(self):
        for item in self.stack_items:
            self.scene.removeItem(item)
        self.stack_items = []

        stack = list(reversed(self.automaton.stack))
        x = 500
        y = 50

        for symbol in stack:
            rect = QGraphicsRectItem(x, y, 50, 30)
            rect.setBrush(QBrush(QColor("#eee")))
            rect.setPen(QPen(Qt.black))
            self.scene.addItem(rect)

            txt = QGraphicsTextItem(symbol)
            txt.setFont(QFont("Arial", 12))
            txt.setPos(x + 15, y + 5)
            self.scene.addItem(txt)

            self.stack_items.append(rect)
            self.stack_items.append(txt)
            y += 35

    def start_automaton(self):
        string = self.input_field.text()
        if not string:
            self.log.addItem("Erro: cadeia vazia.")
            return

        self.automaton.load_input(string)
        self.update_stack_view()
        self.highlight_state(self.automaton.state)
        self.log.clear()
        self.log.addItem(f"Entrada: '{string}'")

        self.btn_step.setEnabled(True)
        self.btn_run.setEnabled(True)

    def step_automaton(self):
        success, msg = self.automaton.step()
        self.highlight_state(self.automaton.state)
        self.update_stack_view()
        self.log.addItem(msg)

        if self.automaton.is_finished() or not success:
            self.btn_step.setEnabled(False)
            self.btn_run.setEnabled(False)
            result = "✅ Aceita" if self.automaton.is_accepted() else "❌ Rejeitada"
            self.log.addItem(result)

    def run_automaton(self):
        while not self.automaton.is_finished():
            success, _ = self.automaton.step()
            if not success:
                break
        self.highlight_state(self.automaton.state)
        self.update_stack_view()
        self.log.addItem("Execução completa.")
        result = "✅ Aceita" if self.automaton.is_accepted() else "❌ Rejeitada"
        self.log.addItem(result)
        self.btn_step.setEnabled(False)
        self.btn_run.setEnabled(False)

    def reset_automaton(self):
        self.automaton.reset()
        self.log.clear()
        self.update_stack_view()
        self.highlight_state(self.automaton.state)
        self.btn_step.setEnabled(False)
        self.btn_run.setEnabled(False)
