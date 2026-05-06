// Copyright 2026 KYNODE
// Licensed under the Apache License, Version 2.0.

const state = {
  lang: localStorage.getItem("kynode-demo-lang") || "en",
  data: null,
};

function t(key) {
  return KYNODE_I18N[state.lang][key] || key;
}

function flagLabel(flag) {
  return KYNODE_I18N[state.lang].flags[flag] || flag;
}

function setLanguage(lang) {
  state.lang = lang;
  localStorage.setItem("kynode-demo-lang", lang);
  document.documentElement.lang = lang;
  document.querySelectorAll(".lang").forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === lang);
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
  list.innerHTML = "";
  items.slice(0, max).forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${item.label}</strong><span>${item.target_date || item.date || ""}</span>`;
    list.appendChild(li);
  });
  if (items.length === 0) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>None</strong><span>-</span>`;
    list.appendChild(li);
  }
}

function render(data) {
  document.getElementById("child-id").textContent = data.child.display_id;
  document.getElementById("child-context").textContent = data.child.context;
  document.getElementById("child-age").textContent = `${data.child.age_months} ${t("months")}`;
  document.getElementById("child-sex").textContent = data.child.sex === "female" ? t("female") : data.child.sex;
  document.getElementById("child-zone").textContent = data.child.zone;
  document.getElementById("privacy-copy").textContent = state.lang === "en"
    ? data.privacy.phi_boundary
    : "Los datos identificables permanecen en la clinica. Solo sale la senal agregada por zona.";

  const triageList = document.getElementById("triage-list");
  triageList.innerHTML = "";
  Object.entries(data.triage.values).forEach(([key, value]) => {
    const row = document.createElement("div");
    const flag = data.triage.flags[key];
    const range = data.triage.ranges[key];
    row.className = "metric-row";
    row.innerHTML = `
      <div>
        <strong>${KYNODE_I18N[state.lang].vitals[key]}</strong>
        <span>${range ? `${range[0]}-${range[1]}` : ""}</span>
      </div>
      <div class="metric-value">${value}</div>
      <span class="chip ${chipClass(flag)}">${flagLabel(flag)}</span>
    `;
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
  .then((response) => response.json())
  .then((data) => {
    state.data = data;
    setLanguage(state.lang);
  })
  .catch(() => {
    document.body.insertAdjacentHTML("beforeend", "<p class='load-error'>Run python demo/generate_demo_data.py first.</p>");
  });
