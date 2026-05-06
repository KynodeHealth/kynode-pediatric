// Copyright 2026 KYNODE
// Licensed under the Apache License, Version 2.0.

const state = {
  lang: KYNODE_I18N[localStorage.getItem("kynode-demo-lang")] ? localStorage.getItem("kynode-demo-lang") : "en",
  data: null,
};

function t(key) {
  return KYNODE_I18N[state.lang][key] || key;
}

function flagLabel(flag) {
  return KYNODE_I18N[state.lang].flags[flag] || flag;
}

function setLanguage(lang) {
  if (!KYNODE_I18N[lang]) lang = "en";
  state.lang = lang;
  localStorage.setItem("kynode-demo-lang", lang);
  document.documentElement.lang = lang;
  document.querySelectorAll(".lang").forEach((button) => {
    const active = button.dataset.lang === lang;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  if (state.data) render(state.data);
}

function chipClass(flag) {
  if (flag.includes("critical") || flag.includes("high_severity")) return "danger";
  if (flag.includes("abnormal") || flag === "low" || flag === "high" || flag === "anomaly") return "warning";
  return "ok";
}

function renderList(id, items, max = 4) {
  const list = document.getElementById(id);
  list.replaceChildren();
  items.slice(0, max).forEach((item) => {
    const li = document.createElement("li");
    const label = document.createElement("strong");
    label.textContent = item.label;
    const date = document.createElement("span");
    date.textContent = item.target_date || item.date || "";
    li.append(label, date);
    list.appendChild(li);
  });
  if (items.length === 0) {
    const li = document.createElement("li");
    const label = document.createElement("strong");
    label.textContent = t("none");
    const dash = document.createElement("span");
    dash.textContent = "-";
    li.append(label, dash);
    list.appendChild(li);
  }
}

function render(data) {
  document.getElementById("child-id").textContent = data.child.display_id;
  document.getElementById("child-context").textContent = data.child.context;
  document.getElementById("child-age").textContent = `${data.child.age_months} ${t("months")}`;
  document.getElementById("child-sex").textContent = data.child.sex === "female" ? t("female") : data.child.sex;
  document.getElementById("child-zone").textContent = data.child.zone;
  document.getElementById("privacy-copy").textContent = state.lang === "en" ? data.privacy.phi_boundary : t("privacyStatement");

  const triageList = document.getElementById("triage-list");
  triageList.replaceChildren();
  Object.entries(data.triage.values).forEach(([key, value]) => {
    const row = document.createElement("div");
    const flag = data.triage.flags[key];
    const range = data.triage.ranges[key];
    const labelWrap = document.createElement("div");
    const label = document.createElement("strong");
    label.textContent = KYNODE_I18N[state.lang].vitals[key];
    const rangeLabel = document.createElement("span");
    rangeLabel.textContent = range ? `${range[0]}-${range[1]}` : "";
    const valueLabel = document.createElement("div");
    valueLabel.className = "metric-value";
    valueLabel.textContent = value;
    const chip = document.createElement("span");
    chip.className = `chip ${chipClass(flag)}`;
    chip.textContent = flagLabel(flag);
    row.className = "metric-row";
    labelWrap.append(label, rangeLabel);
    row.append(labelWrap, valueLabel, chip);
    triageList.appendChild(row);
  });

  document.getElementById("growth-z").textContent = data.growth.z_score;
  document.getElementById("growth-percentile").textContent = `${data.growth.percentile}%`;
  const growthChip = document.getElementById("growth-interpretation");
  growthChip.className = `chip ${chipClass(data.growth.interpretation)}`;
  growthChip.textContent = flagLabel(data.growth.interpretation);
  document.getElementById("growth-formula").textContent = data.growth.formula_used;

  renderList("vaccines-completed", data.vaccinations.completed, 3);
  renderList("vaccines-overdue", data.vaccinations.overdue, 4);
  renderList("vaccines-upcoming", data.vaccinations.upcoming, 3);
  document.getElementById("vaccine-source").textContent = `${data.vaccinations.source.source_name} · ${data.vaccinations.source.validation_status}`;

  document.getElementById("signal-z").textContent = data.signal.z_score;
  document.getElementById("signal-severity").textContent = flagLabel(data.signal.flag);
  document.getElementById("signal-history").textContent = `[${data.signal.historical_counts.join(", ")}]`;
  document.getElementById("signal-current").textContent = data.signal.current_count;
  document.getElementById("export-record").textContent = JSON.stringify(data.signal.exportable_record, null, 2);
}

document.querySelectorAll(".lang").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});

fetch("data/demo-output.json")
  .then((response) => {
    if (!response.ok) throw new Error(`Demo payload failed to load: ${response.status}`);
    return response.json();
  })
  .then((data) => {
    state.data = data;
    setLanguage(state.lang);
  })
  .catch(() => {
    const error = document.createElement("p");
    error.className = "load-error";
    error.textContent = t("loadError");
    document.body.appendChild(error);
  });
