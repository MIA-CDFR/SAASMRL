
class UserProfile:
    def __init__(self, user_id):
        self.user_id = user_id
        self.q_table = {}  # {(state, action): value}
        self.last_state = None
        self.last_action = None

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0)

    def update_q(self, state, action, reward, alpha=0.1):
        old_q = self.get_q(state, action)
        new_q = old_q + alpha * (reward - old_q)
        self.q_table[(state, action)] = new_q

    def choose_action(self, state):
        actions = ["match", "wait"]

        # escolher melhor ação
        best = None
        best_value = -999

        for a in actions:
            q = self.get_q(state, a)
            if q > best_value:
                best_value = q
                best = a

        return best