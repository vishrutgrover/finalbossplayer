import random
from typing import List, Tuple

from player import Player, PlayerAction, PlayerStatus
from game import GamePhase
from card import Card, Rank, Suit
from hand_evaluator import HandEvaluator, HandRank, HandResult

# Helper function to convert card index back to Card object
def index_to_card(index: int) -> Card | None:
    """Converts a card index (0-51) back to a Card object."""
    if index < 0 or index > 51: return None
    suit_value = index // 13
    rank_value_internal = index % 13
    try:
        suit = Suit(suit_value)
        rank = Rank(rank_value_internal + 2)
        return Card(rank, suit)
    except ValueError: return None

class AllInCounterBot(Player): # Renamed
    """
    A bot designed to counter frequent all-in shoves, particularly pre-flop,
    while maintaining adaptive aggression detection post-flop.
    """

    # Threshold for calling PRE-FLOP all-ins (lower than calling normal raises)
    PREFLOP_ALLIN_CALL_CONFIDENCE_THRESHOLD = 0.38 # e.g., Allows AJo, ATs, KQs, 77+

    # Threshold for HERO CALLING post-flop all-ins with weak hands (as % of stack)
    POSTFLOP_HERO_CALL_ALLIN_STACK_PCT = 0.15 # Call all-in with Ace high if cost <= 15% stack


    def _get_preflop_confidence(self, hole_cards: List[Card]) -> float:
        """ Calculates confidence (0.0-1.0) based only on hole cards. (Same as AdaptivePreflopBot) """
        if not hole_cards or len(hole_cards) != 2: return 0.0
        card1, card2 = hole_cards[0], hole_cards[1]
        rank1, rank2 = sorted([card1.rank.value, card2.rank.value], reverse=True)
        is_suited = card1.suit == card2.suit
        is_pair = rank1 == rank2
        gap = rank1 - rank2 -1 if rank1 > rank2 else 0

        if is_pair:
            if rank1 >= Rank.TEN.value: return 0.85 # TT+
            if rank1 >= Rank.SEVEN.value: return 0.60 # 77-99
            return 0.40 # 22-66 (Threshold is 0.38, so calls 77+)

        if is_suited:
            if rank1 >= Rank.QUEEN.value: return 0.65 + (rank1 - Rank.QUEEN.value) * 0.1 # AQ+, KQ+ (Calls KQ+)
            if rank1 >= Rank.TEN.value and rank2 >= Rank.NINE.value: return 0.50 - gap * 0.05 # T9s+ (Calls T9s+)
            if rank1 == Rank.ACE.value and rank2 >= Rank.TEN.value: return 0.55 # ATs+ (Calls ATs+)
            if rank1 == Rank.ACE.value: return 0.45 # A2s-A9s (Calls these)
            return 0.25

        # Offsuit High Cards / Connectors
        if rank1 >= Rank.QUEEN.value and rank2 >= Rank.TEN.value: return 0.35 + (rank1 - Rank.QUEEN.value)*0.05 - (rank2 - Rank.TEN.value)*0.02 # KQo, AJo+ (Calls AJo+)
        if rank1 == Rank.ACE.value and rank2 >= Rank.TEN.value: return 0.40 # ATo+ (Calls ATo+)
        if rank1 == Rank.ACE.value: return 0.20 # A2o-A9o
        if rank1 >= Rank.TEN.value and rank2 >= Rank.EIGHT.value and gap <= 1: return 0.15 - gap * 0.05

        return 0.05


    def _get_postflop_confidence(self, hand_result: HandResult, community_cards: List[Card]) -> float:
        """ Calculates post-flop confidence score (0.0 to 1.0). Applies randomness if >= 0.8. (Same as AdaptivePreflopBot) """
        if not hand_result: return 0.0
        rank = hand_result.hand_rank
        value = hand_result.hand_value
        calculated_confidence = 0.0

        if rank == HandRank.HIGH_CARD: calculated_confidence = 0.05 if value and value[0] == Rank.ACE.value else 0.01
        elif rank == HandRank.PAIR:
            score = 0.10
            if value:
                pair_rank = value[0]
                score += (pair_rank - 2) * 0.01
                if community_cards:
                    highest_community = max((c.rank.value for c in community_cards), default=0)
                    if pair_rank > highest_community: score += 0.05
                    elif pair_rank == highest_community: score += 0.03
            calculated_confidence = min(score, 0.30)
        elif rank == HandRank.TWO_PAIR:
             score = 0.30
             if value: score += (value[0] - 2) * 0.005 + (value[1] - 2) * 0.005
             calculated_confidence = min(score, 0.45)
        elif rank == HandRank.THREE_OF_A_KIND:
             score = 0.45 + (value[0] - 2) * 0.01 if value else 0.45
             calculated_confidence = min(score, 0.60)
        elif rank == HandRank.STRAIGHT: calculated_confidence = 0.60 + (value[0] - 5) * 0.01 if value else 0.60
        elif rank == HandRank.FLUSH:
             score = 0.65 + (value[0] - 7) * 0.01 if value else 0.65
             calculated_confidence = min(score, 0.75)
        elif rank == HandRank.FULL_HOUSE:
             score = 0.75 + (value[0] - 2) * 0.01 if value else 0.75
             calculated_confidence = min(score, 0.85)
        elif rank == HandRank.FOUR_OF_A_KIND: calculated_confidence = 0.85 + (value[0] - 2) * 0.005 if value else 0.85
        elif rank == HandRank.STRAIGHT_FLUSH: calculated_confidence = 0.95
        elif rank == HandRank.ROYAL_FLUSH: calculated_confidence = 1.0

        if calculated_confidence >= 0.80: return random.uniform(0.80, 1.0)
        else: return calculated_confidence


    def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:

        # --- 1. Parse Game State ---
        hole_card_indices = game_state[0:2]
        community_card_indices_raw = game_state[2:7]
        pot = game_state[7]
        current_total_bet = game_state[8]
        big_blind = game_state[9]
        my_stack = self.stack
        my_current_bet = self.bet_amount

        call_amount = max(0, current_total_bet - my_current_bet)
        can_check = (call_amount <= 0)
        min_bet = max(big_blind, 1)

        player_cards: List[Card] = [card for idx in hole_card_indices if (card := index_to_card(idx)) is not None]
        community_cards: List[Card] = [card for idx in community_card_indices_raw if (card := index_to_card(idx)) is not None]

        is_preflop = (len(community_cards) == 0)

        # --- Determine if facing an all-in this round ---
        is_facing_all_in_this_round = False
        opponent_shove_amount = 0 # How much total did the opponent bet who shoved?
        current_phase_str = action_history[-1][0] if action_history else GamePhase.PRE_FLOP.value
        # Find the last opponent action in the current phase
        last_opp_action = None
        last_opp_total_bet = 0 # Track total bet of last acting opponent
        temp_player_bets = {p.name: 0 for p in self.players} if hasattr(self, 'players') else {} # Need player list for this

        for i in range(len(action_history) - 1, -1, -1):
             phase, name, action_str, amt_delta = action_history[i]
             if phase != current_phase_str: break # Stop when phase changes
             # Update running bet total for the player
             #if name in temp_player_bets: temp_player_bets[name] += amt_delta

             if name != self.name: # If it's an opponent's action
                 action_enum = PlayerAction(action_str)
                 last_opp_action = action_enum
                 #last_opp_total_bet = temp_player_bets.get(name, 0) # Rough total bet
                 last_opp_total_bet = current_total_bet # Simplification: Assume the current_total_bet reflects their shove amount
                 if action_enum == PlayerAction.ALL_IN:
                      is_facing_all_in_this_round = True
                      opponent_shove_amount = current_total_bet # Assume current_total_bet is their shove amount
                 break # Found the last opponent action


        # --- ====== PRE-FLOP LOGIC ====== ---
        if is_preflop:
            if not player_cards: return PlayerAction.CHECK if can_check else PlayerAction.FOLD, 0

            preflop_confidence = self._get_preflop_confidence(player_cards)

            # Calculate standard raise size
            last_raise_amount = 0 # Find size of last bet/raise
            if not can_check: # Only needed if facing bet
                # Simplified: use current_total_bet if someone raised before us
                last_raise_amount = current_total_bet if current_total_bet > big_blind else 0

            min_raise = max(big_blind * 2, last_raise_amount * 2) if last_raise_amount > 0 else big_blind * 3
            standard_raise = min(my_stack + my_current_bet, max(min_raise, big_blind * 3))
            if preflop_confidence > 0.8: standard_raise = min(my_stack + my_current_bet, max(min_raise, big_blind * 4))

            # --- Pre-flop Actions ---
            if can_check: # Facing no bet
                if preflop_confidence >= 0.50: # Raise good hands
                    raise_amount_needed = standard_raise - my_current_bet
                    if raise_amount_needed <= 0: return PlayerAction.CHECK, 0
                    if raise_amount_needed >= my_stack: return PlayerAction.ALL_IN, my_stack
                    return PlayerAction.RAISE, standard_raise
                else: return PlayerAction.CHECK, 0
            else: # Facing a bet/raise

                # *** Specific Logic for Facing Pre-flop All-In ***
                if is_facing_all_in_this_round:
                    # Wider calling range here
                    if preflop_confidence >= self.PREFLOP_ALLIN_CALL_CONFIDENCE_THRESHOLD:
                         # print(f"DEBUG: Calling Preflop All-In! Conf: {preflop_confidence:.2f}, Thresh: {self.PREFLOP_ALLIN_CALL_CONFIDENCE_THRESHOLD}")
                         if call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack # Our call is all-in
                         return PlayerAction.CALL, call_amount # Call their all-in
                    else:
                         # print(f"DEBUG: Folding Preflop All-In! Conf: {preflop_confidence:.2f}, Thresh: {self.PREFLOP_ALLIN_CALL_CONFIDENCE_THRESHOLD}")
                         return PlayerAction.FOLD, 0
                # *** End Specific All-In Logic ***

                # --- Logic for Facing Normal Pre-flop Bet/Raise ---
                else:
                    if preflop_confidence >= 0.75: # Re-raise premium hands
                        reraise_target = max(min_raise * 2, current_total_bet * 3)
                        reraise_target = min(my_stack + my_current_bet, reraise_target)
                        if reraise_target - my_current_bet < my_stack and reraise_target > current_total_bet:
                             return PlayerAction.RAISE, reraise_target
                        else: # Cannot afford reraise -> Shove
                             if my_stack > call_amount: return PlayerAction.ALL_IN, my_stack
                             elif call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack # Call is all-in
                             else: return PlayerAction.FOLD, 0
                    elif preflop_confidence >= 0.45: # Call raises with decent hands
                        if call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack
                        return PlayerAction.CALL, call_amount
                    else: # Fold weak hands to normal raises
                        return PlayerAction.FOLD, 0

        # --- ====== POST-FLOP LOGIC ====== ---
        else:
            if not player_cards: return PlayerAction.CHECK if can_check else PlayerAction.FOLD, 0

            hand_result = HandEvaluator.evaluate_hand(player_cards, community_cards)
            postflop_confidence = self._get_postflop_confidence(hand_result, community_cards)

            # --- ADAPTIVE AGGRESSION DETECTION (using POST-FLOP confidence) ---
            # (is_facing_all_in_this_round already calculated above)
            facing_aggressive_bet = False # Reset for post-flop check

            if not can_check and call_amount > 0:
                # Adaptive Threshold Calculation (Same as before)
                base_bb_multiplier = 3.0; base_pot_fraction = 0.75
                bb_scale_factor = 2.0; pot_scale_factor = 0.5
                dynamic_bb_multiplier = max(1.5, min(6.0, base_bb_multiplier + bb_scale_factor * (0.5 - postflop_confidence)))
                dynamic_pot_fraction = max(0.3, min(1.5, base_pot_fraction + pot_scale_factor * (0.5 - postflop_confidence)))
                adaptive_bb_threshold = big_blind * dynamic_bb_multiplier
                pot_before_action = max(0, pot - call_amount)
                adaptive_pot_threshold_value = max(big_blind, pot_before_action * dynamic_pot_fraction)

                # Determine Aggression (Post-flop specific check)
                is_aggressive_vs_bb = current_total_bet > adaptive_bb_threshold
                is_aggressive_vs_pot = current_total_bet > adaptive_pot_threshold_value
                if is_facing_all_in_this_round or is_aggressive_vs_bb or is_aggressive_vs_pot:
                    facing_aggressive_bet = True # Use this combined flag for general response
            # --- End Adaptive Aggression Detection ---


            # --- POST-FLOP ACTION LOGIC (Using ConfidenceBotPlayer structure, slightly adjusted hero call) ---

            # A) Strong Hands (Confidence >= 0.5)
            if postflop_confidence >= 0.5:
                if can_check: # Bet strong
                     bet_fraction = 0.5 + (postflop_confidence - 0.5) * 0.8
                     bet_amount = min(my_stack, max(min_bet, int(pot * bet_fraction)))
                     if bet_amount >= my_stack: return PlayerAction.ALL_IN, my_stack
                     if bet_amount > 0: return PlayerAction.BET, bet_amount
                     else: return PlayerAction.CHECK, 0
                else: # Facing bet/raise - Mostly raise/shove, rarely trap
                     should_trap = facing_aggressive_bet and postflop_confidence > 0.85 and not is_facing_all_in_this_round
                     if should_trap:
                          if call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack
                          return PlayerAction.CALL, call_amount
                     else: # Raise or Shove
                          raise_multiplier = 1.5 + postflop_confidence
                          raise_target = current_total_bet * raise_multiplier
                          min_legal_raise_target = current_total_bet + max(big_blind, call_amount)
                          final_raise_target = max(raise_target, min_legal_raise_target)

                          if final_raise_target - my_current_bet < my_stack and final_raise_target > current_total_bet:
                               return PlayerAction.RAISE, int(final_raise_target)
                          else: # Cannot afford raise -> Call or Shove
                               if my_stack > call_amount: # Can we beat the current bet?
                                   return PlayerAction.ALL_IN, my_stack # Shove strong hands if can't make desired raise but > call
                               else: # Cannot afford call
                                    if call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack # Call IS all-in
                                    else: return PlayerAction.FOLD, 0

            # B) Medium Hands (Confidence ~0.1 to 0.5)
            elif postflop_confidence >= 0.1:
                 if can_check: # Check/Fold logic, maybe bet weak draws? No, keep simple. Check.
                      return PlayerAction.CHECK, 0
                 else: # Facing bet/raise - Use adaptive calling threshold
                      base_call_pct = 0.10
                      # Call wider vs ANY perceived aggression (including all-in)
                      if facing_aggressive_bet: bonus_pct = postflop_confidence * 0.8
                      else: bonus_pct = postflop_confidence * 0.4
                      call_threshold_pct = base_call_pct + bonus_pct
                      is_small_bet = (call_amount <= big_blind * 2)

                      if call_amount > 0 and (call_amount <= my_stack * call_threshold_pct or (is_small_bet and call_amount < my_stack)):
                           if call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack
                           return PlayerAction.CALL, call_amount
                      else: return PlayerAction.FOLD, 0

            # C) Weak Hands (Confidence < 0.1)
            else:
                 if can_check: return PlayerAction.CHECK, 0
                 else: # Facing bet/raise
                      # *** Adjusted Hero Call Logic ***
                      # Consider calling ONLY if facing an all-in, with Ace high, and within stack % threshold
                      is_ace_high = hand_result and hand_result.hand_rank == HandRank.HIGH_CARD and hand_result.hand_value[0] == Rank.ACE.value
                      if is_facing_all_in_this_round and is_ace_high \
                         and call_amount <= my_stack * self.POSTFLOP_HERO_CALL_ALLIN_STACK_PCT:
                           # print(f"DEBUG: HERO CALL Postflop All-In! Cost: {call_amount}, Stack Threshold: {my_stack * self.POSTFLOP_HERO_CALL_ALLIN_STACK_PCT}")
                           if call_amount >= my_stack: return PlayerAction.ALL_IN, my_stack
                           return PlayerAction.CALL, call_amount
                      else: # Fold weak hands to any normal bet or unaffordable/non-AceHigh all-in
                           return PlayerAction.FOLD, 0

            # Fallback Post-flop
            return PlayerAction.CHECK if can_check else PlayerAction.FOLD, 0