[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/Hasanrdp/btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/Hasanrdp/btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

# DipHold — btc-race-24h-20261117-0603

[![make.fun](https://img.shields.io/badge/make.fun-btc--race--24h--20261117--0603-blue)](https://make.fun/bounty/btc-race-24h-20261117-0603)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![simulation only](https://img.shields.io/badge/trading-simulation%20only-green)](https://make.fun/bounty/btc-race-24h-20261117-0603)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A BTC trading bot for the make.fun `btc-race-24h-20261117-0603` competition.
It trades Coinbase Wrapped BTC (cbBTC) minute by minute against real on-chain
prices, starting with $1,000 of paper money. Simulation only — nothing is
traded for real.

## Strategy

Buy the first modest dip, then hold to the end — one trade, no exits:

- **Entry:** the close is at least 0.30% below the highest close of the
  trailing 120 bars. Buy with all cash (one open position at most, long only).
- **Fallback:** still flat at bar 1000 and the close is at least 0.15% below
  that trailing high — buy with all cash, so the bot always trades at least
  once even on a window that never dips 0.30%.
- **Exit:** none. No take-profit, no stop, no time stop. The harness flattens
  the position at the final close. Every extra round trip pays ~26 bps in
  fees, slippage and price impact, and on the previous race
  (`btc-race-24h-20261115-0828`) the profitable entries were the ones that
  bought once and held, while an aggressive time stop sold too early and
  missed the late surge.
- **Slippage cap:** 200 bps past the close each order was decided on.

Local verification on the published frozen dev window: a protocol-level
replay of the real `main.py` through all 1,440 bars (kit's fill model: 4 bps
fee, 2 bps slippage, constant-product price impact, fills at the next bar's
open, flatten at the final close) gives net PnL **+$4.12** on $1,000,
1 trade, max drawdown 2.12% — above the dev gate (net PnL > $0), so the
entry races. Two runs produce byte-identical action logs (deterministic).
The kit's `grade-local --driver docker` is the official check; it could not
run in this VM (no Docker, and the process driver runs Node bots only), so
it should be run at submission time if Docker is available. For calibration,
the same replay model reproduces the kit's own buy-and-hold baseline grade
(+$1.07) to the cent.

## Run

```sh
python3 -P -s main.py
```

Python 3.13, standard library only. The bot speaks `agent-fun/bars-replay/v1`
(newline-delimited JSON on stdin/stdout); `vendor/makefun_bars.py` is the
kit's SDK shim copied byte for byte. Decisions are a pure integer function
of the closes seen so far: no clock, no randomness, no network, no files —
two executions on the same bars produce the same orders.

## Files

- `main.py` — the bot
- `vendor/makefun_bars.py` — the kit's protocol shim (vendored, unmodified)
- `.makefun/owner.json` — payout wallet (Solana)
- `LICENSE` — MIT
