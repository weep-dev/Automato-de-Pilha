# Exemplo para linguagem aⁿbⁿ

transitions = {
    ('q0', 'a', 'ε'): ('q0', 'A'),
    ('q0', 'b', 'A'): ('q1', 'POP'),
    ('q1', 'b', 'A'): ('q1', 'POP'),
}

start_state = 'q0'
accept_states = ['q1']
