# AGENTS.md

## Setup
```bash
pip install -r Script/requirements.txt
```

## Entry Points
- `Chan.py` - Core Chan analysis class for stock data processing
- `a_replay.py` - Runs replay visualization server (calls `run_dev_server()`)

## Project Structure
- `DataAPI/` - Stock data sources (BaoStock, Akshare, CommonStockAPI, CCXT)
- `KLine/` - K-line data structures and operations
- `Seg/` - Segmentation (分型)
- `Bi/` - "笔" (stroke) analysis
- `ZS/` - Trend/signal analysis (走势)
- `BuySellPoint/` - Buy/sell point detection
- `Combiner/` - K-line combining logic
- `ChanModel/` - Feature models
- `Common/` - Shared utilities, enums, exceptions, time handling
- `a_replay_parts/` - Replay visualization components

## Run Tests
No test framework configured.