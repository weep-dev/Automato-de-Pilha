class PushdownAutomaton:
    def __init__(self, transitions, start_state, start_stack_symbol, accept_states):
        self.transitions = transitions
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.accept_states = accept_states

    def process(self, input_string):
        from collections import deque

        initial_config = (self.start_state, 0, [self.start_stack_symbol])
        queue = deque([initial_config])

        while queue:
            state, pos, stack = queue.popleft()

            if pos == len(input_string) and state in self.accept_states and (not stack or stack == ['ε']):
                return True

            stack_top = stack[-1] if stack else 'ε'

            possible_inputs = []
            if pos < len(input_string):
                possible_inputs.append(input_string[pos])
            possible_inputs.append('ε')

            for input_symbol in possible_inputs:
                key = (state, input_symbol, stack_top)
                if key in self.transitions:
                    for next_state, stack_action in self.transitions[key]:
                        new_stack = stack.copy()

                        if stack_action == 'POP':
                            if not new_stack:
                                continue
                            new_stack.pop()
                        elif stack_action != 'ε':
                            new_stack.append(stack_action)

                        new_pos = pos + (1 if input_symbol != 'ε' else 0)
                        queue.append((next_state, new_pos, new_stack))

        return False


# Linguagem aⁿbⁿ

transitions = {
    ('q0', 'a', 'ε'): [('q0', 'A')],
    ('q0', 'a', 'A'): [('q0', 'A')],  
    ('q0', 'b', 'A'): [('q1', 'POP')],
    ('q1', 'b', 'A'): [('q1', 'POP')],
}

start_state = 'q0'
start_stack_symbol = 'ε'
final_states = {'q1'}

pda = PushdownAutomaton(transitions, start_state, start_stack_symbol, final_states)

testes = ["ab", "aabb", "aaabbb", "aabbb", "aaabb", "ba", ""]

for teste in testes:
    resultado = "aceita" if pda.process(teste) else "rejeita"
    print(f"Entrada '{teste}': {resultado}")
