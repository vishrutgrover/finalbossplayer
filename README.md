<p align="center">
  <img src="apogee.png" alt="APOGEE 2024 - A Celestial Epiphany" width="100%">
</p>

# FinalBossPlayer

Our submission for the Silicon Chip Smackdown at APOGEE 2024. It's an AI poker agent that plays Texas Hold'em in the PyPokerEngine game.py environment.

## Overview

We tried a bunch of different approaches for this. Started with ML for hand recognition, messed around with Monte Carlo simulations, and eventually landed on final-agent as our submission. It's pretty simple: no learned models, just win rate estimation from simulations.

## Research Journey

### 1. Hand Recognition with ML

First thing we looked at was using ML for poker hand evaluation (in research/handreco/). We built an MLP in PyTorch to classify hand ranks like Straight Flush, Four of a Kind, Full House, etc. Trained it on a poker dataset and wanted to see if learned hand strength could help with decisions. It was interesting but we didn't end up using it in the final thing.

### 2. PyPokerEngine Deep Dive

We spent some time digging into how PyPokerEngine actually works. The main thing we cared about was estimate_hole_card_win_rate(), which runs Monte Carlo simulations to guess your win probability. Also looked at the hand evaluator, card utils, and how the BasePokerPlayer interface works.

### 3. Hybrid ML + Monte Carlo

At some point we tried combining both. Monte Carlo for win rate, MLP to predict whether to fold/call/raise, plus some hand strength features. We had MLPPokerPlayer and finalboss.py doing this. In the end the ML part just added complexity without really helping much in this setup.

### 4. Pure Monte Carlo

So we dropped the ML and went with a rule-based strategy that only uses Monte Carlo win rates. Way simpler, easier to debug, and it actually did well in round robin against the other submissions.

## Final Submission: final-agent.py

This is what we submitted. The logic is basically:

| Win Rate | Action |
|----------|--------|
| 90%+ | Raise max / all in |
| 75%+ | Raise moderate amount |
| 50%+ | Raise minimum |
| 20%+ | Call |
| below 20% | Fold |
| below 70% + call is expensive | Fold (protect stack) |

We run 1000 simulations per decision with estimate_hole_card_win_rate, use the built-in gen_cards and stuff from PyPokerEngine. Extends BasePokerPlayer, implements declare_action. No external models or heavy deps.

## Project Structure

```
finalbossplayer/
├── apogee.png
├── final-agent.py       <- the submission
├── README.md
└── research/
    ├── handreco/        <- ML hand recognition stuff
    │   └── reco.ipynb
    └── ai-poker-2024/   <- competition env and our iterations
        ├── game.py
        ├── submissions/
        └── examples/players/
```

## Usage

Need PyPokerEngine installed. Then just register FinalBossNewPlayer in your game config:

```python
from pypokerengine.api.game import setup_config, start_poker
from examples.players.final_agent import FinalBossNewPlayer

config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=10)
config.register_player(name="finalboss", algorithm=FinalBossNewPlayer())
# add other players...
game_result = start_poker(config, verbose=1)
```

## Dependencies

- Python 3.x
- [PyPokerEngine](https://github.com/ishikota/PyPokerEngine)
- NumPy

Built for APOGEE 2024, 42nd edition, 4th-7th April.