import numpy as np
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 1000

class FinalBossNewPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=self.nb_player,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        is_bluffing = np.random.randint(0, 100) < 0
        is_going_all_in = np.random.randint(0, 100) < 0

        max_raise = valid_actions[2]['amount']['max']
        min_raise = valid_actions[2]['amount']['min']

        if win_rate<0.7 and valid_actions[1]['amount'] > (max_raise+min_raise)/2:
            action = valid_actions[0]
            return action['action'], action['amount']
        if win_rate >= 0.9 or is_going_all_in:
            action = valid_actions[2]
            return action['action'], max_raise
        elif win_rate >= 0.75 or (win_rate < 0.8 and is_bluffing):
            action = valid_actions[2]
            raise_amount = round((max_raise+min_raise)/3 + min_raise)
            if is_bluffing:
                raise_amount = max_raise
            return action['action'], raise_amount
        elif win_rate >= 0.5:
            action = valid_actions[2]
            raise_amount = min_raise
            return action['action'], raise_amount
        elif win_rate >= 0.2:
            action = valid_actions[1]
            return action['action'], action['amount']
        else:
            action = valid_actions[0]
            return action['action'], action['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
