from PyQt5.QtWidgets import QApplication
from visualizer import AutomatonVisualizer
import sys
from automaton import PushdownAutomaton
from config import transitions, start_state, accept_states

if __name__ == "__main__":
    app = QApplication(sys.argv)

    automaton = PushdownAutomaton(transitions, start_state, accept_states)
    window = AutomatonVisualizer(automaton)
    window.show()

    sys.exit(app.exec_())
