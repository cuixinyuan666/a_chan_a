FRONTEND_EXT = """\
(function () {
  const SHARED_SETTINGS_DEFAULT = {
    data_quality: "network_direct",
    cycle_form: "standard",
    chip_data_quality: "offline_tick",
    offline_kline_path: "",
    offline_tick_path: "",
  };
  const TRAIN_DEFAULT_FORM = {
    code: "600340",
    begin_date: "2018-01-01",
    end_date: "",
    autype: "qfq",
    initial_cash: "100000",
    lv_tokens: ["day", "60m", "15m"],
  };
  let sharedSettingsState = { ...SHARED_SETTINGS_DEFAULT };
  let rldSubtabState = storageGet("rld_subtab_active") || "analysis";
  let rldTrainPayload = null;
  let rldTrainCrosshair = {};

  function ensureArrayText(raw, fallback) {
    if (!Array.isArray(raw)) return fallback.slice();
    const rows = raw.map((item) => String(item || "").trim()).filter(Boolean);
    return rows.length > 0 ? rows : fallback.slice();
  }

  function getTrainForm() {
    const stored = ensureObject(safeJsonParse(storageGet("rld_train_form"), {}), {});
    return {
      code: String(stored.code || TRAIN_DEFAULT_FORM.code),
      begin_date: String(stored.begin_date || TRAIN_DEFAULT_FORM.begin_date),
      end_date: String(stored.end_date || TRAIN_DEFAULT_FORM.end_date),
      autype: String(stored.autype || TRAIN_DEFAULT_FORM.autype),
      initial_cash: String(stored.initial_cash || TRAIN_DEFAULT_FORM.initial_cash),
      lv_tokens: ensureArrayText(stored.lv_tokens, TRAIN_DEFAULT_FORM.lv_tokens),
    };
  }

  function saveTrainForm(form) {
    storageSet("rld_train_form", JSON.stringify({
      ...TRAIN_DEFAULT_FORM,
      ...form,
      lv_tokens: ensureArrayText(form.lv_tokens, TRAIN_DEFAULT_FORM.lv_tokens),
    }));
  }

  function getSourcePriorityHint() {
    const priority = ensureArray(dataSourcePriorityState && dataSourcePriorityState.priority, []);
    return priority.length > 0 ? priority.join(" > ") : "BaoStock > AKShare > Ashare > AData > Tushare > OfflineTXT > Tencent > Sina > Eastmoney > Yahoo";
  }

  async function loadSharedSettings() {
    try {
      const payload = await api("/api/shared-settings", null, "GET");
      sharedSettingsState = { ...SHARED_SETTINGS_DEFAULT, ...ensureObject(payload, {}) };
    } catch (e) {
      sharedSettingsState = { ...SHARED_SETTINGS_DEFAULT };
    }
    return sharedSettingsState;
  }

  async function persistSharedSettings(nextState, quiet) {
    const payload = await api("/api/shared-settings", nextState, "POST");
    sharedSettingsState = { ...SHARED_SETTINGS_DEFAULT, ...ensureObject(payload, {}) };
    if (!quiet) showToast("共享系统设置已保存", { record: false });
    renderSharedSettingsSummary();
    return sharedSettingsState;
  }

  function sharedSettingsFieldHtml(id, label, options, value, tip) {
    return `
      <div class="settingsItem">
        <label>${label} <span class="tip-icon" data-tip="${escapeHtmlAttr(tip)}">!</span></label>
        <select id="${id}">
          ${options.map((item) => `<option value="${item.value}" ${item.value === value ? "selected" : ""}>${item.label}</option>`).join("")}
        </select>
      </div>
    `;
  }

  function appendSharedSettingsToSystemModal() {
    const container = $("systemSettingsContent");
    if (!container || container.querySelector("[data-shared-settings='1']")) return;
    const section = document.createElement("div");
    section.className = "settingsSection";
    section.dataset.sharedSettings = "1";
    section.style.background = "rgba(249, 115, 22, 0.08)";
    section.innerHTML = `
      <div class="settingsSectionTitle" style="color:#c2410c">共享数据 / 周期 / 筹码设置</div>
      <div class="settingsGrid">
        ${sharedSettingsFieldHtml(
          "sysDataQuality",
          "数据质量",
          [
            { value: "network_direct", label: "网络直接获取" },
            { value: "network_agg", label: "网络小周期聚合大周期" },
            { value: "offline_direct", label: "离线文件直接获取" },
            { value: "offline_agg", label: "离线小周期聚合大周期" },
          ],
          sharedSettingsState.data_quality,
          "复盘与融立德统一使用这一套取数策略。聚合模式会优先拿更小周期，再在本地聚合成大周期。"
        )}
        ${sharedSettingsFieldHtml(
          "sysCycleForm",
          "周期形式",
          [
            { value: "standard", label: "标准K线" },
            { value: "custom_group", label: "自定义周期N" },
          ],
          sharedSettingsState.cycle_form,
          "仅融立德-缠论训练会读取这个选项。切到自定义周期后，可输入 day2、60m5 这类格式。"
        )}
        ${sharedSettingsFieldHtml(
          "sysChipQuality",
          "筹码数据质量",
          [
            { value: "kline_estimate", label: "原逻辑 / K线估算" },
            { value: "network_tick", label: "网络获取分笔数据" },
            { value: "offline_tick", label: "离线分笔文件" },
          ],
          sharedSettingsState.chip_data_quality,
          "若网络或离线分笔读取失败，训练页会隐藏对应筹码图，并在状态区给出提示。"
        )}
        <div class="settingsItem" style="grid-column:1 / -1;">
          <label>离线K线路径 <span class="tip-icon" data-tip="可填单个 txt 文件，也可填目录。目录下会按 *#股票代码.txt 自动匹配。">!</span></label>
          <input id="sysOfflineKlinePath" type="text" value="${escapeHtmlAttr(sharedSettingsState.offline_kline_path || "")}" placeholder="例如 F:\\\\my_file\\\\3\\\\chan.py\\\\a_Data\\\\SZ#001312\\\\KLine\\\\SZ#001312.txt" />
        </div>
        <div class="settingsItem" style="grid-column:1 / -1;">
          <label>离线分笔路径 <span class="tip-icon" data-tip="可填单个 txt 文件，也可填 TickData 目录。目录下会按 *_股票代码.txt 自动匹配。">!</span></label>
          <input id="sysOfflineTickPath" type="text" value="${escapeHtmlAttr(sharedSettingsState.offline_tick_path || "")}" placeholder="例如 F:\\\\my_file\\\\3\\\\chan.py\\\\a_Data\\\\SZ#001312\\\\TickData" />
        </div>
      </div>
    `;
    container.appendChild(section);
    initTooltips();
  }

  function readSharedSettingsFromSystemModal() {
    return {
      data_quality: $("sysDataQuality") ? $("sysDataQuality").value : sharedSettingsState.data_quality,
      cycle_form: $("sysCycleForm") ? $("sysCycleForm").value : sharedSettingsState.cycle_form,
      chip_data_quality: $("sysChipQuality") ? $("sysChipQuality").value : sharedSettingsState.chip_data_quality,
      offline_kline_path: $("sysOfflineKlinePath") ? $("sysOfflineKlinePath").value.trim() : sharedSettingsState.offline_kline_path,
      offline_tick_path: $("sysOfflineTickPath") ? $("sysOfflineTickPath").value.trim() : sharedSettingsState.offline_tick_path,
    };
  }

  function renderSharedSettingsSummary() {
    const host = $("settingsSharedSummary");
    if (!host) return;
    host.innerHTML = `
      <div class="sharedSettingChip"><span>数据质量</span><strong>${sharedSettingsState.data_quality}</strong></div>
      <div class="sharedSettingChip"><span>周期形式</span><strong>${sharedSettingsState.cycle_form}</strong></div>
      <div class="sharedSettingChip"><span>筹码质量</span><strong>${sharedSettingsState.chip_data_quality}</strong></div>
      <div class="sharedSettingChip wide"><span>当前优先级</span><strong>${escapeHtmlAttr(getSourcePriorityHint())}</strong></div>
    `;
  }

  function wrapSystemSettingsFunctions() {
    if (window.__sharedSettingsWrapped === true) return;
    window.__sharedSettingsWrapped = true;
    const originalRender = renderSystemSettingsForm;
    renderSystemSettingsForm = function () {
      originalRender();
      appendSharedSettingsToSystemModal();
    };
    const originalSave = saveSystemSettingsFromForm;
    saveSystemSettingsFromForm = async function () {
      const nextShared = readSharedSettingsFromSystemModal();
      originalSave();
      try {
        await persistSharedSettings(nextShared, true);
      } catch (e) {
        showToast(`共享设置保存失败：${e.message}`, { record: false });
      }
    };
    const originalReset = resetSystemSettings;
    resetSystemSettings = async function () {
      originalReset();
      sharedSettingsState = { ...SHARED_SETTINGS_DEFAULT };
      try {
        await persistSharedSettings(sharedSettingsState, true);
      } catch (e) {
        showToast(`共享设置重置失败：${e.message}`, { record: false });
      }
      renderSystemSettingsForm();
    };
    const saveBtn = $("btnSystemSettingsSave");
    if (saveBtn && saveBtn.dataset.extBound !== "1") {
      const cloned = saveBtn.cloneNode(true);
      saveBtn.replaceWith(cloned);
      cloned.dataset.extBound = "1";
      cloned.addEventListener("click", () => saveSystemSettingsFromForm());
    }
    const resetBtn = $("btnSystemSettingsReset");
    if (resetBtn && resetBtn.dataset.extBound !== "1") {
      const cloned = resetBtn.cloneNode(true);
      resetBtn.replaceWith(cloned);
      cloned.dataset.extBound = "1";
      cloned.addEventListener("click", () => resetSystemSettings());
    }
  }

  function injectSharedSummaryIntoSettingsHub() {
    const mount = $("settingsSharedMount");
    if (!mount || mount.querySelector("#settingsSharedSummary")) return;
    const box = document.createElement("section");
    box.className = "settingsHubInner";
    box.innerHTML = `
      <div class="settingsHubSectionTitle">共享系统摘要</div>
      <div id="settingsSharedSummary" class="sharedSettingGrid"></div>
      <div class="settingsHubHint">共享系统设置会同时作用于复盘、融立德多周期分析、融立德缠论训练。</div>
    `;
    mount.appendChild(box);
    renderSharedSettingsSummary();
  }

  function trainLevelRowHtml(value, idx) {
    return `
      <div class="trainLevelRow" data-train-level-row="${idx}">
        <div class="rldLevelCell">
          <label>训练周期 ${idx + 1}</label>
          <input class="trainLevelToken" type="text" value="${escapeHtmlAttr(value)}" placeholder="day / 60m / day2 / 15m5" />
        </div>
        <button class="rldLevelRemove" type="button" data-remove-train-level="${idx}" ${idx === 0 ? "disabled" : ""}>删除</button>
      </div>
    `;
  }

  function readTrainLevelTokens() {
    const host = $("trainLevelList");
    if (!host) return getTrainForm().lv_tokens.slice();
    const values = Array.from(host.querySelectorAll(".trainLevelToken"))
      .map((input) => String(input.value || "").trim())
      .filter(Boolean);
    return values.length > 0 ? values : TRAIN_DEFAULT_FORM.lv_tokens.slice();
  }

  function renderTrainLevelRows(values) {
    const host = $("trainLevelList");
    if (!host) return;
    const rows = ensureArrayText(values, TRAIN_DEFAULT_FORM.lv_tokens);
    host.innerHTML = rows.map((value, idx) => trainLevelRowHtml(value, idx)).join("");
    host.querySelectorAll("[data-remove-train-level]").forEach((btn) => {
      btn.onclick = () => {
        const idx = Number(btn.getAttribute("data-remove-train-level"));
        const next = readTrainLevelTokens().filter((_, rowIdx) => rowIdx !== idx);
        renderTrainLevelRows(next);
        persistTrainSettingsFromHub();
      };
    });
    host.querySelectorAll(".trainLevelToken").forEach((input) => {
      input.onchange = () => persistTrainSettingsFromHub();
    });
  }

  function buildTrainSettingsMarkup() {
    const form = getTrainForm();
    return `
      <section class="settingsHubInner">
        <div class="settingsHubSectionTitle">缠论训练参数</div>
        <div class="rldFormGrid">
          <div class="rldField"><label>代码</label><input id="trainCode" value="${escapeHtmlAttr(form.code)}" /></div>
          <div class="rldField"><label>复权</label><select id="trainAutype"><option value="qfq">前复权</option><option value="hfq">后复权</option><option value="none">不复权</option></select></div>
          <div class="rldField"><label>开始日期</label><input id="trainBegin" type="date" value="${escapeHtmlAttr(form.begin_date)}" /></div>
          <div class="rldField"><label>结束日期</label><input id="trainEnd" type="date" value="${escapeHtmlAttr(form.end_date)}" /></div>
          <div class="rldField"><label>初始资金</label><input id="trainCash" type="number" step="1000" min="1000" value="${escapeHtmlAttr(form.initial_cash)}" /></div>
          <div class="rldField full">
            <div class="settingsInlineHead">
              <label>训练周期列表</label>
              <button id="trainAddLevel" class="miniAction" type="button">＋ 添加周期</button>
            </div>
            <div id="trainLevelList" class="rldLevelList"></div>
            <div class="settingsHubHint">标准K线示例：day、60m、15m。自定义周期示例：day2、60m5。只有当系统设置中的“周期形式”切到 custom_group 时，才允许带数字后缀。</div>
          </div>
        </div>
      </section>
    `;
  }

  function persistTrainSettingsFromHub() {
    const next = {
      code: $("trainCode") ? $("trainCode").value.trim() : TRAIN_DEFAULT_FORM.code,
      begin_date: $("trainBegin") ? $("trainBegin").value : TRAIN_DEFAULT_FORM.begin_date,
      end_date: $("trainEnd") ? $("trainEnd").value : "",
      autype: $("trainAutype") ? $("trainAutype").value : "qfq",
      initial_cash: $("trainCash") ? $("trainCash").value : TRAIN_DEFAULT_FORM.initial_cash,
      lv_tokens: readTrainLevelTokens(),
    };
    saveTrainForm(next);
  }

  function mountTrainSettingsIntoHub() {
    const mount = $("settingsRldMount");
    if (!mount || mount.querySelector("#trainCode")) return;
    const wrap = document.createElement("div");
    wrap.innerHTML = buildTrainSettingsMarkup();
    mount.appendChild(wrap);
    const form = getTrainForm();
    if ($("trainAutype")) $("trainAutype").value = form.autype;
    renderTrainLevelRows(form.lv_tokens);
    ["trainCode", "trainBegin", "trainEnd", "trainAutype", "trainCash"].forEach((id) => {
      const el = $(id);
      if (el) el.addEventListener("change", persistTrainSettingsFromHub);
    });
    const addBtn = $("trainAddLevel");
    if (addBtn) {
      addBtn.onclick = () => {
        const next = readTrainLevelTokens();
        next.push(sharedSettingsState.cycle_form === "custom_group" ? "day2" : "day");
        renderTrainLevelRows(next);
        persistTrainSettingsFromHub();
      };
    }
    initTooltips();
  }

  function injectTrainStyle() {
    if ($("rldTrainStyle")) return;
    const style = document.createElement("style");
    style.id = "rldTrainStyle";
    style.textContent = `
      .rldSubtabBar {
        display:flex;
        gap:8px;
        margin-bottom:12px;
      }
      .rldSubtabBtn {
        width:auto;
        padding:8px 14px;
        border-radius:999px;
        border:1px solid rgba(148,163,184,0.45);
        background:rgba(255,255,255,0.82);
        font-weight:700;
      }
      .rldSubtabBtn.active {
        background:#0f172a;
        color:#fff;
        border-color:#0f172a;
      }
      .rldSubpanel { display:none; }
      .rldSubpanel.active { display:block; }
      .trainShell {
        display:flex;
        flex-direction:column;
        gap:12px;
      }
      .trainPanel {
        border-radius:18px;
        border:1px solid rgba(148,163,184,0.28);
        background:linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96));
        box-shadow:0 10px 30px rgba(15,23,42,0.06);
        padding:16px;
      }
      .trainHead {
        display:flex;
        justify-content:space-between;
        gap:12px;
        align-items:flex-start;
        flex-wrap:wrap;
      }
      .trainHeadTitle {
        font-size:20px;
        font-weight:800;
        color:#0f172a;
      }
      .trainHeadSub {
        color:#475569;
        font-size:13px;
        line-height:1.7;
        max-width:720px;
      }
      .trainActionRow {
        display:flex;
        flex-wrap:wrap;
        gap:8px;
      }
      .trainActionRow button {
        width:auto;
        padding:8px 12px;
      }
      .trainSummaryGrid, .sharedSettingGrid {
        display:grid;
        grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));
        gap:10px;
      }
      .trainSummaryCard, .sharedSettingChip {
        border-radius:14px;
        border:1px solid rgba(226,232,240,0.9);
        background:rgba(255,255,255,0.92);
        padding:12px;
      }
      .trainSummaryCard .k, .sharedSettingChip span {
        display:block;
        color:#64748b;
        font-size:12px;
        margin-bottom:4px;
      }
      .trainSummaryCard .v, .sharedSettingChip strong {
        color:#0f172a;
        font-size:18px;
        font-weight:800;
      }
      .sharedSettingChip.wide {
        grid-column:1 / -1;
      }
      .trainChartStack {
        display:grid;
        grid-template-columns:repeat(auto-fit, minmax(440px, 1fr));
        gap:12px;
        align-items:start;
      }
      .trainChartCard {
        border-radius:18px;
        border:1px solid rgba(148,163,184,0.28);
        background:#fff;
        padding:12px;
        resize:vertical;
        overflow:auto;
        min-height:440px;
      }
      .trainChartHead {
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        gap:10px;
        margin-bottom:10px;
        flex-wrap:wrap;
      }
      .trainChartMeta {
        display:flex;
        flex-direction:column;
        gap:4px;
      }
      .trainChartTitle {
        color:#0f172a;
        font-size:16px;
        font-weight:800;
      }
      .trainChartSub {
        color:#475569;
        font-size:12px;
      }
      .trainChartActions {
        display:flex;
        flex-wrap:wrap;
        gap:6px;
      }
      .trainChartActions button {
        width:auto;
        padding:6px 10px;
        font-size:12px;
      }
      .trainCanvasWrap {
        position:relative;
        border-radius:14px;
        background:linear-gradient(180deg, #ffffff, #f8fafc);
        border:1px solid rgba(226,232,240,0.9);
        padding:8px;
      }
      .trainChartCanvas {
        width:100%;
        height:260px;
        display:block;
      }
      .trainChipCanvas {
        width:100%;
        height:96px;
        display:block;
        margin-top:6px;
        border-top:1px dashed rgba(148,163,184,0.45);
        padding-top:6px;
      }
      .trainHoverPanel {
        position:absolute;
        top:10px;
        right:10px;
        width:min(240px, calc(100% - 24px));
        border-radius:12px;
        background:rgba(15,23,42,0.92);
        color:#fff;
        padding:10px 12px;
        font-size:12px;
        line-height:1.6;
        pointer-events:auto;
        opacity:0;
        transform:translateY(-4px);
        transition:opacity .16s ease, transform .16s ease;
      }
      .trainHoverPanel.visible {
        opacity:1;
        transform:translateY(0);
      }
      .trainHoverPanel:hover {
        opacity:1;
      }
      .trainTimelineTable {
        width:100%;
        border-collapse:collapse;
        font-size:12px;
      }
      .trainTimelineTable th, .trainTimelineTable td {
        border-bottom:1px solid rgba(226,232,240,0.9);
        padding:8px 6px;
        text-align:left;
        white-space:nowrap;
      }
      .trainStatusBox {
        white-space:pre-line;
        font-size:12px;
        line-height:1.7;
        color:#334155;
      }
      @media (max-width: 1100px) {
        .trainChartStack {
          grid-template-columns:1fr;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function ensureRldSubtabs() {
    injectTrainStyle();
    const page = $("pageRld");
    if (!page || page.querySelector("#rldSubtabBar")) return;
    const analysisNode = page.querySelector(".rldWorkbench");
    if (!analysisNode) return;
    const bar = document.createElement("div");
    bar.id = "rldSubtabBar";
    bar.className = "rldSubtabBar";
    bar.innerHTML = `
      <button id="rldSubtabAnalysis" class="rldSubtabBtn" type="button">多周期分析</button>
      <button id="rldSubtabTrain" class="rldSubtabBtn" type="button">缠论训练</button>
    `;
    const analysisWrap = document.createElement("div");
    analysisWrap.id = "rldSubpanelAnalysis";
    analysisWrap.className = "rldSubpanel";
    analysisNode.parentNode.insertBefore(analysisWrap, analysisNode);
    analysisWrap.appendChild(analysisNode);
    const trainWrap = document.createElement("div");
    trainWrap.id = "rldSubpanelTrain";
    trainWrap.className = "rldSubpanel";
    trainWrap.innerHTML = `
      <div class="trainShell">
        <section class="trainPanel">
          <div class="trainHead">
            <div>
              <div class="trainHeadTitle">融立德 / 缠论训练</div>
              <div class="trainHeadSub">训练态按最小周期驱动，再把大周期对齐到当前小周期进度，避免高周期提前显示未来K线。周期支持无限扩展，支持标准周期和自定义周期N。</div>
            </div>
            <div class="trainActionRow">
              <button id="trainBtnInit" data-tip="加载缠论训练会话，周期和参数读取自“设置 > 融立德 > 缠论训练参数”。">加载训练</button>
              <button id="trainBtnReset" data-tip="重置当前训练状态并清空持仓。">重置</button>
              <button id="trainBtnGoSettings" data-tip="打开设置页并定位到融立德参数。">打开设置</button>
            </div>
          </div>
        </section>
        <section class="trainPanel">
          <div id="trainSummaryGrid" class="trainSummaryGrid"></div>
        </section>
        <section class="trainPanel">
          <div id="trainStatusBox" class="trainStatusBox">等待加载训练状态...</div>
        </section>
        <section class="trainPanel">
          <div id="trainChartStack" class="trainChartStack"></div>
        </section>
        <section class="trainPanel">
          <div class="rldCardTitle" style="margin:0 0 10px 0;">多周期时间线</div>
          <div style="overflow:auto;">
            <table class="trainTimelineTable">
              <thead><tr><th>周期</th><th>时间</th><th>价格</th><th>趋势</th><th>买卖点</th><th>CHDL</th><th>MACD</th></tr></thead>
              <tbody id="trainTimelineBody"></tbody>
            </table>
          </div>
        </section>
      </div>
    `;
    page.insertBefore(bar, analysisWrap);
    page.appendChild(trainWrap);
    const setTab = (tab) => {
      rldSubtabState = tab === "train" ? "train" : "analysis";
      storageSet("rld_subtab_active", rldSubtabState);
      $("rldSubtabAnalysis").classList.toggle("active", rldSubtabState === "analysis");
      $("rldSubtabTrain").classList.toggle("active", rldSubtabState === "train");
      $("rldSubpanelAnalysis").classList.toggle("active", rldSubtabState === "analysis");
      $("rldSubpanelTrain").classList.toggle("active", rldSubtabState === "train");
      if (rldSubtabState === "train") {
        requestAnimationFrame(() => renderTrainPayload(rldTrainPayload));
      }
    };
    $("rldSubtabAnalysis").onclick = () => setTab("analysis");
    $("rldSubtabTrain").onclick = () => setTab("train");
    setTab(rldSubtabState);
    initTooltips();
  }

  function trainCollectPayload() {
    const form = getTrainForm();
    const lvList = ensureArrayText(form.lv_tokens, TRAIN_DEFAULT_FORM.lv_tokens);
    if (sharedSettingsState.cycle_form !== "custom_group" && lvList.some((item) => /\\d+$/.test(item) && !/^(1m|3m|5m|15m|30m|60m)$/.test(item))) {
      throw new Error("当前周期形式为 standard，请先在系统设置把“周期形式”切到 custom_group 后再使用 day2 / 60m5 这类格式。");
    }
    return {
      code: form.code,
      begin_date: form.begin_date,
      end_date: form.end_date || null,
      autype: form.autype,
      initial_cash: Number(form.initial_cash || "100000"),
      lv_list: lvList,
      chan_config: JSON.parse(JSON.stringify(chanConfig)),
    };
  }

  async function callTrainApi(path, body, method, loadingText) {
    setGlobalLoading(true, loadingText);
    try {
      return await api(path, body, method || "POST");
    } finally {
      hideGlobalLoading();
    }
  }

  function updateTrainSummary(payload) {
    const grid = $("trainSummaryGrid");
    if (!grid) return;
    if (!payload || !payload.ready) {
      grid.innerHTML = `<div class="trainSummaryCard"><span class="k">状态</span><span class="v">未加载</span></div>`;
      return;
    }
    grid.innerHTML = `
      <div class="trainSummaryCard"><span class="k">当前时间</span><span class="v">${payload.time || "-"}</span></div>
      <div class="trainSummaryCard"><span class="k">驱动周期</span><span class="v">${payload.raw_level_label || "-"}</span></div>
      <div class="trainSummaryCard"><span class="k">当前索引</span><span class="v">${payload.raw_index + 1} / ${payload.raw_total}</span></div>
      <div class="trainSummaryCard"><span class="k">数据源</span><span class="v">${payload.data_source ? payload.data_source.label : "-"}</span></div>
      <div class="trainSummaryCard"><span class="k">现金</span><span class="v">${rldNumber(payload.account ? payload.account.cash : null, 2)}</span></div>
      <div class="trainSummaryCard"><span class="k">总资产</span><span class="v">${rldNumber(payload.account ? payload.account.equity : null, 2)}</span></div>
      <div class="trainSummaryCard"><span class="k">持仓股数</span><span class="v">${payload.account ? payload.account.position : "-"}</span></div>
      <div class="trainSummaryCard"><span class="k">持仓成本</span><span class="v">${rldNumber(payload.account ? payload.account.avg_cost : null, 4)}</span></div>
    `;
  }

  function updateTrainStatus(payload, message) {
    const box = $("trainStatusBox");
    if (!box) return;
    if (!payload || !payload.ready) {
      box.textContent = "等待加载训练状态...";
      return;
    }
    const lines = [
      `标的：${payload.name || payload.code}`,
      `当前时间：${payload.time}`,
      `周期：${ensureArray(payload.levels, []).map((item) => item.label).join(" / ")}`,
      `数据源：${payload.data_source ? payload.data_source.label : "-"}`,
      `尝试顺序：${getSourcePriorityHint()}`,
      ...(payload.data_source && payload.data_source.logs ? payload.data_source.logs : []),
    ];
    if (message) lines.unshift(message);
    box.textContent = lines.join("\\n");
  }

  function drawTrainChip(canvas, chip) {
    const prepared = rldPrepareCanvas(canvas);
    if (!prepared) return;
    const { ctx, width, height } = prepared;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = cssVar("--bg", "#ffffff");
    ctx.fillRect(0, 0, width, height);
    const buckets = ensureArray(chip && chip.buckets, []);
    if (!chip || !chip.available || buckets.length <= 0) {
      ctx.fillStyle = cssVar("--muted", "#64748b");
      ctx.font = "12px Arial";
      ctx.fillText(chip && chip.source ? `${chip.source} 暂无筹码数据` : "暂无筹码数据", 10, 18);
      return;
    }
    const maxVol = Math.max(1, ...buckets.map((item) => Number(item.volume || 0)));
    const barW = Math.max(4, (width - 28) / buckets.length);
    ctx.fillStyle = cssVar("--chipBg", "rgba(37,99,235,0.22)");
    ctx.fillRect(0, 0, width, height);
    buckets.forEach((item, idx) => {
      const h = Math.max(2, (Number(item.volume || 0) / maxVol) * (height - 26));
      const x = 14 + idx * barW;
      const y = height - h - 12;
      ctx.fillStyle = cssVar("--chipFill", "rgba(37,99,235,0.62)");
      ctx.fillRect(x, y, Math.max(2, barW - 2), h);
    });
    ctx.fillStyle = cssVar("--text", "#0f172a");
    ctx.font = "11px Arial";
    ctx.fillText(chip.source || "Chip", 10, 14);
  }

  function nearestTrainK(chart, timeText) {
    return rldFindNearestK(chart, timeText);
  }

  function drawTrainChart(canvas, levelItem) {
    const prepared = rldPrepareCanvas(canvas);
    if (!prepared) return;
    const { ctx, width, height } = prepared;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = cssVar("--bg", "#ffffff");
    ctx.fillRect(0, 0, width, height);
    if (!levelItem || !levelItem.chart || !Array.isArray(levelItem.chart.kline) || levelItem.chart.kline.length <= 0) {
      ctx.fillStyle = cssVar("--muted", "#64748b");
      ctx.font = "12px Arial";
      ctx.fillText("暂无K线", 16, 22);
      return;
    }
    const chart = levelItem.chart;
    const ks = chart.kline;
    const padL = 56;
    const padR = 14;
    const padT = 18;
    const padB = 26;
    const macdH = Math.max(46, Math.floor(height * 0.22));
    const priceH = height - macdH - padT - padB - 8;
    const maxPrice = Math.max(...ks.map((item) => Number(item.h)), ...ensureArray(chart.seg_zs, []).map((item) => Number(item.high || item.h || 0)));
    const minPrice = Math.min(...ks.map((item) => Number(item.l)), ...ensureArray(chart.seg_zs, []).map((item) => Number(item.low || item.l || 9999999)));
    const range = Math.max(1e-6, maxPrice - minPrice);
    const stepX = (width - padL - padR) / Math.max(1, ks.length - 1);
    const xByIndex = (idx) => padL + idx * stepX;
    const yByPrice = (price) => padT + priceH - ((price - minPrice) / range) * priceH;
    const macdItems = ensureArray(chart.indicators, []);
    const macdAbs = Math.max(1e-6, ...macdItems.map((item) => Math.abs(Number(item.macd && item.macd.macd || 0))));
    const macdBaseY = padT + priceH + 12 + macdH / 2;
    const macdScale = (macdH / 2 - 8) / macdAbs;

    ctx.strokeStyle = cssVar("--grid", "rgba(148,163,184,0.35)");
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i += 1) {
      const y = padT + (priceH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(width - padR, y);
      ctx.stroke();
    }
    ctx.fillStyle = cssVar("--text", "#64748b");
    ctx.font = "11px Arial";
    for (let i = 0; i <= 4; i += 1) {
      const price = maxPrice - (range / 4) * i;
      const y = padT + (priceH / 4) * i;
      ctx.fillText(Number(price).toFixed(2), 8, y + 4);
    }
    ks.forEach((k, idx) => {
      const x = xByIndex(idx);
      const openY = yByPrice(Number(k.o));
      const closeY = yByPrice(Number(k.c));
      const highY = yByPrice(Number(k.h));
      const lowY = yByPrice(Number(k.l));
      const isUp = Number(k.c) >= Number(k.o);
      ctx.strokeStyle = isUp ? rldChartColor("candleUp") : rldChartColor("candleDown");
      ctx.beginPath();
      ctx.moveTo(x, highY);
      ctx.lineTo(x, lowY);
      ctx.stroke();
      ctx.fillStyle = isUp ? "rgba(220,38,38,0.18)" : "rgba(22,163,74,0.55)";
      ctx.fillRect(x - Math.max(1.5, stepX * 0.22), Math.min(openY, closeY), Math.max(3, stepX * 0.44), Math.max(2, Math.abs(closeY - openY)));
    });
    const drawLineSet = (rows, color, widthPx) => {
      ensureArray(rows, []).forEach((line) => {
        ctx.strokeStyle = color;
        ctx.lineWidth = widthPx;
        ctx.beginPath();
        ctx.moveTo(xByIndex(Number(line.x1)), yByPrice(Number(line.y1)));
        ctx.lineTo(xByIndex(Number(line.x2)), yByPrice(Number(line.y2)));
        ctx.stroke();
      });
    };
    const drawZsSet = (rows, stroke, fill) => {
      ensureArray(rows, []).forEach((zs) => {
        const x1 = xByIndex(Number(zs.x1));
        const x2 = xByIndex(Number(zs.x2));
        const y1 = yByPrice(Number(zs.high));
        const y2 = yByPrice(Number(zs.low));
        ctx.fillStyle = fill;
        ctx.fillRect(x1, y1, Math.max(4, x2 - x1), Math.max(4, y2 - y1));
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 1;
        ctx.strokeRect(x1, y1, Math.max(4, x2 - x1), Math.max(4, y2 - y1));
      });
    };
    drawZsSet(chart.bi_zs, "rgba(249,115,22,0.45)", "rgba(249,115,22,0.08)");
    drawZsSet(chart.seg_zs, "rgba(14,165,233,0.45)", "rgba(14,165,233,0.08)");
    drawLineSet(chart.bi, rldChartColor("bi"), 1.3);
    drawLineSet(chart.seg, rldChartColor("seg"), 2.0);
    drawLineSet(chart.segseg, rldChartColor("segseg"), 2.5);
    ensureArray(chart.bsp, []).forEach((item) => {
      const idx = ks.findIndex((k) => Number(k.x) === Number(item.x));
      if (idx < 0) return;
      const x = xByIndex(idx);
      const y = item.is_buy ? yByPrice(Number(item.y)) + 15 : yByPrice(Number(item.y)) - 12;
      ctx.fillStyle = item.is_buy ? cssVar("--candleUp", "#b91c1c") : cssVar("--candleDown", "#15803d");
      ctx.font = "bold 11px Arial";
      ctx.fillText(item.display_label || item.label || "", x - 10, y);
    });
    ctx.strokeStyle = cssVar("--grid", "rgba(100,116,139,0.35)");
    ctx.beginPath();
    ctx.moveTo(padL, macdBaseY);
    ctx.lineTo(width - padR, macdBaseY);
    ctx.stroke();
    macdItems.forEach((item, idx) => {
      const x = xByIndex(idx);
      const val = Number(item.macd && item.macd.macd || 0);
      ctx.strokeStyle = val >= 0 ? rldChartColor("macdPos") : rldChartColor("macdNeg");
      ctx.beginPath();
      ctx.moveTo(x, macdBaseY);
      ctx.lineTo(x, macdBaseY - val * macdScale);
      ctx.stroke();
    });
    const crossTime = rldTrainCrosshair[levelItem.token] || (ks.length > 0 ? ks[ks.length - 1].t : null);
    const selectedK = nearestTrainK(chart, crossTime);
    if (selectedK) {
      const idx = ks.findIndex((item) => Number(item.x) === Number(selectedK.x));
      const x = xByIndex(Math.max(0, idx));
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = cssVar("--text", "#0f172a");
      ctx.beginPath();
      ctx.moveTo(x, padT);
      ctx.lineTo(x, height - padB);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = cssVar("--accentTitle", "#0f172a");
      ctx.font = "11px Arial";
      ctx.fillText(String(selectedK.t), Math.max(padL, x - 40), height - 6);
    }
  }

  function trainHoverHtml(levelItem, k) {
    return `
      <div><strong>${levelItem.label}</strong></div>
      <div>时间：${k ? k.t : "-"}</div>
      <div>OHLC：${k ? `${rldNumber(k.o, 3)} / ${rldNumber(k.h, 3)} / ${rldNumber(k.l, 3)} / ${rldNumber(k.c, 3)}` : "-"}</div>
      <div>趋势：${levelItem.summary ? levelItem.summary.trend_label : "-"}</div>
      <div>买卖点：${levelItem.summary && levelItem.summary.latest_bsp ? levelItem.summary.latest_bsp.display_label : "无"}</div>
      <div>中枢：${levelItem.summary ? `${levelItem.summary.zs_state.kind}${levelItem.summary.zs_state.label}` : "-"}</div>
      <div>CHDL：${levelItem.summary ? rldNumber(levelItem.summary.chdl_score) : "-"}</div>
      <div>MACD：${levelItem.summary ? rldNumber(levelItem.summary.macd_bias) : "-"}</div>
    `;
  }

  function renderTrainCharts(payload) {
    const stack = $("trainChartStack");
    if (!stack) return;
    if (!payload || !payload.ready) {
      stack.innerHTML = `<div class="trainChartCard">请先在设置页配置训练周期并加载训练。</div>`;
      return;
    }
    const levels = ensureArray(payload.levels, []);
    stack.innerHTML = levels.map((levelItem, idx) => `
      <article class="trainChartCard">
        <div class="trainChartHead">
          <div class="trainChartMeta">
            <div class="trainChartTitle">${levelItem.label}</div>
            <div class="trainChartSub">${levelItem.summary ? `${levelItem.summary.trend_label} / CHDL ${rldNumber(levelItem.summary.chdl_score)}` : ""}</div>
          </div>
          <div class="trainChartActions">
            <button type="button" data-train-step-back="${levelItem.token}" data-tip="按当前周期后退一根训练K线。">后退</button>
            <button type="button" data-train-step="${levelItem.token}" data-tip="按当前周期步进一根训练K线。">步进</button>
            <button type="button" data-train-buy="${levelItem.token}" data-tip="按当前周期最后一根可见K线收盘价执行买入。">买入</button>
            <button type="button" data-train-sell="${levelItem.token}" data-tip="按当前周期最后一根可见K线收盘价执行卖出。">卖出</button>
          </div>
        </div>
        <div class="trainCanvasWrap">
          <canvas id="trainChartCanvas${idx + 1}" class="trainChartCanvas" data-train-token="${levelItem.token}"></canvas>
          <canvas id="trainChipCanvas${idx + 1}" class="trainChipCanvas"></canvas>
          <div id="trainHover${idx + 1}" class="trainHoverPanel"></div>
        </div>
      </article>
    `).join("");
    levels.forEach((levelItem, idx) => {
      drawTrainChart($("trainChartCanvas" + (idx + 1)), levelItem);
      drawTrainChip($("trainChipCanvas" + (idx + 1)), levelItem.chip);
      const hoverEl = $("trainHover" + (idx + 1));
      const canvas = $("trainChartCanvas" + (idx + 1));
      if (!canvas || !hoverEl) return;
      const chart = levelItem.chart || {};
      const ks = ensureArray(chart.kline, []);
      if (ks.length > 0) hoverEl.innerHTML = trainHoverHtml(levelItem, ks[ks.length - 1]);
      hoverEl.onmouseenter = () => {
        hoverEl.dataset.locked = "1";
        hoverEl.classList.add("visible");
      };
      hoverEl.onmouseleave = () => {
        hoverEl.dataset.locked = "";
        hoverEl.classList.remove("visible");
      };
      canvas.onmousemove = (e) => {
        if (!ks.length) return;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const idx2 = Math.max(0, Math.min(ks.length - 1, Math.round(((x - 56) / Math.max(1, rect.width - 70)) * (ks.length - 1))));
        const k = ks[idx2];
        rldTrainCrosshair[levelItem.token] = k.t;
        hoverEl.innerHTML = trainHoverHtml(levelItem, k);
        hoverEl.classList.add("visible");
        drawTrainChart(canvas, levelItem);
      };
      canvas.onmouseleave = () => {
        if (hoverEl.dataset.locked !== "1") hoverEl.classList.remove("visible");
      };
    });
    stack.querySelectorAll("[data-train-step]").forEach((btn) => btn.onclick = () => trainStep(btn.getAttribute("data-train-step"), true));
    stack.querySelectorAll("[data-train-step-back]").forEach((btn) => btn.onclick = () => trainStep(btn.getAttribute("data-train-step-back"), false));
    stack.querySelectorAll("[data-train-buy]").forEach((btn) => btn.onclick = () => trainTrade(btn.getAttribute("data-train-buy"), "buy"));
    stack.querySelectorAll("[data-train-sell]").forEach((btn) => btn.onclick = () => trainTrade(btn.getAttribute("data-train-sell"), "sell"));
    initTooltips();
  }

  function renderTrainTimeline(payload) {
    const body = $("trainTimelineBody");
    if (!body) return;
    if (!payload || !payload.ready) {
      body.innerHTML = `<tr><td colspan="7">等待训练数据...</td></tr>`;
      return;
    }
    body.innerHTML = ensureArray(payload.timeline, []).map((item) => `
      <tr>
        <td>${item.label || "-"}</td>
        <td>${item.time || "-"}</td>
        <td>${rldNumber(item.price, 4)}</td>
        <td>${item.trend || "-"}</td>
        <td>${item.bsp || "-"}</td>
        <td>${rldNumber(item.chdl, 2)}</td>
        <td>${rldNumber(item.macd, 2)}</td>
      </tr>
    `).join("");
  }

  function renderTrainPayload(payload, message) {
    rldTrainPayload = payload;
    updateTrainSummary(payload);
    updateTrainStatus(payload, message || (payload && payload.message) || "");
    renderTrainCharts(payload);
    renderTrainTimeline(payload);
  }

  async function restoreTrainState() {
    try {
      const payload = await api("/api/rld-train/state", null, "GET");
      if (payload && payload.ready) renderTrainPayload(payload, "已恢复缠论训练会话。");
      else renderTrainPayload(null);
    } catch (e) {
      renderTrainPayload(null);
    }
  }

  async function trainLoad() {
    persistTrainSettingsFromHub();
    const body = trainCollectPayload();
    updateTrainStatus(rldTrainPayload, `正在按优先级取数：${getSourcePriorityHint()}`);
    const payload = await callTrainApi("/api/rld-train/init", body, "POST", "正在加载融立德缠论训练...");
    renderTrainPayload(payload, payload.message || "缠论训练已加载");
    return payload;
  }

  async function trainLoadSafe() {
    try {
      return await trainLoad();
    } catch (e) {
      showToast(`缂犺璁粌鍔犺浇澶辫触锛?{e.message}`, { record: false });
      if ((e.message || "").includes("离线分笔读取失败")) {
        const goSettings = window.confirm("离线分笔读取失败。是否现在跳转到“设置 > 共享”手动补充分笔路径？");
        if (goSettings) {
          rldSetTopTab("settings");
          rldSetSettingsHubTab("shared");
        }
      }
      throw e;
    }
  }

  async function trainStep(levelToken, forward) {
    try {
      const payload = await callTrainApi(forward ? "/api/rld-train/step" : "/api/rld-train/back", { level: levelToken, n: 1 }, "POST", forward ? "正在训练步进..." : "正在训练后退...");
      renderTrainPayload(payload, payload.message || (forward ? "训练步进成功" : "训练后退成功"));
    } catch (e) {
      showToast(`${forward ? "步进" : "后退"}失败：${e.message}`, { record: false });
    }
  }

  async function trainTrade(levelToken, side) {
    try {
      const payload = await callTrainApi("/api/rld-train/trade", { level: levelToken, side }, "POST", side === "buy" ? "正在执行买入..." : "正在执行卖出...");
      renderTrainPayload(payload, payload.message || "训练交易已执行");
    } catch (e) {
      showToast(`训练交易失败：${e.message}`, { record: false });
    }
  }

  function bindTrainButtons() {
    const bind = (id, fn) => {
      const el = $(id);
      if (!el || el.dataset.boundExt === "1") return;
      el.dataset.boundExt = "1";
      el.onclick = fn;
    };
    bind("trainBtnInit", () => trainLoadSafe());
    bind("trainBtnReset", async () => {
      try {
        const payload = await callTrainApi("/api/rld-train/reset", null, "POST", "正在重置缠论训练...");
        rldTrainPayload = null;
        renderTrainPayload(payload, payload.message || "缠论训练已重置");
      } catch (e) {
        showToast(`训练重置失败：${e.message}`, { record: false });
      }
    });
    bind("trainBtnGoSettings", () => {
      rldSetTopTab("settings");
      rldSetSettingsHubTab("rld");
    });
  }

  function wrapLoadButtonsForSourceHint() {
    const replayInit = $("btnInit");
    if (replayInit && replayInit.dataset.sourceWrapped !== "1" && typeof replayInit.onclick === "function") {
      const original = replayInit.onclick;
      replayInit.dataset.sourceWrapped = "1";
      replayInit.onclick = async function () {
        const el = $("dataSourceStatus");
        if (el) {
          el.textContent = `当前数据源尝试顺序：${getSourcePriorityHint()}`;
          el.title = "正在按优先级尝试数据源";
        }
        return original.apply(this, arguments);
      };
    }
    const rldInit = $("rldBtnInit");
    if (rldInit && rldInit.dataset.sourceWrapped !== "1" && typeof rldInit.onclick === "function") {
      const original = rldInit.onclick;
      rldInit.dataset.sourceWrapped = "1";
      rldInit.onclick = async function () {
        rldSetStatus(`正在按优先级尝试：${getSourcePriorityHint()}`, "busy");
        return original.apply(this, arguments);
      };
    }
  }

  function enhanceLoadButtonsFinal() {
    const replayInit = $("btnInit");
    if (replayInit && replayInit.dataset.sourceWrappedFinal !== "1" && typeof replayInit.onclick === "function") {
      const original = replayInit.onclick;
      replayInit.dataset.sourceWrappedFinal = "1";
      replayInit.onclick = async function () {
        const originalSetGlobalLoading = window.setGlobalLoading;
        if (typeof originalSetGlobalLoading === "function") {
          window.setGlobalLoading = function (visible, text) {
            const nextText = visible ? "正在加载复盘会话..." : text;
            return originalSetGlobalLoading.call(this, visible, nextText);
          };
        }
        try {
          return await original.apply(this, arguments);
        } finally {
          if (typeof originalSetGlobalLoading === "function") window.setGlobalLoading = originalSetGlobalLoading;
        }
      };
    }
    const rldInit = $("rldBtnInit");
    if (rldInit && rldInit.dataset.sourceWrappedFinal !== "1" && typeof rldInit.onclick === "function") {
      const original = rldInit.onclick;
      rldInit.dataset.sourceWrappedFinal = "1";
      rldInit.onclick = async function () {
        try {
          return await original.apply(this, arguments);
        } catch (e) {
          const useOfflineFirst = (sharedSettingsState.data_quality || "").startsWith("offline") || getSourcePriorityHint().startsWith("OfflineTXT");
          if (useOfflineFirst && String((e && e.message) || "").includes("离线")) {
            const goSettings = window.confirm("离线K线读取失败。是否现在跳转到“设置 > 共享”手动补充离线K线路径？");
            if (goSettings) {
              rldSetTopTab("settings");
              rldSetSettingsHubTab("shared");
            }
          }
          throw e;
        }
      };
    }
  }

  const TERMINAL_MENU_DEFS = [
    {
      label: "文件(F)",
      items: [
        { label: "加载复盘会话", action: () => clickUi("btnInit") },
        { label: "加载融立德工作台", action: () => clickUi("rldBtnInit") },
        { label: "加载缠论训练", action: () => clickUi("trainBtnInit") },
        { separator: true },
        { label: "重置复盘", action: () => clickUi("btnReset") },
        { label: "重置融立德", action: () => clickUi("rldBtnReset") },
        { label: "退出", action: () => clickUi("btnExit") },
      ],
    },
    {
      label: "画面(P)",
      items: [
        { label: "复盘工作区", action: () => rldSetTopTab("trainer") },
        { label: "融立德", action: () => rldSetTopTab("rld") },
        { label: "设置中心", action: () => rldSetTopTab("settings") },
        { separator: true },
        { label: "图表全屏", action: () => clickUi("btnFullscreen") },
        { label: "最新K线居中", action: () => runMaybe("centerLatestK") },
      ],
    },
    {
      label: "分析(A)",
      items: [
        { label: "应用融立德配置", action: () => clickUi("rldBtnReconfig") },
        { label: "刷新矩阵", action: () => clickUi("rldBtnMatrix") },
        { label: "运行回测", action: () => clickUi("rldBtnBacktest") },
        { separator: true },
        { label: "缠论配置", action: () => clickUi("btnChanSettingsOpen") },
        { label: "图表显示设置", action: () => clickUi("btnSettingsOpen") },
        { label: "系统配置", action: () => clickUi("btnSystemSettingsOpen") },
      ],
    },
    {
      label: "训练(T)",
      items: [
        { label: "下一根K线", action: () => clickUi("btnStep") },
        { label: "步进N根", action: () => clickUi("btnStepN") },
        { label: "后退N根", action: () => clickUi("btnBackN") },
        { separator: true },
        { label: "买入", action: () => clickUi("btnBuy") },
        { label: "卖出", action: () => clickUi("btnSell") },
      ],
    },
  ];

  const terminalViewState = Object.create(null);
  let terminalShellPatched = false;
  let terminalMenuOpenRoot = null;

  function clickUi(id) {
    const el = $(id);
    if (!el || el.disabled) return false;
    el.click();
    return true;
  }

  function runMaybe(name) {
    const fn = window[name];
    if (typeof fn === "function") return fn();
    return null;
  }

  function activeTerminalTab() {
    const raw = storageGet("chan_top_active_tab") || "trainer";
    return raw === "rld" || raw === "settings" ? raw : "trainer";
  }

  function activeRldSubtab() {
    const raw = storageGet("rld_subtab_active") || "analysis";
    return raw === "train" ? "train" : "analysis";
  }

  function injectTerminalWorkspaceStyle() {
    if ($("rldTerminalShellStyle")) return;
    const style = document.createElement("style");
    style.id = "rldTerminalShellStyle";
    style.textContent = `
      #terminalShell {
        height: 100vh;
        display: grid;
        grid-template-rows: 30px 34px minmax(0, 1fr) 26px;
        background: #050608;
        color: #d7dce2;
        overflow: hidden;
      }
      #terminalTitlebar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 0 12px;
        background: #08090b;
        border-bottom: 1px solid #23272d;
        user-select: none;
      }
      .terminalBrand {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
      }
      .terminalBrandMark {
        width: 14px;
        height: 14px;
        border: 1px solid #ff3b30;
        background:
          linear-gradient(135deg, transparent 0 38%, #ff3b30 38% 58%, transparent 58% 100%),
          linear-gradient(45deg, transparent 0 58%, #ff3b30 58% 78%, transparent 78% 100%);
      }
      .terminalBrandText {
        font-size: 12px;
        font-weight: 600;
        color: #f4f4f5;
        white-space: nowrap;
      }
      .terminalBrandSub {
        font-size: 11px;
        color: #9aa3ad;
        white-space: nowrap;
      }
      .terminalWindowButtons {
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .terminalWindowButtons button {
        width: 26px;
        height: 18px;
        padding: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
      }
      #terminalMenuBar {
        display: flex;
        align-items: center;
        gap: 0;
        padding: 0 6px;
        background: #111317;
        border-bottom: 1px solid #23272d;
        position: relative;
        z-index: 120;
      }
      .terminalMenuRoot {
        width: auto;
        min-width: 72px;
        height: 100%;
        padding: 0 14px;
        border: none;
        border-right: 1px solid #23272d;
        background: transparent;
        color: #d7dce2;
        font-size: 12px;
        text-align: left;
      }
      .terminalMenuRoot:hover,
      .terminalMenuRoot.active {
        background: var(--hoverBg);
        color: var(--hoverText);
      }
      #terminalMenuHost {
        position: absolute;
        top: 100%;
        left: 0;
        z-index: 125;
      }
      .terminalMenuPanel {
        min-width: 220px;
        border: 1px solid var(--border);
        background: var(--panel);
        box-shadow: 8px 10px 0 rgba(0, 0, 0, 0.15);
      }
      .terminalMenuItem,
      .terminalMenuSep {
        display: block;
      }
      .terminalMenuItem {
        width: 100%;
        padding: 7px 12px;
        border: none;
        border-bottom: 1px solid var(--border);
        background: transparent;
        color: var(--text);
        font-size: 12px;
        text-align: left;
      }
      .terminalMenuItem:last-child {
        border-bottom: none;
      }
      .terminalMenuItem:hover {
        background: var(--hoverBg);
        color: var(--hoverText);
      }
      .terminalMenuSep {
        height: 1px;
        background: var(--border);
      }
      #terminalBody {
        min-height: 0;
        display: grid;
        grid-template-columns: 44px minmax(0, 1fr) 128px;
        background: var(--bg);
        overflow: hidden;
      }
      #terminalRailMount {
        min-height: 0;
        border-right: 1px solid var(--border);
        background: var(--panel);
      }
      #topTabBar.terminalRail {
        display: flex;
        flex-direction: column;
        gap: 0;
        height: 100%;
        padding: 0;
        border-bottom: none;
        background: transparent;
      }
      #topTabBar.terminalRail .tabButton {
        min-width: 0;
        width: 100%;
        height: 88px;
        padding: 8px 0;
        border: none;
        border-bottom: 1px solid var(--border);
        background: transparent;
        color: var(--muted);
        writing-mode: vertical-rl;
        text-orientation: mixed;
        letter-spacing: 0.12em;
        font-size: 11px;
        font-weight: 700;
      }
      #topTabBar.terminalRail .tabButton.active,
      #topTabBar.terminalRail .tabButton:hover {
        background: var(--hoverBg);
        color: var(--hoverText);
        box-shadow: inset 2px 0 0 var(--accent);
      }
      #terminalWorkspace {
        min-height: 0;
        overflow: hidden;
        background: var(--bg);
      }
      #topPageShell {
        height: 100%;
        overflow: hidden;
      }
      .topPage {
        height: 100%;
        min-height: 0;
      }
      #pageTrainer,
      #pageRld,
      #pageSettings {
        height: 100%;
        min-height: 0;
        overflow: auto;
        background: var(--bg);
      }
      #pageTrainer .wrap {
        height: 100%;
      }
      #pageTrainer .left {
        border-left: none;
        border-right: 1px solid var(--border);
        background: var(--panel);
      }
      #pageTrainer .right {
        background: var(--chartBg);
      }
      #pageTrainer .card,
      #pageTrainer .chartToolsPanel {
        background: var(--panel);
        border-color: var(--border);
      }
      #pageTrainer #chart {
        background: var(--chartBg);
      }
      #terminalRightRail {
        min-height: 0;
        overflow: auto;
        border-left: 1px solid var(--border);
        background: var(--panel);
        padding: 8px 6px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .terminalSideSection {
        border: 1px solid var(--border);
        background: var(--panel);
      }
      .terminalSideTitle {
        padding: 6px 7px;
        border-bottom: 1px solid var(--border);
        color: var(--muted);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .terminalSideContent {
        padding: 6px;
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .terminalSideContent button,
      .terminalCycleBadge,
      .terminalInfoBadge {
        width: 100%;
        min-height: 28px;
        padding: 4px 6px;
        font-size: 11px;
      }
      .terminalCycleBadge,
      .terminalInfoBadge {
        border: 1px solid var(--border);
        background: var(--btn);
        color: var(--btnText);
        text-align: center;
        box-sizing: border-box;
      }
      .terminalCycleBadge.active {
        border-color: var(--accent);
        color: var(--hoverText);
      }
      #terminalStatusBar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        padding: 0 10px;
        background: var(--panel);
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-size: 11px;
      }
      #terminalStatusLeft,
      #terminalStatusRight {
        display: flex;
        align-items: center;
        gap: 10px;
        white-space: nowrap;
        overflow: hidden;
      }
      #terminalStatusLeft span,
      #terminalStatusRight span {
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .rldWorkbench,
      .settingsHubPage {
        min-height: 100%;
        padding: 10px;
        box-sizing: border-box;
        background: var(--bg) !important;
      }
      .rldPanel,
      .trainPanel,
      .settingsHubCard,
      .settingsHubInner {
        border: 1px solid var(--border) !important;
        border-radius: 0 !important;
        background: var(--panel) !important;
        box-shadow: none !important;
        color: var(--text);
      }
      .rldCardTitle,
      .trainHeadTitle,
      .settingsHubHeroTitle,
      .settingsHubHead,
      .settingsHubSectionTitle,
      .trainChartTitle {
        color: var(--accentTitle) !important;
      }
      .settingsHubHero,
      .rldHeaderBar,
      .trainHead {
        border: 1px solid var(--border);
        border-radius: 0 !important;
        background: var(--panel) !important;
        box-shadow: none !important;
      }
      .rldMetaRow,
      .settingsHubHeroText,
      .settingsHubHint,
      .trainHeadSub,
      .trainChartSub,
      .rldStatus,
      .trainStatusBox {
        color: var(--muted) !important;
      }
      .rldBadge {
        border-radius: 0 !important;
        background: var(--btn) !important;
        color: var(--btnText) !important;
      }
      .rldBadge.buy {
        background: var(--candleUpFill) !important;
        color: var(--candleUp) !important;
      }
      .rldBadge.sell {
        background: var(--candleDownFill) !important;
        color: var(--candleDown) !important;
      }
      .rldSummaryGrid,
      .trainSummaryGrid,
      .sharedSettingGrid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 8px;
      }
      .rldSummaryCard,
      .trainSummaryCard,
      .sharedSettingChip {
        border: 1px solid var(--border) !important;
        border-radius: 0 !important;
        background: var(--panel) !important;
        padding: 8px 10px;
      }
      .rldSummaryCard .k,
      .trainSummaryCard .k,
      .sharedSettingChip span {
        color: var(--muted) !important;
        font-size: 10px !important;
      }
      .rldSummaryCard .v,
      .trainSummaryCard .v,
      .sharedSettingChip strong {
        color: var(--text) !important;
        font-size: 16px !important;
        font-weight: 700 !important;
      }
      .rldChartStack,
      .trainChartStack {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
        gap: 10px;
      }
      .rldChartCard,
      .trainChartCard {
        border: 1px solid var(--border);
        background: var(--panel);
        min-height: 0;
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .rldChartHead,
      .trainChartHead {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 8px;
        color: #d7dce2;
        font-size: 12px;
      }
      .rldChartHead span {
        display: block;
        color: #8f98a4;
        font-size: 11px;
        margin-top: 2px;
      }
      .rldChartFrame,
      .trainChartFrame {
        min-height: 0;
        display: grid;
        grid-template-columns: minmax(0, 1fr) 122px;
        gap: 8px;
      }
      .rldChartCanvasHost,
      .trainChartCanvasHost {
        position: relative;
        min-height: 0;
        border: 1px solid #23272d;
        background: #000000;
      }
      .rldChartCanvas,
      .trainChartCanvas {
        width: 100%;
        height: 320px;
        display: block;
        background: #000000;
      }
      .rldChipPane,
      .trainChipPane {
        display: grid;
        grid-template-rows: 1fr auto;
        gap: 8px;
      }
      .rldChipCanvas,
      .trainChipCanvas {
        width: 100%;
        height: 320px;
        display: block;
        border: 1px solid #23272d;
        background: #090b0f;
      }
      .rldChipStats,
      .trainChipStats {
        border: 1px solid #23272d;
        background: #10141a;
        color: #d7dce2;
        font-family: Consolas, monospace;
        font-size: 11px;
        line-height: 1.6;
        padding: 7px 8px;
        white-space: pre-line;
      }
      .rldHoverPanel,
      .trainHoverPanel {
        position: absolute;
        top: 8px;
        left: 8px;
        width: min(248px, calc(100% - 16px));
        border: 1px solid #353b44;
        border-radius: 0;
        background: rgba(8, 10, 12, 0.94);
        color: #d7dce2;
        padding: 8px 10px;
        font-size: 11px;
        line-height: 1.6;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.14s ease;
      }
      .rldHoverPanel.visible,
      .trainHoverPanel.visible {
        opacity: 1;
      }
      .terminalTimelineShell {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .terminalTimelineHead {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        flex-wrap: wrap;
        color: #9aa3ad;
        font-size: 11px;
      }
      .terminalTimelineGrid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 8px;
      }
      .terminalTimelineCard {
        border: 1px solid #23272d;
        background: #10141a;
        padding: 8px 9px;
        color: #d7dce2;
        font-size: 11px;
        line-height: 1.65;
        cursor: pointer;
      }
      .terminalTimelineCard:hover {
        border-color: #f0a53a;
      }
      .terminalTimelineCard .k {
        color: #8f98a4;
      }
      .trainTimelineWrap {
        overflow: auto;
        border: 1px solid #23272d;
        background: #0f1216;
      }
      .trainTimelineTable,
      .rldTable {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
      }
      .trainTimelineTable th,
      .trainTimelineTable td,
      .rldTable th,
      .rldTable td {
        border-bottom: 1px solid rgba(43,47,54,0.9);
        padding: 6px 6px;
        text-align: left;
        white-space: nowrap;
      }
      .trainTimelineTable th,
      .rldTable th {
        background: #11151a;
        color: #9aa3ad;
        position: sticky;
        top: 0;
        z-index: 1;
      }
      .trainTimelineTable tr:hover td,
      .rldTable tr:hover td {
        background: rgba(240,165,58,0.08);
      }
      @media (max-width: 1360px) {
        #terminalBody {
          grid-template-columns: 44px minmax(0, 1fr) 112px;
        }
        .rldChartStack,
        .trainChartStack {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 1024px) {
        #terminalShell {
          grid-template-rows: 34px 34px minmax(0, 1fr) 28px;
        }
        #terminalBody {
          grid-template-columns: 38px minmax(0, 1fr);
        }
        #terminalRightRail {
          display: none;
        }
        .rldChartFrame,
        .trainChartFrame {
          grid-template-columns: 1fr;
        }
        .rldChipCanvas,
        .trainChipCanvas {
          height: 180px;
        }
      }
      @media (max-width: 780px) {
        #terminalShell {
          height: auto;
          min-height: 100vh;
          overflow: auto;
        }
        #terminalBody {
          min-height: 0;
          overflow: visible;
        }
        #terminalWorkspace,
        #topPageShell,
        .topPage,
        #pageTrainer,
        #pageRld,
        #pageSettings {
          overflow: visible;
          height: auto;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function renderTerminalMenuPanels() {
    const host = $("terminalMenuHost");
    const bar = $("terminalMenuBar");
    if (!host || !bar) return;
    if (!terminalMenuOpenRoot) {
      host.innerHTML = "";
      bar.querySelectorAll(".terminalMenuRoot").forEach((btn) => btn.classList.remove("active"));
      return;
    }
    const def = TERMINAL_MENU_DEFS[terminalMenuOpenRoot];
    if (!def) return;
    host.innerHTML = `
      <div class="terminalMenuPanel">
        ${def.items.map((item, idx) => item.separator
          ? '<div class="terminalMenuSep"></div>'
          : `<button class="terminalMenuItem" type="button" data-terminal-menu-item="${terminalMenuOpenRoot}:${idx}">${item.label}</button>`
        ).join("")}
      </div>
    `;
    bar.querySelectorAll(".terminalMenuRoot").forEach((btn, idx) => btn.classList.toggle("active", idx === terminalMenuOpenRoot));
    host.querySelectorAll("[data-terminal-menu-item]").forEach((btn) => {
      btn.onclick = () => {
        const [rootIdx, itemIdx] = String(btn.getAttribute("data-terminal-menu-item") || "").split(":").map((x) => Number(x));
        const item = TERMINAL_MENU_DEFS[rootIdx] && TERMINAL_MENU_DEFS[rootIdx].items[itemIdx];
        terminalMenuOpenRoot = null;
        renderTerminalMenuPanels();
        if (item && typeof item.action === "function") item.action();
      };
    });
  }

  function ensureTerminalShell() {
    injectTerminalWorkspaceStyle();
    const topTabBar = $("topTabBar");
    const pageShell = $("topPageShell");
    if (!topTabBar || !pageShell) return;
    if (!$("terminalShell")) {
      const root = document.createElement("div");
      root.id = "terminalShell";
      root.innerHTML = `
        <div id="terminalTitlebar">
          <div class="terminalBrand">
            <span class="terminalBrandMark"></span>
            <span class="terminalBrandText">金字塔决策交易系统</span>
            <span id="terminalBrandSub" class="terminalBrandSub">融立德 / 技术分析</span>
          </div>
          <div class="terminalWindowButtons">
            <button id="terminalMinBtn" type="button">_</button>
            <button id="terminalMaxBtn" type="button">□</button>
            <button id="terminalCloseBtn" type="button">×</button>
          </div>
        </div>
        <div id="terminalMenuBar">
          ${TERMINAL_MENU_DEFS.map((item, idx) => `<button class="terminalMenuRoot" type="button" data-terminal-root="${idx}">${item.label}</button>`).join("")}
          <div id="terminalMenuHost"></div>
        </div>
        <div id="terminalBody">
          <aside id="terminalRailMount"></aside>
          <main id="terminalWorkspace"></main>
          <aside id="terminalRightRail">
            <section class="terminalSideSection">
              <div class="terminalSideTitle">快捷命令</div>
              <div id="terminalActionList" class="terminalSideContent"></div>
            </section>
            <section class="terminalSideSection">
              <div class="terminalSideTitle">周期 / 训练</div>
              <div id="terminalCycleList" class="terminalSideContent"></div>
            </section>
            <section class="terminalSideSection">
              <div class="terminalSideTitle">状态摘要</div>
              <div id="terminalInfoList" class="terminalSideContent"></div>
            </section>
          </aside>
        </div>
        <div id="terminalStatusBar">
          <div id="terminalStatusLeft"></div>
          <div id="terminalStatusRight"></div>
        </div>
      `;
      const parent = topTabBar.parentNode;
      parent.insertBefore(root, topTabBar);
      $("terminalRailMount").appendChild(topTabBar);
      $("terminalWorkspace").appendChild(pageShell);
      $("terminalMinBtn").onclick = () => {
        const rail = $("terminalRightRail");
        if (rail) rail.style.display = rail.style.display === "none" ? "" : "none";
      };
      $("terminalMaxBtn").onclick = () => clickUi("btnFullscreen");
      $("terminalCloseBtn").onclick = () => clickUi("btnExit");
      document.addEventListener("click", (e) => {
        if (!terminalMenuOpenRoot) return;
        const target = e.target;
        if (target && (target.closest("#terminalMenuBar") || target.closest("#terminalMenuHost"))) return;
        terminalMenuOpenRoot = null;
        renderTerminalMenuPanels();
      });
    }
    topTabBar.classList.add("terminalRail");
    topTabBar.querySelectorAll(".tabButton").forEach((btn) => btn.classList.add("terminalRailButton"));
    topTabBar.style.position = "static";
    topTabBar.style.zIndex = "auto";
    const bar = $("terminalMenuBar");
    if (bar && bar.dataset.bound !== "1") {
      bar.dataset.bound = "1";
      bar.querySelectorAll(".terminalMenuRoot").forEach((btn) => {
        btn.onclick = (e) => {
          e.stopPropagation();
          const idx = Number(btn.getAttribute("data-terminal-root") || 0);
          terminalMenuOpenRoot = terminalMenuOpenRoot === idx ? null : idx;
          renderTerminalMenuPanels();
        };
      });
    }
  }

  function summarizeChipBucketsJs(buckets, currentPrice) {
    const rows = ensureArray(buckets, [])
      .map((item) => ({ price: Number(item.price), volume: Number(item.volume || 0) }))
      .filter((item) => Number.isFinite(item.price) && Number.isFinite(item.volume) && item.volume > 0)
      .sort((a, b) => a.price - b.price);
    const empty = { bucket_count: 0, total_volume: 0, peak_price: null, avg_cost: null, benefit_ratio: null, band70: { low: null, high: null }, band90: { low: null, high: null } };
    if (rows.length <= 0) return empty;
    const total = rows.reduce((sum, item) => sum + item.volume, 0);
    const avg = rows.reduce((sum, item) => sum + item.price * item.volume, 0) / total;
    const peak = rows.reduce((best, item) => {
      if (!best || item.volume > best.volume || (item.volume === best.volume && item.price < best.price)) return item;
      return best;
    }, null);
    const tightBand = (ratio) => {
      const target = total * ratio;
      let best = null;
      let left = 0;
      let acc = 0;
      for (let right = 0; right < rows.length; right += 1) {
        acc += rows[right].volume;
        while (left <= right && acc - rows[left].volume >= target) {
          acc -= rows[left].volume;
          left += 1;
        }
        if (acc < target) continue;
        const width = rows[right].price - rows[left].price;
        if (!best || width < best.width || (width === best.width && rows[left].price < best.low)) {
          best = { width, low: rows[left].price, high: rows[right].price };
        }
      }
      return best ? { low: best.low, high: best.high } : { low: rows[0].price, high: rows[rows.length - 1].price };
    };
    const benefit = Number.isFinite(Number(currentPrice))
      ? rows.filter((item) => item.price <= Number(currentPrice)).reduce((sum, item) => sum + item.volume, 0) / total
      : null;
    return {
      bucket_count: rows.length,
      total_volume: total,
      peak_price: peak ? peak.price : null,
      avg_cost: avg,
      benefit_ratio: benefit,
      band70: tightBand(0.7),
      band90: tightBand(0.9),
    };
  }

  function buildChipFromKlineRows(chart) {
    const ks = ensureArray(chart && chart.kline, []);
    if (ks.length <= 0) {
      return { available: false, source: "KLineChip", buckets: [], summary: summarizeChipBucketsJs([], null) };
    }
    const step = 0.05;
    const hist = Object.create(null);
    ks.forEach((item) => {
      const price = Number(item.c);
      const volume = Math.max(1, Number(item.v || item.volume || 0) || 1);
      const bucket = (Math.round(price / step) * step).toFixed(2);
      hist[bucket] = (hist[bucket] || 0) + volume;
    });
    const buckets = Object.keys(hist)
      .map((price) => ({ price: Number(price), volume: hist[price] }))
      .sort((a, b) => a.price - b.price);
    return {
      available: buckets.length > 0,
      source: "KLineChip",
      buckets,
      summary: summarizeChipBucketsJs(buckets, ks[ks.length - 1] ? Number(ks[ks.length - 1].c) : null),
    };
  }

  function chipStatsText(chip) {
    const summary = chip && chip.summary ? chip.summary : summarizeChipBucketsJs([], null);
    if (!chip || !chip.available || ensureArray(chip.buckets, []).length <= 0) {
      return `来源：${chip && chip.source ? chip.source : "无"}\n暂无筹码数据`;
    }
    const ratio = summary.benefit_ratio === null || summary.benefit_ratio === undefined ? "-" : `${(Number(summary.benefit_ratio) * 100).toFixed(1)}%`;
    const avg = summary.avg_cost === null || summary.avg_cost === undefined ? "-" : Number(summary.avg_cost).toFixed(3);
    const peak = summary.peak_price === null || summary.peak_price === undefined ? "-" : Number(summary.peak_price).toFixed(3);
    const band90 = summary.band90 && summary.band90.low !== null ? `${Number(summary.band90.low).toFixed(2)} - ${Number(summary.band90.high).toFixed(2)}` : "-";
    const band70 = summary.band70 && summary.band70.low !== null ? `${Number(summary.band70.low).toFixed(2)} - ${Number(summary.band70.high).toFixed(2)}` : "-";
    return `来源：${chip.source || "-"}\n获利比例：${ratio}\n平均成本：${avg}\n筹码峰值：${peak}\n90%成本：${band90}\n70%成本：${band70}`;
  }

  function drawTerminalChipPane(canvas, chip) {
    const prepared = rldPrepareCanvas(canvas);
    if (!prepared) return;
    const { ctx, width, height } = prepared;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = cssVar("--bg", "#090b0f");
    ctx.fillRect(0, 0, width, height);
    const buckets = ensureArray(chip && chip.buckets, []);
    if (!chip || !chip.available || buckets.length <= 0) {
      ctx.fillStyle = cssVar("--muted", "#8f98a4");
      ctx.font = "11px Consolas";
      ctx.fillText(chip && chip.source ? chip.source : "暂无筹码", 8, 16);
      return;
    }
    const maxVol = Math.max(1, ...buckets.map((item) => Number(item.volume || 0)));
    const summary = chip.summary || summarizeChipBucketsJs(buckets, null);
    const priceMin = Math.min(...buckets.map((item) => Number(item.price)));
    const priceMax = Math.max(...buckets.map((item) => Number(item.price)));
    const y = (price) => {
      const span = Math.max(0.001, priceMax - priceMin || 0.001);
      return 16 + ((priceMax - price) / span) * (height - 32);
    };
    ctx.fillStyle = cssVar("--chipBg", "rgba(240,165,58,0.12)");
    ctx.fillRect(0, 0, width, height);
    buckets.forEach((item) => {
      const len = (Number(item.volume || 0) / maxVol) * (width - 18);
      const yTop = y(Number(item.price) + 0.025);
      const yBottom = y(Number(item.price) - 0.025);
      const barH = Math.max(1, yBottom - yTop);
      ctx.fillStyle = cssVar("--chipFill", "rgba(240,165,58,0.85)");
      ctx.fillRect(width - 8 - len, yTop, len, barH);
    });
    if (summary && summary.peak_price !== null && summary.peak_price !== undefined) {
      const peakY = y(Number(summary.peak_price));
      ctx.strokeStyle = cssVar("--candleUp", "#ff3b30");
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.moveTo(4, peakY);
      ctx.lineTo(width - 4, peakY);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.strokeStyle = cssVar("--border", "#3a3f46");
    ctx.strokeRect(0.5, 0.5, width - 1, height - 1);
  }

  function ensureTerminalView(scope, key, chart) {
    const ks = ensureArray(chart && chart.kline, []);
    const viewId = `${scope}:${key}`;
    if (ks.length <= 0) {
      terminalViewState[viewId] = { xMin: 0, xMax: 1, yZoom: 1, yShift: 0, ready: false };
      return terminalViewState[viewId];
    }
    const allMin = Number(ks[0].x);
    const allMax = Number(ks[ks.length - 1].x);
    let state = terminalViewState[viewId];
    if (!state) {
      state = { xMin: allMin, xMax: allMax, yZoom: 1, yShift: 0, userAdjusted: false };
      terminalViewState[viewId] = state;
    }
    if (!state.userAdjusted) {
      state.xMin = allMin;
      state.xMax = allMax;
    }
    if (state.xMax <= state.xMin) {
      state.xMin = allMin;
      state.xMax = allMax;
      state.userAdjusted = false;
    }
    if (state.xMin < allMin) {
      const span = state.xMax - state.xMin;
      state.xMin = allMin;
      state.xMax = state.xMin + span;
    }
    state.ready = true;
    state.allMin = allMin;
    state.allMax = allMax;
    return state;
  }

  function buildTerminalScaler(canvas, chart, view) {
    const prepared = rldPrepareCanvas(canvas);
    if (!prepared) return null;
    const { ctx, width, height } = prepared;
    const padL = 48;
    const padR = 10;
    const padT = 14;
    const padB = 20;
    const macdH = Math.max(46, Math.floor(height * 0.18));
    const priceBottom = height - padB - macdH - 10;
    let visibleKs = ensureArray(chart && chart.kline, []).filter((item) => Number(item.x) >= view.xMin && Number(item.x) <= view.xMax);
    if (visibleKs.length <= 0) visibleKs = ensureArray(chart && chart.kline, []);
    let yMin = Infinity;
    let yMax = -Infinity;
    visibleKs.forEach((item) => {
      yMin = Math.min(yMin, Number(item.l));
      yMax = Math.max(yMax, Number(item.h));
    });
    [...ensureArray(chart && chart.bi_zs, []), ...ensureArray(chart && chart.seg_zs, [])].forEach((item) => {
      const x1 = Number(item.x1);
      const x2 = Number(item.x2);
      if (x2 < view.xMin || x1 > view.xMax) return;
      yMin = Math.min(yMin, Number(item.low || item.l || yMin));
      yMax = Math.max(yMax, Number(item.high || item.h || yMax));
    });
    if (!Number.isFinite(yMin) || !Number.isFinite(yMax) || yMax <= yMin) {
      yMin = 0;
      yMax = 1;
    }
    const baseSpan = Math.max(0.001, yMax - yMin);
    const midY = (yMax + yMin) / 2;
    const zoomed = baseSpan / Math.max(0.2, Number(view.yZoom || 1));
    yMin = midY - zoomed / 2 + baseSpan * Number(view.yShift || 0);
    yMax = midY + zoomed / 2 + baseSpan * Number(view.yShift || 0);
    const xSpan = Math.max(1, view.xMax - view.xMin);
    const ySpan = Math.max(0.001, yMax - yMin);
    return {
      ctx,
      width,
      height,
      padL,
      padR,
      padT,
      padB,
      priceBottom,
      macdH,
      xMin: view.xMin,
      xMax: view.xMax,
      visibleKs,
      x: (value) => padL + ((Number(value) - view.xMin) / xSpan) * (width - padL - padR),
      y: (price) => padT + ((yMax - Number(price)) / ySpan) * (priceBottom - padT),
      plotW: width - padL - padR,
      yMin,
      yMax,
    };
  }

  function terminalHoverHtml(levelItem, k) {
    const summary = levelItem && levelItem.summary ? levelItem.summary : {};
    return `
      <div><strong>${levelItem.label || levelItem.level || "-"}</strong></div>
      <div>时间：${k ? k.t : "-"}</div>
      <div>OHLC：${k ? `${rldNumber(k.o, 3)} / ${rldNumber(k.h, 3)} / ${rldNumber(k.l, 3)} / ${rldNumber(k.c, 3)}` : "-"}</div>
      <div>趋势：${summary.trend_label || "-"}</div>
      <div>买卖点：${summary.latest_bsp ? summary.latest_bsp.display_label : "无"}</div>
      <div>中枢：${summary.zs_state ? `${summary.zs_state.kind}${summary.zs_state.label}` : "-"}</div>
      <div>CHDL：${rldNumber(summary.chdl_score)}</div>
      <div>MACD：${rldNumber(summary.macd_bias)}</div>
    `;
  }

  function drawTerminalKlineChart(canvas, levelItem, scope, key, crosshairTime) {
    const chart = ensureObject(levelItem && levelItem.chart, {});
    const view = ensureTerminalView(scope, key, chart);
    const scaler = buildTerminalScaler(canvas, chart, view);
    if (!scaler) return;
    const { ctx, width, height, padL, padR, padT, priceBottom, macdH, visibleKs, x, y } = scaler;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = cssVar("--chartBg", "#000000");
    ctx.fillRect(0, 0, width, height);
    if (visibleKs.length <= 0) {
      ctx.fillStyle = cssVar("--muted", "#8f98a4");
      ctx.font = "12px Consolas";
      ctx.fillText("暂无K线", 12, 20);
      return;
    }
    ctx.strokeStyle = cssVar("--grid", "rgba(120, 32, 32, 0.45)");
    ctx.setLineDash([3, 5]);
    for (let i = 0; i < 5; i += 1) {
      const yLine = padT + ((priceBottom - padT) / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padL, yLine);
      ctx.lineTo(width - padR, yLine);
      ctx.stroke();
    }
    ctx.setLineDash([]);
    ctx.fillStyle = cssVar("--text", "#ff4d4f");
    ctx.font = "11px Consolas";
    for (let i = 0; i < 5; i += 1) {
      const price = scaler.yMax - ((scaler.yMax - scaler.yMin) / 4) * i;
      const yLine = padT + ((priceBottom - padT) / 4) * i;
      ctx.fillText(Number(price).toFixed(2), width - padR + 2, yLine + 4);
    }
    const bodyW = Math.max(3, scaler.plotW / Math.max(26, visibleKs.length * 1.2));
    visibleKs.forEach((k) => {
      const xPos = x(k.x);
      const openY = y(k.o);
      const closeY = y(k.c);
      const highY = y(k.h);
      const lowY = y(k.l);
      const isUp = Number(k.c) >= Number(k.o);
      ctx.strokeStyle = isUp ? "#ff3b30" : "#27d6dc";
      ctx.beginPath();
      ctx.moveTo(xPos, highY);
      ctx.lineTo(xPos, lowY);
      ctx.stroke();
      ctx.fillStyle = isUp ? "rgba(255,59,48,0.18)" : "rgba(39,214,220,0.6)";
      ctx.fillRect(xPos - bodyW / 2, Math.min(openY, closeY), bodyW, Math.max(2, Math.abs(closeY - openY)));
    });
    const drawLineSet = (rows, color, widthPx) => {
      ensureArray(rows, []).forEach((line) => {
        if (Number(line.x2) < scaler.xMin || Number(line.x1) > scaler.xMax) return;
        ctx.strokeStyle = color;
        ctx.lineWidth = widthPx;
        ctx.beginPath();
        ctx.moveTo(x(line.x1), y(line.y1));
        ctx.lineTo(x(line.x2), y(line.y2));
        ctx.stroke();
      });
    };
    const drawZsSet = (rows, stroke, fill) => {
      ensureArray(rows, []).forEach((zs) => {
        if (Number(zs.x2) < scaler.xMin || Number(zs.x1) > scaler.xMax) return;
        const x1 = x(zs.x1);
        const x2 = x(zs.x2);
        const y1 = y(zs.high);
        const y2 = y(zs.low);
        ctx.fillStyle = fill;
        ctx.fillRect(x1, y1, Math.max(4, x2 - x1), Math.max(4, y2 - y1));
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 1;
        ctx.strokeRect(x1, y1, Math.max(4, x2 - x1), Math.max(4, y2 - y1));
      });
    };
    drawZsSet(chart.bi_zs, "rgba(240,165,58,0.6)", "rgba(240,165,58,0.12)");
    drawZsSet(chart.seg_zs, "rgba(39,214,220,0.55)", "rgba(39,214,220,0.1)");
    drawLineSet(chart.bi, "#f0a53a", 1.2);
    drawLineSet(chart.seg, "#58cb83", 1.8);
    drawLineSet(chart.segseg, "#8db6ff", 2.2);
    ensureArray(chart.bsp, []).forEach((item) => {
      const xPos = x(item.x);
      const yPos = item.is_buy ? y(item.y) + 13 : y(item.y) - 10;
      ctx.fillStyle = item.is_buy ? "#ff837c" : "#7ff2f7";
      ctx.font = "bold 10px Consolas";
      ctx.fillText(item.display_label || item.label || "", xPos - 12, yPos);
    });
    const macdItems = ensureArray(chart.indicators, []).filter((item) => Number(item.x) >= scaler.xMin && Number(item.x) <= scaler.xMax);
    const macdBaseY = priceBottom + 10 + macdH / 2;
    const macdAbs = Math.max(0.001, ...macdItems.map((item) => Math.abs(Number(item.macd && item.macd.macd || 0))));
    const macdScale = (macdH / 2 - 6) / macdAbs;
    ctx.strokeStyle = cssVar("--border", "#3a3f46");
    ctx.beginPath();
    ctx.moveTo(padL, macdBaseY);
    ctx.lineTo(width - padR, macdBaseY);
    ctx.stroke();
    macdItems.forEach((item) => {
      const xPos = x(item.x);
      const val = Number(item.macd && item.macd.macd || 0);
      ctx.strokeStyle = val >= 0 ? cssVar("--candleUp", "#ff3b30") : cssVar("--candleDown", "#27d6dc");
      ctx.beginPath();
      ctx.moveTo(xPos, macdBaseY);
      ctx.lineTo(xPos, macdBaseY - val * macdScale);
      ctx.stroke();
    });
    const selectedK = rldFindNearestK(chart, crosshairTime) || visibleKs[visibleKs.length - 1];
    if (selectedK) {
      const crossX = x(selectedK.x);
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = cssVar("--text", "#d7dce2");
      ctx.beginPath();
      ctx.moveTo(crossX, padT);
      ctx.lineTo(crossX, height - 18);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = cssVar("--accentTitle", "#f7c97e");
      ctx.font = "11px Consolas";
      ctx.fillText(String(selectedK.t), Math.max(padL, crossX - 56), height - 4);
    }
  }

  function bindTerminalCanvas(canvas, levelItem, scope, key, hoverEl, redraw, getCrosshair, setCrosshair) {
    if (!canvas || canvas.dataset.terminalBound === "1") return;
    canvas.dataset.terminalBound = "1";
    let drag = null;
    canvas.onwheel = (e) => {
      e.preventDefault();
      const chart = ensureObject(levelItem && levelItem.chart, {});
      const view = ensureTerminalView(scope, key, chart);
      const rect = canvas.getBoundingClientRect();
      const rel = (e.clientX - rect.left - 48) / Math.max(1, rect.width - 58);
      const anchor = view.xMin + clamp(rel, 0, 1) * Math.max(1, view.xMax - view.xMin);
      if (e.ctrlKey) {
        view.yZoom = clamp(view.yZoom * (e.deltaY > 0 ? 0.92 : 1.08), 0.45, 3.8);
      } else {
        const span = Math.max(5, view.xMax - view.xMin);
        const factor = e.deltaY > 0 ? 1.16 : 0.86;
        const newSpan = clamp(span * factor, 5, Math.max(5, (view.allMax || view.xMax) - (view.allMin || view.xMin) + 32));
        view.xMin = Math.round(anchor - clamp(rel, 0, 1) * newSpan);
        view.xMax = Math.round(view.xMin + newSpan);
        if (view.xMin < view.allMin) {
          view.xMin = view.allMin;
          view.xMax = view.xMin + newSpan;
        }
        view.userAdjusted = true;
      }
      redraw();
    };
    canvas.onpointerdown = (e) => {
      const chart = ensureObject(levelItem && levelItem.chart, {});
      const view = ensureTerminalView(scope, key, chart);
      canvas.setPointerCapture(e.pointerId);
      drag = {
        pointerId: e.pointerId,
        startX: e.clientX,
        startY: e.clientY,
        xMin: view.xMin,
        xMax: view.xMax,
        yShift: view.yShift || 0,
      };
    };
    canvas.onpointermove = (e) => {
      const chart = ensureObject(levelItem && levelItem.chart, {});
      const view = ensureTerminalView(scope, key, chart);
      const ks = ensureArray(chart.kline, []);
      if (drag && drag.pointerId === e.pointerId) {
        const rect = canvas.getBoundingClientRect();
        const span = Math.max(5, drag.xMax - drag.xMin);
        const dxBars = Math.round((-(e.clientX - drag.startX) / Math.max(1, rect.width - 58)) * span);
        view.xMin = drag.xMin + dxBars;
        view.xMax = drag.xMax + dxBars;
        if (view.xMin < view.allMin) {
          const delta = view.allMin - view.xMin;
          view.xMin += delta;
          view.xMax += delta;
        }
        view.yShift = clamp(drag.yShift + ((e.clientY - drag.startY) / Math.max(1, rect.height)) * 0.8, -1.5, 1.5);
        view.userAdjusted = true;
        redraw();
        return;
      }
      if (ks.length <= 0) return;
      const rect = canvas.getBoundingClientRect();
      const rel = clamp((e.clientX - rect.left - 48) / Math.max(1, rect.width - 58), 0, 1);
      const scaler = buildTerminalScaler(canvas, chart, view);
      const visible = scaler ? scaler.visibleKs : ks;
      const targetX = view.xMin + rel * Math.max(1, view.xMax - view.xMin);
      const nearest = nearestKByX(visible, targetX) || visible[visible.length - 1];
      if (nearest) {
        setCrosshair(nearest.t);
        if (hoverEl) {
          hoverEl.innerHTML = terminalHoverHtml(levelItem, nearest);
          hoverEl.classList.add("visible");
        }
        redraw();
      }
    };
    canvas.onpointerup = (e) => {
      if (drag && drag.pointerId === e.pointerId) {
        drag = null;
        canvas.releasePointerCapture(e.pointerId);
      }
    };
    canvas.onpointercancel = () => {
      drag = null;
    };
    canvas.onmouseleave = () => {
      if (hoverEl) hoverEl.classList.remove("visible");
    };
    canvas.ondblclick = () => {
      const chart = ensureObject(levelItem && levelItem.chart, {});
      const view = ensureTerminalView(scope, key, chart);
      view.xMin = view.allMin;
      view.xMax = view.allMax;
      view.yZoom = 1;
      view.yShift = 0;
      view.userAdjusted = false;
      redraw();
    };
  }

  function renderTrainChartsTerminal(payload) {
    const stack = $("trainChartStack");
    if (!stack) return;
    if (!payload || !payload.ready) {
      stack.innerHTML = `<div class="trainChartCard">请先在设置页配置训练周期并加载训练。</div>`;
      return;
    }
    const levels = ensureArray(payload.levels, []);
    stack.innerHTML = levels.map((levelItem, idx) => `
      <article class="trainChartCard">
        <div class="trainChartHead">
          <div class="trainChartMeta">
            <div class="trainChartTitle">${levelItem.label}</div>
            <div class="trainChartSub">${levelItem.summary ? `${levelItem.summary.trend_label} / CHDL ${rldNumber(levelItem.summary.chdl_score)}` : ""}</div>
          </div>
          <div class="trainChartActions">
            <button type="button" data-train-step-back="${levelItem.token}">后退</button>
            <button type="button" data-train-step="${levelItem.token}">步进</button>
            <button type="button" data-train-buy="${levelItem.token}">买入</button>
            <button type="button" data-train-sell="${levelItem.token}">卖出</button>
          </div>
        </div>
        <div class="trainChartFrame">
          <div class="trainChartCanvasHost">
            <canvas id="trainChartCanvas${idx + 1}" class="trainChartCanvas" data-train-token="${levelItem.token}"></canvas>
            <div id="trainHover${idx + 1}" class="trainHoverPanel"></div>
          </div>
          <div class="trainChipPane">
            <canvas id="trainChipCanvas${idx + 1}" class="trainChipCanvas"></canvas>
            <div id="trainChipStats${idx + 1}" class="trainChipStats"></div>
          </div>
        </div>
      </article>
    `).join("");
    levels.forEach((levelItem, idx) => {
      const chartCanvas = $("trainChartCanvas" + (idx + 1));
      const chipCanvas = $("trainChipCanvas" + (idx + 1));
      const hoverEl = $("trainHover" + (idx + 1));
      const statsEl = $("trainChipStats" + (idx + 1));
      const redraw = () => drawTerminalKlineChart(chartCanvas, levelItem, "train", levelItem.token || String(idx), rldTrainCrosshair[levelItem.token] || (levelItem.chart && levelItem.chart.kline && levelItem.chart.kline.length > 0 ? levelItem.chart.kline[levelItem.chart.kline.length - 1].t : null));
      redraw();
      drawTerminalChipPane(chipCanvas, levelItem.chip);
      if (statsEl) statsEl.textContent = chipStatsText(levelItem.chip);
      bindTerminalCanvas(
        chartCanvas,
        levelItem,
        "train",
        levelItem.token || String(idx),
        hoverEl,
        redraw,
        () => rldTrainCrosshair[levelItem.token],
        (value) => { rldTrainCrosshair[levelItem.token] = value; }
      );
      if (hoverEl && levelItem.chart && ensureArray(levelItem.chart.kline, []).length > 0) {
        hoverEl.innerHTML = terminalHoverHtml(levelItem, levelItem.chart.kline[levelItem.chart.kline.length - 1]);
      }
    });
    stack.querySelectorAll("[data-train-step]").forEach((btn) => btn.onclick = () => trainStep(btn.getAttribute("data-train-step"), true));
    stack.querySelectorAll("[data-train-step-back]").forEach((btn) => btn.onclick = () => trainStep(btn.getAttribute("data-train-step-back"), false));
    stack.querySelectorAll("[data-train-buy]").forEach((btn) => btn.onclick = () => trainTrade(btn.getAttribute("data-train-buy"), "buy"));
    stack.querySelectorAll("[data-train-sell]").forEach((btn) => btn.onclick = () => trainTrade(btn.getAttribute("data-train-sell"), "sell"));
  }

  function renderTrainTimelineTerminal(payload) {
    const body = $("trainTimelineBody");
    if (!body) return;
    if (!payload || !payload.ready) {
      body.innerHTML = `<tr><td colspan="9">等待训练数据...</td></tr>`;
      return;
    }
    body.parentElement && body.parentElement.parentElement && (body.parentElement.parentElement.parentElement.className = "trainTimelineWrap");
    const rows = ensureArray(payload.levels, []).map((item) => {
      const summary = item.summary || {};
      const chip = item.chip || {};
      const chipSummary = chip.summary || {};
      return {
        token: item.token,
        label: item.label,
        time: item.last_time || "-",
        price: item.last_price,
        trend: summary.trend_label || "-",
        bsp: summary.latest_bsp ? summary.latest_bsp.display_label : "无",
        chdl: summary.chdl_score,
        macd: summary.macd_bias,
        chipSource: chip.source || "-",
        benefit: chipSummary.benefit_ratio === null || chipSummary.benefit_ratio === undefined ? "-" : `${(Number(chipSummary.benefit_ratio) * 100).toFixed(1)}%`,
      };
    });
    body.innerHTML = rows.map((item) => `
      <tr data-train-timeline-token="${item.token}">
        <td>${item.label}</td>
        <td>${item.time}</td>
        <td>${rldNumber(item.price, 4)}</td>
        <td>${item.trend}</td>
        <td>${item.bsp}</td>
        <td>${rldNumber(item.chdl, 2)}</td>
        <td>${rldNumber(item.macd, 2)}</td>
        <td>${item.chipSource}</td>
        <td>${item.benefit}</td>
      </tr>
    `).join("");
    body.querySelectorAll("[data-train-timeline-token]").forEach((row) => {
      row.onclick = () => {
        const token = row.getAttribute("data-train-timeline-token");
        const level = ensureArray(payload.levels, []).find((item) => item.token === token);
        if (!level || !level.chart || !ensureArray(level.chart.kline, []).length) return;
        rldTrainCrosshair[token] = level.chart.kline[level.chart.kline.length - 1].t;
        renderTrainCharts(payload);
      };
    });
  }

  function renderRldChartsTerminal() {
    const stack = $("rldChartStack");
    if (!stack) return;
    if (!rldPayload || !rldPayload.ready || !rldPayload.analysis) {
      stack.innerHTML = `<div class="rldChartCard">请先到“设置”页配置周期并加载数据。</div>`;
      return;
    }
    const levels = ensureArray(rldPayload.analysis.levels, []);
    if (levels.length <= 0) {
      stack.innerHTML = `<div class="rldChartCard">当前结果没有可绘制的周期数据。</div>`;
      return;
    }
    stack.innerHTML = levels.map((levelItem, idx) => `
      <div class="rldChartCard">
        <div class="rldChartHead">
          <div>
            <strong>${levelItem.label}</strong>
            <span>${levelItem.summary ? `${levelItem.summary.trend_label} / CHDL ${rldNumber(levelItem.summary.chdl_score)}` : ""}</span>
          </div>
          <div class="rldBadge ${levelItem.summary && levelItem.summary.trend_sign > 0 ? "buy" : levelItem.summary && levelItem.summary.trend_sign < 0 ? "sell" : ""}">
            ${levelItem.summary ? levelItem.summary.trend_label : "等待"}
          </div>
        </div>
        <div class="rldChartFrame">
          <div class="rldChartCanvasHost">
            <canvas id="rldChart${idx + 1}" class="rldChartCanvas" data-rld-chart-index="${idx}"></canvas>
            <div id="rldHover${idx + 1}" class="rldHoverPanel"></div>
          </div>
          <div class="rldChipPane">
            <canvas id="rldChip${idx + 1}" class="rldChipCanvas"></canvas>
            <div id="rldChipStats${idx + 1}" class="rldChipStats"></div>
          </div>
        </div>
      </div>
    `).join("");
    levels.forEach((levelItem, idx) => {
      const chartCanvas = $("rldChart" + (idx + 1));
      const chipCanvas = $("rldChip" + (idx + 1));
      const hoverEl = $("rldHover" + (idx + 1));
      const statsEl = $("rldChipStats" + (idx + 1));
      const chip = buildChipFromKlineRows(levelItem.chart);
      const redraw = () => drawTerminalKlineChart(chartCanvas, levelItem, "analysis", levelItem.label || String(idx), rldCrosshairTime || (levelItem.chart && levelItem.chart.kline && levelItem.chart.kline.length > 0 ? levelItem.chart.kline[levelItem.chart.kline.length - 1].t : null));
      redraw();
      drawTerminalChipPane(chipCanvas, chip);
      if (statsEl) statsEl.textContent = chipStatsText(chip);
      bindTerminalCanvas(
        chartCanvas,
        levelItem,
        "analysis",
        levelItem.label || String(idx),
        hoverEl,
        () => {
          redraw();
          renderRldPerspectiveTerminal();
        },
        () => rldCrosshairTime,
        (value) => { rldCrosshairTime = value; }
      );
      if (hoverEl && levelItem.chart && ensureArray(levelItem.chart.kline, []).length > 0) {
        hoverEl.innerHTML = terminalHoverHtml(levelItem, levelItem.chart.kline[levelItem.chart.kline.length - 1]);
      }
    });
  }

  function renderRldPerspectiveTerminal() {
    const box = $("rldPerspective");
    if (!box) return;
    if (!rldPayload || !rldPayload.ready || !rldPayload.analysis) {
      box.innerHTML = `<div class="terminalTimelineShell"><div class="terminalTimelineHead"><span>等待加载</span></div></div>`;
      return;
    }
    const levels = ensureArray(rldPayload.analysis.levels, []);
    let pivotTime = rldCrosshairTime;
    if (!pivotTime && levels[0] && levels[0].chart && ensureArray(levels[0].chart.kline, []).length > 0) {
      pivotTime = levels[0].chart.kline[levels[0].chart.kline.length - 1].t;
    }
    const agg = rldPayload.analysis.aggregate || {};
    box.innerHTML = `
      <div class="terminalTimelineShell">
        <div class="terminalTimelineHead">
          <span>同步时间轴：${pivotTime || "-"}</span>
          <span>RLD_BS：${agg.rld_bs ? `${agg.rld_bs.side} ${rldNumber(agg.rld_bs.score)}` : "-"}</span>
          <span>一根筋：${agg.one_line ? "是" : "否"}</span>
          <span>多周期 MACD：${rldNumber(agg.three_macd)}</span>
        </div>
        <div class="terminalTimelineGrid">
          ${levels.map((level) => {
            const nearest = rldFindNearestK(level.chart, pivotTime);
            return `
              <div class="terminalTimelineCard" data-rld-timeline-time="${nearest ? nearest.t : ""}">
                <div><strong>${level.label}</strong></div>
                <div><span class="k">时间：</span>${nearest ? nearest.t : "-"}</div>
                <div><span class="k">价格：</span>${nearest ? rldNumber(nearest.c, 4) : "-"}</div>
                <div><span class="k">趋势：</span>${level.summary.trend_label}</div>
                <div><span class="k">买卖点：</span>${level.summary.latest_bsp ? level.summary.latest_bsp.display_label : "无"}</div>
                <div><span class="k">中枢：</span>${level.summary.zs_state.kind}${level.summary.zs_state.label}</div>
                <div><span class="k">CHDL / MACD：</span>${rldNumber(level.summary.chdl_score)} / ${rldNumber(level.summary.macd_bias)}</div>
              </div>
            `;
          }).join("")}
        </div>
        <div class="rldMetaRow">${agg.rld_bs && agg.rld_bs.reasons ? agg.rld_bs.reasons.map((item) => `<span>${item}</span>`).join("") : "<span>-</span>"}</div>
      </div>
    `;
    box.querySelectorAll("[data-rld-timeline-time]").forEach((card) => {
      card.onclick = () => {
        const time = card.getAttribute("data-rld-timeline-time");
        if (!time) return;
        rldCrosshairTime = time;
        renderRldPerspectiveTerminal();
        renderRldChartsTerminal();
      };
    });
  }

  function syncTerminalStatus() {
    const left = $("terminalStatusLeft");
    const right = $("terminalStatusRight");
    const actions = $("terminalActionList");
    const cycles = $("terminalCycleList");
    const info = $("terminalInfoList");
    const sub = $("terminalBrandSub");
    if (!left || !right || !actions || !cycles || !info || !sub) return;

    const tab = activeTerminalTab();
    const subtab = activeRldSubtab();
    let sourceLabel = "-";
    let symbol = "-";
    let time = "-";
    let extra = [];
    let actionRows = [];
    let cycleRows = [];
    let infoRows = [];

    if (tab === "trainer") {
      sub.textContent = "复盘 / 技术分析";
      sourceLabel = lastPayload && lastPayload.data_source ? lastPayload.data_source.label : "未加载";
      symbol = lastPayload && lastPayload.ready ? `${lastPayload.name || lastPayload.code}` : "复盘待载入";
      time = lastPayload && lastPayload.ready ? (lastPayload.time || "-") : "-";
      actionRows = [
        { label: "加载会话", id: "btnInit" },
        { label: "下一根", id: "btnStep" },
        { label: "步进N", id: "btnStepN" },
        { label: "后退N", id: "btnBackN" },
        { label: "买入", id: "btnBuy" },
        { label: "卖出", id: "btnSell" },
      ];
      cycleRows = [
        { label: `N=${getStepNValue()}`, active: true },
        { label: getActionShortcutDisplay("nextBar") || "Space" },
        { label: getActionShortcutDisplay("buyAll") || "PageUp" },
      ];
      infoRows = [
        `数据源 ${sourceLabel}`,
        lastPayload && lastPayload.ready ? `现金 ${rldNumber(lastPayload.account ? lastPayload.account.cash : null, 2)}` : "等待加载",
        lastPayload && lastPayload.ready ? `持仓 ${lastPayload.account ? lastPayload.account.position : 0}` : "持仓 -",
      ];
      extra = [
        `模式：复盘`,
        lastPayload && lastPayload.ready ? `最新价 ${rldNumber(lastPayload.price, 4)}` : "最新价 -",
      ];
    } else if (tab === "rld" && subtab === "analysis") {
      sub.textContent = "融立德 / 多周期分析";
      sourceLabel = rldPayload && rldPayload.ready && rldPayload.data_source ? ensureArray(rldPayload.data_source.logs, [])[0] || "已加载" : "未加载";
      symbol = rldPayload && rldPayload.ready ? `${rldPayload.name || rldPayload.code}` : "融立德待载入";
      time = rldCrosshairTime || (rldPayload && rldPayload.ready && rldPayload.analysis && rldPayload.analysis.levels && rldPayload.analysis.levels[0] && rldPayload.analysis.levels[0].chart && ensureArray(rldPayload.analysis.levels[0].chart.kline, []).slice(-1)[0] ? rldPayload.analysis.levels[0].chart.kline.slice(-1)[0].t : "-");
      actionRows = [
        { label: "加载工作台", id: "rldBtnInit" },
        { label: "应用配置", id: "rldBtnReconfig" },
        { label: "刷新矩阵", id: "rldBtnMatrix" },
        { label: "运行回测", id: "rldBtnBacktest" },
        { label: "设置", onClick: () => { rldSetTopTab("settings"); rldSetSettingsHubTab("rld"); } },
      ];
      cycleRows = ensureArray(rldPayload && rldPayload.lv_labels, []).map((label, idx) => ({ label, active: idx === 0 }));
      infoRows = [
        rldPayload && rldPayload.analysis ? `CHDL ${rldNumber(rldPayload.analysis.aggregate.weighted_chdl)}` : "CHDL -",
        rldPayload && rldPayload.analysis ? `MACD ${rldNumber(rldPayload.analysis.aggregate.three_macd)}` : "MACD -",
        rldPayload && rldPayload.analysis ? `RLD_BS ${rldPayload.analysis.aggregate.rld_bs.side}` : "RLD_BS -",
      ];
      extra = [
        `模式：融立德分析`,
        rldPayload && rldPayload.analysis ? `一根筋 ${rldPayload.analysis.aggregate.one_line ? "是" : "否"}` : "一根筋 -",
      ];
    } else if (tab === "rld" && subtab === "train") {
      sub.textContent = "融立德 / 缠论训练";
      sourceLabel = rldTrainPayload && rldTrainPayload.ready && rldTrainPayload.data_source ? rldTrainPayload.data_source.label : "未加载";
      symbol = rldTrainPayload && rldTrainPayload.ready ? `${rldTrainPayload.name || rldTrainPayload.code}` : "训练待载入";
      time = rldTrainPayload && rldTrainPayload.ready ? rldTrainPayload.time : "-";
      actionRows = [
        { label: "加载训练", onClick: () => trainLoadSafe() },
        { label: "重置训练", id: "trainBtnReset" },
        { label: "打开设置", id: "trainBtnGoSettings" },
      ];
      cycleRows = ensureArray(rldTrainPayload && rldTrainPayload.levels, []).map((item) => ({ label: item.label, active: true }));
      infoRows = [
        rldTrainPayload && rldTrainPayload.account ? `现金 ${rldNumber(rldTrainPayload.account.cash, 2)}` : "现金 -",
        rldTrainPayload && rldTrainPayload.account ? `总资产 ${rldNumber(rldTrainPayload.account.equity, 2)}` : "总资产 -",
        rldTrainPayload && rldTrainPayload.account ? `持仓 ${rldTrainPayload.account.position}` : "持仓 -",
      ];
      extra = [
        `模式：缠论训练`,
        rldTrainPayload && rldTrainPayload.raw_level_label ? `驱动周期 ${rldTrainPayload.raw_level_label}` : "驱动周期 -",
      ];
    } else {
      sub.textContent = "设置 / 终端配置";
      sourceLabel = "设置页";
      symbol = "系统参数";
      actionRows = [
        { label: "共享设置", onClick: () => rldSetSettingsHubTab("shared") },
        { label: "复盘参数", onClick: () => rldSetSettingsHubTab("trainer") },
        { label: "融立德参数", onClick: () => rldSetSettingsHubTab("rld") },
      ];
      cycleRows = [
        { label: sharedSettingsState.data_quality || "-" },
        { label: sharedSettingsState.cycle_form || "-" },
        { label: sharedSettingsState.chip_data_quality || "-" },
      ];
      infoRows = [
        `数据优先级`,
        getSourcePriorityHint(),
      ];
      extra = ["模式：设置中心"];
    }

    left.innerHTML = `<span>${symbol}</span><span>${time}</span><span>${sourceLabel}</span>`;
    right.innerHTML = extra.map((item) => `<span>${item}</span>`).join("");
    actions.innerHTML = actionRows.map((item, idx) => `<button type="button" data-terminal-action="${idx}">${item.label}</button>`).join("");
    actions.querySelectorAll("[data-terminal-action]").forEach((btn) => {
      const item = actionRows[Number(btn.getAttribute("data-terminal-action") || 0)];
      btn.onclick = () => {
        if (!item) return;
        if (item.id) clickUi(item.id);
        else if (typeof item.onClick === "function") item.onClick();
      };
    });
    cycles.innerHTML = cycleRows.map((item) => `<div class="terminalCycleBadge ${item.active ? "active" : ""}">${item.label}</div>`).join("");
    info.innerHTML = infoRows.map((item) => `<div class="terminalInfoBadge">${item}</div>`).join("");
    if ($("topTabRld")) $("topTabRld").textContent = "融立德";
  }

  function installTerminalOverrides() {
    if (terminalShellPatched) {
      ensureTerminalShell();
      syncTerminalStatus();
      return;
    }
    terminalShellPatched = true;
    ensureTerminalShell();

    const originalRefreshUi = refreshUI;
    refreshUI = function () {
      const result = originalRefreshUi.apply(this, arguments);
      syncTerminalStatus();
      return result;
    };

    const originalRldRefresh = rldRefresh;
    rldRefresh = function () {
      const result = originalRldRefresh.apply(this, arguments);
      syncTerminalStatus();
      return result;
    };

    const originalRldSetTopTab = rldSetTopTab;
    rldSetTopTab = function () {
      const result = originalRldSetTopTab.apply(this, arguments);
      syncTerminalStatus();
      return result;
    };

    renderTrainCharts = renderTrainChartsTerminal;
    renderTrainTimeline = renderTrainTimelineTerminal;
    rldDrawAllCharts = renderRldChartsTerminal;
    rldRenderPerspective = renderRldPerspectiveTerminal;
    syncTerminalStatus();
  }

  async function bootstrapRldTrainExtension() {
    await loadSharedSettings();
    wrapSystemSettingsFunctions();
    if (typeof renderSystemSettingsForm === "function" && isSystemSettingsOpen()) renderSystemSettingsForm();
    injectSharedSummaryIntoSettingsHub();
    mountTrainSettingsIntoHub();
    ensureRldSubtabs();
    installTerminalOverrides();
    bindTrainButtons();
    wrapLoadButtonsForSourceHint();
    enhanceLoadButtonsFinal();
    renderSharedSettingsSummary();
    await restoreTrainState();
    if (rldPayload && rldPayload.ready) {
      rldDrawAllCharts();
      rldRenderPerspective();
    }
    if (rldTrainPayload && rldSubtabState === "train") {
      renderTrainPayload(rldTrainPayload);
    }
    syncTerminalStatus();
  }

  window.addEventListener("resize", () => {
    if (rldSubtabState === "train") renderTrainPayload(rldTrainPayload);
    if (rldPayload && rldPayload.ready) {
      rldDrawAllCharts();
      rldRenderPerspective();
    }
    syncTerminalStatus();
  });

  bootstrapRldTrainExtension();
})();
"""
