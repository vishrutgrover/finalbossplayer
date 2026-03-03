<p align="center">
  <img src="apogee.png" alt="APOGEE 2024 - A Celestial Epiphany" width="100%">
</p>

# FinalBossPlayer

This repo contains our submissions for the Silicon Chip Smackdown at APOGEE 24 and APOGEE 25. AI poker agents that play Texas Hold'em.

## Structure

- **aipoker24** - Our APOGEE 24 submission. Monte Carlo based final-agent, ML hand recognition experiments, PyPokerEngine stuff. Kept for reference.
- **aipoker25** - Our APOGEE 25 submission. The winning one. AllInCounterBot in try1.py.

## The Winning Bot: AllInCounterBot

The bot that won is built to counter opponents who go all-in a lot, especially pre-flop. Beyond that it plays a solid adaptive game post-flop and tries to spot aggressive betting.

### Pre-Flop (before community cards)

Only knows its two hole cards. Ranks them by strength: pairs (high pairs strong, low pairs decent), suited cards, connected cards, high cards.

**Facing an all-in:** This is where it shines. It calls all-ins with a wider range than normal. Any pair, strong Aces like AT or better, good suited connectors like KQs. If the hand meets the threshold it calls, otherwise folds.

**Facing a normal bet/raise:** Premium hands (QQ+, AK) it re-raises or shoves. Good but not premium hands it calls. Weak hands it folds.

**No bet yet:** Good hands it opens 3-4x big blind. Weak hands it checks.

### Post-Flop (after community cards)

Uses a hand evaluator to get its best five-card hand and assigns a confidence score. Also detects if the opponent is betting aggressively (large vs blind, large vs pot, or all-in).

**Strong hands (two pair or better):** Bets for value, usually raises when facing a bet. Sometimes traps by just calling when it has a monster and the opponent is aggressive.

**Medium hands:** Checks when no bet. When facing a bet, calls more often if the bet looks aggressive (might be getting odds or opponent bluffing). Folds if the bet is big and not aggressive, or hand is on the weaker side.

**Weak hands:** Usually folds. One exception: "hero call" when opponent goes all-in, we only have Ace-high, and the call is 15% or less of our stack. Banking on them bluffing with worse.

There's a tiny bit of randomness in bet sizing with very strong hands to stay less predictable.

### How it adapts

Doesn't learn opponent profiles over multiple hands. Adapts within each hand based on the situation. Pre-flop it's always ready with that wider all-in calling range. Post-flop it dynamically flags aggressive bets and adjusts: more willing to call medium hands vs aggression, more likely to raise or trap with strong hands.

## Project Structure

```
finalbossplayer/
├── apogee.png
├── README.md
├── aipoker24/           <- old code (Monte Carlo agent, research)
│   └── final-agent.py
├── aipoker25/           <- winning submission
│   └── try1.py         <- AllInCounterBot
└── research/            <- ML hand recognition, PyPokerEngine experiments
    ├── handreco/
    ├── ai-poker-2024/
    └── pypoks/          <- submodule: https://github.com/piteren/pypoks
```

## Dependencies

- Python 3.x
- aipoker24 uses [PyPokerEngine](https://github.com/ishikota/PyPokerEngine) and NumPy
- aipoker25 uses the competition's game engine (player, game, card, hand_evaluator modules)