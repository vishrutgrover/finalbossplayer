from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 1000

class FinalBossPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=self.nb_player,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
                )
        if win_rate >= 0.9:
            action = valid_actions[2]
            max_raise = valid_actions[2]['amount']['max']
            min_raise = valid_actions[2]['amount']['min']
            return action['action'], max_raise
        elif win_rate >= 0.8:
            action = valid_actions[2]
            max_raise = valid_actions[2]['amount']['max']
            min_raise = valid_actions[2]['amount']['min']
            return action['action'], round((max_raise+min_raise)/2.5)
        elif win_rate >= 0.7:
            action = valid_actions[2]
            max_raise = valid_actions[2]['amount']['max']
            min_raise = valid_actions[2]['amount']['min']
            return action['action'], round((max_raise+min_raise)/2.8)
        elif win_rate >= 0.1:
            action = valid_actions[1]  # fetch CALL action info
        elif win_rate < 0.1:
            action = valid_actions[0]  # fetch FOLD action info
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