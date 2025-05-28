class PushdownAutomaton:
    def __init__(self, transitions, start_state, accept_states):
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.reset()

    def reset(self):
        self.state = self.start_state
        self.stack = []
        self.index = 0
        self.input_string = ""
        self.log = []

    def load_input(self, input_string):
        self.reset()
        self.input_string = input_string

    def step(self):
        if self.index >= len(self.input_string):
            return False, "Fim da entrada."

        symbol = self.input_string[self.index]
        stack_top = self.stack[-1] if self.stack else ''

        key = (self.state, symbol, stack_top)
        if key in self.transitions:
            next_state, stack_op = self.transitions[key]
            self.state = next_state

            if stack_op == 'POP' and self.stack:
                self.stack.pop()
            elif stack_op != 'ε':
                self.stack.append(stack_op)

            self.index += 1
            self.log.append(f"Lido '{symbol}': transição para {next_state}, operação: {stack_op}")
            return True, self.log[-1]
        else:
            return False, f"Erro: transição indefinida para ({self.state}, {symbol}, {stack_top})"

    def is_finished(self):
        return self.index >= len(self.input_string)

    def is_accepted(self):
        return self.state in self.accept_states and not self.stack
