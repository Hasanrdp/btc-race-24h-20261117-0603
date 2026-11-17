"""DipHold: a buy-the-dip-and-hold BTC bot for make.fun btc-race-24h-20261117-0603.

Strategy, in one paragraph: wait for the first modest intraday dip, buy
Coinbase Wrapped BTC (CBBTC) with all cash, then hold it to the end of the
24-hour race window. No take-profit, no trailing stop, no time stop, no
second trade. The race is won by whoever is long through the window's net
move, and every extra round trip pays ~26 bps in fees, slippage and price
impact, so the bot trades exactly once.

Entry rule (decided on bar k, filled at bar k+1's open):
  * Flat and the latest close is at least DIP_BPS (30 bps, 0.30%) below the
    highest close of the trailing WINDOW (120) bars -> buy 100% of cash.
  * Fallback: still flat at bar FALLBACK_BAR (1000) or later and the close
    is at least FALLBACK_DIP_BPS (15 bps) below that trailing high -> buy
    100% of cash. This only fires on a window so strong it never dipped
    0.30%, so the bot still meets the race's minimum-trade bar instead of
    sitting in cash all day.

No exit rule: once long the bot sends no further orders. The harness
flattens the position at the final close. A long-only bot cannot be hurt by
a whipsawed exit, and on the previous race (btc-race-24h-20261115-0828) the
profitable entries were exactly the ones that bought once and held, while
our aggressive time stop sold too early and missed the late surge.

Determinism: the decision is a pure integer function of the closes seen so
far. No clock, no environment, no randomness, no network, no files. Two
executions on the same bars produce the same orders byte for byte.

Runtime: Python 3.13, standard library only, via the kit's vendored shim
(vendor/makefun_bars.py, copied byte for byte from the kit's sdk/).
The grader runs: python3 -P -s /bot/main.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"

# Buy when the close is this far below the trailing high (basis points).
DIP_BPS = 30
# Trailing-high lookback, in bars (120 minutes = 2 hours).
WINDOW = 120
# If still flat this late, accept a shallower dip so the bot always trades.
FALLBACK_BAR = 1000
FALLBACK_DIP_BPS = 15
# Largest move past the latest close a fill may suffer before it is refused.
MAX_SLIPPAGE_BPS = 200

# Closes seen so far, oldest first. Appended in batch order; the bot's only
# memory, and a pure function of the bars the harness sent.
_closes = []


def _dip_bps(close):
    """How far (basis points, integer) the close sits below the trailing high."""
    window = _closes[-WINDOW:] if len(_closes) > WINDOW else _closes
    high = max(window)
    if high <= 0 or close >= high:
        return 0
    return (high - close) * 10000 // high


def on_batch(state, batch):
    # Orders decided on a warm-up batch are rejected, so send none.
    if state.warming_up:
        return []
    bar = state.latest.get(SYMBOL)
    if bar is None:
        return []
    close = int(bar["c"])
    _closes.append(close)

    # Already long: hold to the end. No take-profit, no stop, no time exit.
    if SYMBOL in state.positions:
        return []

    dip = _dip_bps(close)
    buy = dip >= DIP_BPS
    if not buy and state.seq >= FALLBACK_BAR:
        buy = dip >= FALLBACK_DIP_BPS
    if not buy:
        return []

    cash = state.cash
    if cash <= 0:
        return []
    return [
        {
            "side": "buy",
            "symbol": SYMBOL,
            "notional_quote_units": cash,
            "max_slippage_bps": MAX_SLIPPAGE_BPS,
        }
    ]


makefun_bars.run(on_batch)
