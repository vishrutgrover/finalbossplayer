<p align="center">
  <img src="apogee.png" alt="APOGEE 2024 - A Celestial Epiphany" width="100%">
</p>

# FinalBossPlayer

This repo contains our submissions for the Silicon Chip Smackdown at APOGEE 24 and APOGEE 25. AI poker agents that play Texas Hold'em.

## Structure

- **aipoker24** - Our APOGEE 24 submission. Monte Carlo based final-agent, ML hand recognition experiments, PyPokerEngine stuff. Kept for reference.
- **aipoker25** - Our APOGEE 25 submission. The winning one. craziBot.py.

## APOGEE 25 Winner: craziBot (AllInCounterBot)

**What was novel:** The hero call. When an opponent goes all-in and we only have Ace-high (no pair), we call if the cost is 15% or less of our stack. Most bots fold here. We're banking on them bluffing with worse. It paid off.

**Why it won:** The competition had a lot of all-in heavy bots. craziBot is built to counter that. Pre-flop it calls all-ins with a wider range than normal (any pair, AT+, KQs). Post-flop it detects aggressive bets and calls more with medium hands when it suspects a bluff. The hero call sealed it when others folded Ace-high to bluffs.

Runs on the [AI Poker 2025](https://github.com/Tanish-0001/AI-Poker-2025) engine.

## Project Structure

```
finalbossplayer/
├── apogee.png
├── README.md
├── aipoker24/           <- APOGEE 24 (Monte Carlo agent)
│   └── final-agent.py
├── aipoker25/           <- APOGEE 25 winner
│   └── craziBot.py
└── research/            <- ML hand recognition, PyPokerEngine experiments
    ├── handreco/
    ├── ai-poker-2024/
    └── pypoks/          <- submodule: https://github.com/piteren/pypoks
```

## Dependencies

- Python 3.x
- aipoker24 uses [PyPokerEngine](https://github.com/ishikota/PyPokerEngine) and NumPy
- aipoker25 uses [AI Poker 2025](https://github.com/Tanish-0001/AI-Poker-2025) engine (player, game, card, hand_evaluator modules)
