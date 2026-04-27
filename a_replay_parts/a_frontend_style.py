FRONTEND_STYLE = """\

    :root, [data-theme="light"]{
      --bg: #ffffff;
      --panel: #f7f8fa;
      --text: #101418;
      --muted: #5f6975;
      --border: #9aa3ad;
      --btn: #eceff2;
      --btnText: #111827;
      --chartBg: #ffffff;
      --grid: #d4d8de;
      --candleUp: #ff3b30;
      --candleDown: #27d6dc;
      --candleUpFill: rgba(255,59,48,0.12);
      --candleDownFill: rgba(39,214,220,0.55);
      --lineFx: #8ab4f8;
      --lineBi: #ffb347;
      --lineBiWeak: #8694a6;
      --lineSeg: #4fd18a;
      --lineSegWeak: #8ae6bb;
      --holdFill: rgba(51,122,255,0.14);
      --holdFillPast: rgba(71,95,199,0.12);
      --markBuy: #ff5e57;
      --markSell: #27d6dc;
      --rayBuy: #f6a623;
      --raySell: #27d6dc;
      --bspBuy: #ff5e57;
      --bspSell: #27d6dc;
      --legendBg: rgba(255,255,255,0.92);
      --legendText: #0f172a;
      --legendBorder: rgba(154,163,173,0.8);
      --chipFill: rgba(246,166,35,0.45);
      --chipBg: rgba(154,163,173,0.12);
      --chipEdge: rgba(246,166,35,0.8);
      --inputBg: #ffffff;
      --inputText: #101418;
      --inputBorder: #9aa3ad;
      --hoverBg: #dde4ec;
      --hoverText: #23425f;
      --toolboxBg: #edf1f6;
      --toolBtnBg: #e3e8ef;
      --accent: #f0a53a;
      --accentTitle: #a16207;
      --dangerText: #b91c1c;
      --modalPanelBg: #f7f8fa;
      --tipBg: rgba(15, 23, 42, 0.95);
      --tipText: #f8fafc;
      --overlayPanelBg: rgba(255, 255, 255, 0.95);
      --overlayBorder: #d0d8e2;
      --overlayTitle: #0f172a;
      --overlaySubText: #64748b;
      --overlayPlusBg: rgba(254, 242, 242, 0.95);
      --overlayMinusBg: rgba(240, 253, 244, 0.95);
      --settlementBtnBg: #2563eb;
      --settlementBtnText: #ffffff;
    }
    [data-theme="dark"]{
      --bg: #050608;
      --panel: #0e1013;
      --text: #d7dce2;
      --muted: #8f98a4;
      --border: #2b2f36;
      --btn: #13171d;
      --btnText: #d7dce2;
      --chartBg: #000000;
      --grid: #2b1212;
      --candleUp: #ff3b30;
      --candleDown: #27d6dc;
      --candleUpFill: rgba(255,59,48,0.18);
      --candleDownFill: rgba(39,214,220,0.55);
      --lineFx: #8db6ff;
      --lineBi: #f0a53a;
      --lineBiWeak: #7a8797;
      --lineSeg: #58cb83;
      --lineSegWeak: #8ce4ad;
      --holdFill: rgba(23,41,84,0.28);
      --holdFillPast: rgba(54,72,126,0.22);
      --markBuy: #ff615c;
      --markSell: #27d6dc;
      --rayBuy: #f0a53a;
      --raySell: #27d6dc;
      --bspBuy: #ff615c;
      --bspSell: #27d6dc;
      --legendBg: rgba(8,10,12,0.94);
      --legendText: #d7dce2;
      --legendBorder: rgba(58,63,70,0.9);
      --chipFill: rgba(240,165,58,0.65);
      --chipBg: rgba(61,35,10,0.25);
      --chipEdge: rgba(240,165,58,0.95);
      --inputBg: #090c11;
      --inputText: #d7dce2;
      --inputBorder: #2b2f36;
      --hoverBg: #1b1f25;
      --hoverText: #f7c97e;
      --toolboxBg: #090b0f;
      --toolBtnBg: #11151a;
      --accent: #f0a53a;
      --accentTitle: #f1c979;
      --dangerText: #f87171;
      --modalPanelBg: #0e1013;
      --tipBg: rgba(6, 8, 12, 0.96);
      --tipText: #ffffff;
      --overlayPanelBg: rgba(30, 41, 59, 0.95);
      --overlayBorder: #334155;
      --overlayTitle: #f1f5f9;
      --overlaySubText: #94a3b8;
      --overlayPlusBg: rgba(69, 10, 10, 0.95);
      --overlayMinusBg: rgba(5, 46, 22, 0.95);
      --settlementBtnBg: #3b82f6;
      --settlementBtnText: #ffffff;
    }
    [data-theme="eye-care"]{
      --bg: #e8f0e8;
      --panel: #f4faf4;
      --text: #1a2e1a;
      --muted: #3d5a3d;
      --border: #a3c4a3;
      --btn: #dcefdc;
      --btnText: #1a2e1a;
      --chartBg: #fafdf8;
      --grid: #c5dcc5;
      --candleUp: #c0392b;
      --candleDown: #27ae60;
      --candleUpFill: rgba(192,57,43,0.12);
      --candleDownFill: rgba(39,174,96,0.55);
      --lineFx: #1a8a9e;
      --lineBi: #b45309;
      --lineBiWeak: #78716c;
      --lineSeg: #047857;
      --lineSegWeak: #6ee7b7;
      --holdFill: rgba(37,99,235,0.12);
      --holdFillPast: rgba(79,70,229,0.1);
      --markBuy: #b91c1c;
      --markSell: #15803d;
      --rayBuy: #c2410c;
      --raySell: #0f766e;
      --bspBuy: #b91c1c;
      --bspSell: #15803d;
      --legendBg: rgba(250,253,248,0.94);
      --legendText: #1a2e1a;
      --legendBorder: rgba(163,196,163,0.9);
      --chipFill: rgba(37,99,235,0.42);
      --chipBg: rgba(163,196,163,0.18);
      --chipEdge: rgba(37,99,235,0.72);
      --inputBg: #f8fcf8;
      --inputText: #1a2e1a;
      --inputBorder: #a3c4a3;
      --hoverBg: #d8e8d8;
      --hoverText: #1f5134;
      --toolboxBg: #eaf3ea;
      --toolBtnBg: #dcefdc;
      --accent: #f0a53a;
      --accentTitle: #8f5f1d;
      --dangerText: #9b1c1c;
      --modalPanelBg: #f4faf4;
      --tipBg: rgba(32, 51, 32, 0.94);
      --tipText: #f4faf4;
      --overlayPanelBg: rgba(244, 250, 244, 0.95);
      --overlayBorder: #a3c4a3;
      --overlayTitle: #1a2e1a;
      --overlaySubText: #3d5a3d;
      --overlayPlusBg: rgba(254, 242, 242, 0.9);
      --overlayMinusBg: rgba(240, 253, 244, 0.9);
      --settlementBtnBg: #2f855a;
      --settlementBtnText: #ffffff;
    }
    body { margin: 0; font-family: "Segoe UI", "Microsoft YaHei UI", Tahoma, sans-serif; background: var(--bg); color: var(--text); overflow: hidden; letter-spacing: 0.01em; }
    .wrap { display: flex; height: 100vh; min-height: 0; flex-direction: row-reverse; }
    .left { width: clamp(300px, 24vw, 360px); min-width: 300px; max-width: 380px; padding: 10px; border-right: none; border-left: 1px solid var(--border); box-sizing: border-box; overflow: auto; background: var(--panel); position: relative; overscroll-behavior: contain; }
    .leftContent {
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
      min-height: 0;
    }
    .sourceStatus {
      margin: -4px 0 10px;
      color: var(--muted);
      font-size: 12px;
      min-height: 18px;
    }
    .resizer {
      flex: 0 0 4px;
      width: 4px;
      cursor: col-resize;
      background: var(--border);
      height: 100%;
      z-index: 10;
      transition: background 0.2s;
    }
    .resizer:hover { background: #f0a53a; }
    .right { flex: 1; padding: 0; box-sizing: border-box; min-width: 0; position: relative; display: flex; }
    .row { margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .row input[type="checkbox"] { width: auto; transform: scale(1.1); margin-left: 8px; }
    label { display: inline-block; width: 110px; font-size: 12px; }
    input, select, textarea { flex: 1; padding: 4px 6px; background: var(--inputBg); color: var(--inputText); border: 1px solid var(--inputBorder); min-width: 0; border-radius: 0; box-shadow: none; }
    
    .btnRow { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
    .btnRow button { width: 100%; margin: 0; padding: 8px; text-align: left; position: relative; }
    
    button { padding: 6px 10px; border: 1px solid var(--border); background: var(--btn); color: var(--btnText); cursor: pointer; border-radius: 0; box-shadow: none; transition: background 0.16s ease, border-color 0.16s ease, color 0.16s ease; }
    button:disabled { opacity: 0.4; cursor: not-allowed; }
    button:hover:not(:disabled) { border-color: #f0a53a; background: var(--hoverBg); color: var(--hoverText); }
    
    .title { font-size: 14px; margin: 2px 0 8px; color: var(--accentTitle); font-weight: 700; }
    .card { border: 1px solid var(--border); padding: 10px; margin-bottom: 10px; background: var(--panel); border-radius: 0; }
    .left.compact .title { margin-bottom: 8px; font-size: 15px; }
    .left.compact .sourceStatus { margin-bottom: 8px; font-size: 11px; }
    .left.compact .chartToolsPanel,
    .left.compact .card { padding: 10px; margin-bottom: 10px; }
    .left.compact .btnRow { gap: 4px; margin-bottom: 6px; }
    .left.compact .btnRow button { padding: 6px 8px; }
    .left.compact .row { margin-bottom: 6px; }
    .left.compact label { width: 96px; font-size: 13px; }
    .left.compact input,
    .left.compact select,
    .left.compact button { font-size: 12px; }
    #chart { width: 100%; height: 100%; min-height: 420px; background: var(--chartBg); display: block; flex: 1; min-width: 0; }
    .muted { color: var(--muted); font-size: 12px; }
    .mono { font-family: Consolas, monospace; }
    
    .account-grid { display: grid; grid-template-columns: 1fr; gap: 8px; }
    .account-item { display: flex; justify-content: space-between; font-size: 14px; padding: 4px 0; border-bottom: 1px dashed var(--grid); }
    .account-item label { width: auto; color: var(--muted); }
    .account-item span { font-weight: bold; font-family: Consolas, monospace; }

    /* Tooltip logic */
    .tip-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 16px;
      height: 16px;
      background: #f0a53a;
      color: white;
      border-radius: 0;
      font-size: 11px;
      font-weight: bold;
      margin-left: 6px;
      cursor: help;
      position: relative;
      user-select: none;
    }
    .tip-icon::before {
      content: "i";
      font-family: serif;
    }
    .tip-content {
      position: fixed;
      background: var(--tipBg);
      color: var(--tipText);
      padding: 8px 12px;
      border-radius: 0;
      font-size: 12px;
      white-space: pre-wrap;
      z-index: 30000;
      width: max-content;
      max-width: 280px;
      font-weight: normal;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      pointer-events: auto;
      display: none;
      line-height: 1.5;
    }

    /* Chart tools panel (pinned to the very top of the trainer controls) */
    .chartToolsPanel {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 0;
      background: var(--panel);
      padding: 12px;
      box-sizing: border-box;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      margin: 0 0 12px 0;
    }
    :fullscreen #chart { height: 100vh; }
    .fullscreen-btn {
      background: var(--toolBtnBg);
      border: 1px solid var(--border);
      border-radius: 0;
      padding: 4px 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      width: auto;
      min-width: 140px;
      justify-content: center;
    }
    .fullscreen-btn:hover { background: var(--hoverBg); border-color: #f0a53a; color: var(--hoverText); }

    .judge-bsp-btn {
      background: var(--toolBtnBg);
      border: 1px solid var(--border);
      border-radius: 0;
      padding: 4px 10px;
      cursor: pointer;
      display: none;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      width: auto;
      min-width: 124px;
      justify-content: center;
    }
    .judge-bsp-btn:hover { background: var(--hoverBg); border-color: #27d6dc; color: var(--hoverText); }
    .judge-bsp-btn:disabled { opacity: 0.55; cursor: not-allowed; }

    .toolbox {
      background: var(--toolboxBg);
      border: 1px solid var(--border);
      border-radius: 0;
      padding: 8px;
      display: flex;
      flex: 1 1 460px;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      min-width: 0;
    }
    .toolbox .label {
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
      margin-right: 4px;
    }
    .toolbox button {
      padding: 4px 8px;
      font-size: 12px;
      width: auto;
      border-radius: 0;
      border: 1px solid var(--border);
      background: var(--toolBtnBg);
      color: var(--btnText);
      cursor: pointer;
      white-space: nowrap;
    }
    .toolbox button.active {
      border-color: #f0a53a;
      box-shadow: inset 0 0 0 1px rgba(240, 165, 58, 0.35);
    }

    /* Toast 弹窗 */
    #toastContainer {
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 11000;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      pointer-events: none;
    }
    .toast {
      padding: 10px 20px;
      background: var(--legendBg);
      color: var(--legendText);
      border: 1px solid var(--legendBorder);
      border-radius: 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      font-family: Consolas, monospace;
      animation: toastFadeIn 0.3s forwards;
      pointer-events: auto;
      max-width: 80vw;
      text-align: center;
      transition: opacity 0.3s;
      white-space: pre-wrap;
      line-height: 1.5;
    }
    @keyframes toastFadeIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* 消息历史弹窗 */
    .msgHistoryModal {
      position: fixed; inset: 0; display: none; align-items: center; justify-content: center;
      background: rgba(2, 6, 23, 0.6); z-index: 10006;
    }
    .msgHistoryModal.show { display: flex; }
    .msgHistoryModal .panel {
      width: 600px; max-height: 80vh; background: var(--panel); padding: 20px; border-radius: 12px;
      display: flex; flex-direction: column;
    }
    .msgHistoryList {
      flex: 1; overflow-y: auto; border: 1px solid var(--border); margin: 10px 0; padding: 10px;
      font-family: Consolas, monospace; font-size: 13px;
    }
    .msgHistoryItem { border-bottom: 1px dashed var(--grid); padding: 6px 0; }
    .msgHistoryItem .time { color: #2563eb; margin-right: 10px; }
    
    .stepNRow {
      margin-top: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }
    .stepNRow input {
      width: 76px;
      padding: 4px 6px;
      box-sizing: border-box;
      font-family: Consolas, monospace;
    }
    .stepNRow .hint {
      color: var(--muted);
      font-size: 12px;
    }
    .modal-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 10000;
    }
    .modal-overlay > div {
      pointer-events: auto;
    }
    .globalLoading {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(15, 23, 42, 0.36);
      backdrop-filter: blur(1px);
      z-index: 20000;
    }
    .globalLoading.show { display: flex; }
    .globalLoading .panel {
      min-width: 260px;
      padding: 18px 20px;
      border-radius: 10px;
      border: 1px solid var(--legendBorder);
      background: var(--legendBg);
      color: var(--legendText);
      box-shadow: 0 14px 36px rgba(2, 6, 23, 0.26);
      display: flex;
      align-items: center;
      gap: 12px;
      font: 14px Consolas, monospace;
    }
    .globalLoading .spinner {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid rgba(59, 130, 246, 0.22);
      border-top-color: #2563eb;
      animation: spin 0.8s linear infinite;
      flex: 0 0 auto;
    }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .bspPrompt {
      position: absolute;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(2, 6, 23, 0.45);
      z-index: 10001;
      pointer-events: auto;
      cursor: pointer;
    }
    .bspPrompt.show { display: flex; }
    .bspPrompt .panel {
      width: min(560px, calc(100vw - 24px));
      border: 1px solid var(--legendBorder);
      border-radius: 10px;
      background: var(--legendBg);
      color: var(--legendText);
      box-shadow: 0 18px 42px rgba(2, 6, 23, 0.32);
      padding: 16px;
      box-sizing: border-box;
      pointer-events: auto;
      cursor: default;
    }
    .bspPromptTitle {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #b91c1c;
    }
    .bspPromptBody {
      white-space: pre-wrap;
      line-height: 1.6;
      margin-bottom: 10px;
      font-family: Consolas, monospace;
      font-size: 13px;
    }
    .bspPromptHint {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 10px;
    }
    .bspPromptActions {
      display: flex;
      justify-content: flex-end;
    }
    .bspPromptActions button {
      min-width: 120px;
    }
    /* 交易状态悬浮窗 */
    .tradeStatusOverlay {
      position: fixed;
      top: 16px;
      left: 16px;
      width: 280px;
      min-width: 220px;
      min-height: 64px;
      background: var(--overlayPanelBg);
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
      padding: 0;
      z-index: 10002;
      border: 2px solid var(--overlayBorder);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      backdrop-filter: blur(8px);
      overflow: hidden;
    }
    .tradeStatusTitleBar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 12px;
      background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(14,165,233,0.08));
      border-bottom: 1px solid #dbeafe;
      cursor: move;
      user-select: none;
      gap: 8px;
    }
    .tradeStatusTitle {
      font-weight: bold;
      font-size: 14px;
      letter-spacing: 0.5px;
      color: var(--overlayTitle);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tradeStatusDot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: linear-gradient(135deg, #22c55e, #16a34a);
      box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.18);
    }
    .tradeStatusActions { display: flex; gap: 6px; }
    .tradeStatusMiniBtn {
      width: 24px;
      height: 24px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--btn);
      color: var(--btnText);
      font-size: 12px;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .tradeStatusMiniBtn:hover { background: var(--hoverBg); color: var(--hoverText); }
    .tradeStatusOverlay.dragging .tradeStatusTitle { opacity: 0.85; }
    .tradeStatusBody { padding: 12px 14px 16px; }
    .tradeStatusGrid { display: grid; grid-template-columns: 1fr; gap: 6px; }
    .tsItem { display: flex; justify-content: space-between; font-family: Consolas, monospace; }
    .tsItem label { color: var(--overlaySubText); font-size: 12px; }
    .tsItem span { font-weight: bold; }
    .tradeStatusOverlay.minimized .tradeStatusBody { display: none; }
    .tradeStatusResizeHandle {
      position: absolute;
      right: 0;
      bottom: 0;
      width: 18px;
      height: 18px;
      cursor: nwse-resize;
      background: linear-gradient(135deg, transparent 45%, rgba(37,99,235,0.45) 45%, rgba(37,99,235,0.45) 55%, transparent 55%);
    }
    .pnl-plus { color: #ef4444; }
    .pnl-minus { color: #22c55e; }
    .overlay-plus { border-color: #ef4444; background: var(--overlayPlusBg); }
    .overlay-minus { border-color: #22c55e; background: var(--overlayMinusBg); }

    /* 结算弹窗 */
    .settlementModal {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 10000;
    }
    .settlementModal.show { display: flex; }
    .settlementModal .panel {
      width: 480px; background: var(--modalPanelBg); color: var(--text); border-radius: 12px; padding: 24px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .settlementTitle { font-size: 20px; font-weight: bold; margin-bottom: 20px; text-align: center; border-bottom: 2px solid var(--border); padding-bottom: 12px; }
    .settlementBody { font-family: Consolas, monospace; line-height: 1.8; font-size: 14px; margin-bottom: 20px; }
    .settlementActions { text-align: center; }
    .settlementActions button { padding: 10px 40px; font-size: 16px; cursor: pointer; background: var(--settlementBtnBg); color: var(--settlementBtnText); border: none; border-radius: 6px; }

    .settingsModal {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(2, 6, 23, 0.6);
      z-index: 10005;
    }
    .settingsModal.show { display: flex; }
    .settingsModal .panel {
      width: min(640px, calc(100vw - 40px));
      max-height: 85vh;
      overflow-y: auto;
      border: 1px solid var(--legendBorder);
      border-radius: 12px;
      background: var(--panel);
      color: var(--text);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
      padding: 24px;
      box-sizing: border-box;
    }
    .settingsTitle {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--border);
      color: var(--accentTitle);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .settingsSection {
      margin-bottom: 20px;
      padding: 16px;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .settingsSectionTitle {
      font-weight: bold;
      margin-bottom: 16px;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .settingsSectionTitle::before {
      content: "";
      display: inline-block;
      width: 4px;
      height: 16px;
      background: currentColor;
      border-radius: 2px;
    }
    .settingsGrid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px;
    }
    .settingsItem {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .settingsItem label {
      font-size: 13px;
      width: auto;
    }
    .settingsItem input {
      width: 100%;
      box-sizing: border-box;
    }
    .settingsActions {
      margin-top: 16px;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      position: sticky;
      bottom: 0;
      z-index: 2;
      padding: 12px 0 4px;
      border-top: 1px solid var(--border);
      background: linear-gradient(to bottom, transparent, var(--panel) 24%);
    }
    .settingsActions button {
      min-width: 100px;
    }
    @media (max-width: 1180px) {
      body { overflow: auto; }
      .wrap {
        height: auto;
        min-height: 100vh;
        flex-direction: column;
      }
      .left {
        width: 100%;
        min-width: 0;
        max-width: none;
        border-left: none;
        border-top: 1px solid var(--border);
        order: 2;
      }
      .right {
        min-height: 62vh;
        order: 1;
      }
      .resizer {
        display: none;
      }
    }
  
"""
