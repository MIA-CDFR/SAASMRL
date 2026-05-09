// ── TABS ───────────────────────────────────────────────
window.showTab = function(tabId) {
  document.querySelectorAll('[id^="tab-"]').forEach(el => el.style.display = "none");
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove("active"));
  document.getElementById(tabId).style.display = "block";
  document.getElementById("btn-" + tabId.replace("tab-", "")).classList.add("active");

  // Leaflet precisa de ser inicializado depois do div estar visível
  if (tabId === "tab-map" && !window.mapInitialized) {
    inicializarMapa();
    window.mapInitialized = true;
  }
};

showTab("tab-ranking");

// ── CARREGAR CSVs ──────────────────────────────────────
Promise.all([
  d3.csv("dance4life_activity.csv"),
  d3.csv("dance4life_invitation.csv"),
  d3.csv("dance4life_matching.csv"),
  d3.csv("dance4life_movement_recommendation.csv")
]).then(([activity, invitation, matching, recommendation]) => {

  // ── AGREGAÇÃO POR UTILIZADOR ───────────────────────
  const activityCount      = d3.rollup(activity, v => v.length, d => d.userId);
  const invitationTotal    = d3.rollup(invitation, v => v.length, d => d.userId);
  const invitationAccepted = d3.rollup(
    invitation.filter(d => d.status === "accepted"),
    v => v.length, d => d.userId
  );
  const matchingCount = d3.rollup(matching, v => v.length, d => d.userId);
  const recCount      = d3.rollup(recommendation, v => v.length, d => d.userId);

  const allUsers = [...new Set([
    ...activity.map(d => d.userId),
    ...invitation.map(d => d.userId),
    ...matching.map(d => d.userId),
    ...recommendation.map(d => d.userId)
  ])];

  let dataset = allUsers.map(userId => ({
    userId,
    activityCount:      activityCount.get(userId) || 0,
    invitationTotal:    invitationTotal.get(userId) || 0,
    invitationAccepted: invitationAccepted.get(userId) || 0,
    matchingCount:      matchingCount.get(userId) || 0,
    recCount:           recCount.get(userId) || 0,
  }));

  dataset = dataset.map(d => ({
    ...d,
    score: d.activityCount + d.invitationAccepted + d.matchingCount + d.recCount
  }));

  dataset.sort((a, b) => b.score - a.score);
  dataset = dataset.map((d, i) => ({ ...d, rank: i + 1 }));

  window.dataset = dataset;

  // ── TABELA ─────────────────────────────────────────
  const table = d3.select("#output").append("table");

  table.append("tr").selectAll("th")
    .data(["Rank", "Utilizador", "Atividades", "Convites", "Aceites", "Matchings", "Recomendações", "Score"])
    .join("th").text(d => d);

  table.selectAll("tr.row")
    .data(dataset)
    .join("tr")
    .attr("class", d => {
      if (d.rank === 1) return "row top1";
      if (d.rank === 2) return "row top2";
      if (d.rank === 3) return "row top3";
      return "row";
    })
    .on("click", (event, d) => {
      document.getElementById("search-input").value = d.userId;
      searchUser();
    })
    .selectAll("td")
    .data(d => [d.rank, d.userId, d.activityCount, d.invitationTotal, d.invitationAccepted, d.matchingCount, d.recCount, d.score])
    .join("td").text(d => d);

  // ── GRÁFICO DE BARRAS — TOP 10 ─────────────────────
  const top10 = dataset.slice(0, 10);

  const margin = { top: 20, right: 20, bottom: 60, left: 40 };
  const width  = 500 - margin.left - margin.right;
  const height = 300 - margin.top  - margin.bottom;

  const svg = d3.select("#bar-chart")
    .attr("width",  width  + margin.left + margin.right)
    .attr("height", height + margin.top  + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
    .domain(top10.map(d => d.userId))
    .range([0, width])
    .padding(0.2);

  const y = d3.scaleLinear()
    .domain([0, d3.max(top10, d => d.score)])
    .range([height, 0]);

  svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x))
    .selectAll("text").attr("transform", "rotate(-35)").style("text-anchor", "end");

  svg.append("g").call(d3.axisLeft(y));

  svg.selectAll("rect")
    .data(top10)
    .join("rect")
    .attr("x", d => x(d.userId))
    .attr("y", d => y(d.score))
    .attr("width", x.bandwidth())
    .attr("height", d => height - y(d.score))
    .attr("fill", "#4a90d9")
    .style("cursor", "pointer")
    .on("click", (event, d) => {
      document.getElementById("search-input").value = d.userId;
      searchUser();
    });

  // ── LINHA TEMPORAL ─────────────────────────────────
  const parseDate   = d3.timeParse("%Y-%m-%d %H:%M:%S");
  const formatMonth = d3.timeFormat("%Y-%m");

  const activityByMonth = d3.rollup(
    activity,
    v => v.length,
    d => formatMonth(parseDate(d.date))
  );

  const timelineData = Array.from(activityByMonth, ([month, count]) => ({
    date: new Date(month + "-01"),
    count
  })).sort((a, b) => a.date - b.date);

  const tmMargin = { top: 20, right: 30, bottom: 50, left: 50 };
  const tmWidth  = 700 - tmMargin.left - tmMargin.right;
  const tmHeight = 350 - tmMargin.top  - tmMargin.bottom;

  const tmSvg = d3.select("#timeline-chart")
    .attr("width",  tmWidth  + tmMargin.left + tmMargin.right)
    .attr("height", tmHeight + tmMargin.top  + tmMargin.bottom)
    .append("g")
    .attr("transform", `translate(${tmMargin.left},${tmMargin.top})`);

  const xTm = d3.scaleTime()
    .domain(d3.extent(timelineData, d => d.date))
    .range([0, tmWidth]);

  const yTm = d3.scaleLinear()
    .domain([0, d3.max(timelineData, d => d.count)])
    .range([tmHeight, 0]);

  tmSvg.append("g").attr("transform", `translate(0,${tmHeight})`).call(d3.axisBottom(xTm).ticks(8));
  tmSvg.append("g").call(d3.axisLeft(yTm));

  const line = d3.line()
    .x(d => xTm(d.date))
    .y(d => yTm(d.count));

  tmSvg.append("path")
    .datum(timelineData)
    .attr("fill", "none")
    .attr("stroke", "#4a90d9")
    .attr("stroke-width", 2.5)
    .attr("d", line);

  tmSvg.selectAll("circle.tm")
    .data(timelineData)
    .join("circle")
    .attr("class", "tm")
    .attr("cx", d => xTm(d.date))
    .attr("cy", d => yTm(d.count))
    .attr("r", 4)
    .attr("fill", "#4a90d9");

  // ── MAPA LEAFLET — CIDADES ─────────────────────────
  const activityByCidade = d3.rollup(activity, v => v.length, d => d.city);

  const cidadeCoordenadas = {
    "Lisboa":        [38.7169, -9.1399],
    "Porto":         [41.1579, -8.6291],
    "Coimbra":       [40.2033, -8.4103],
    "Braga":         [41.5454, -8.4265],
    "Faro":          [37.0194, -7.9304],
    "Évora":         [38.5714, -7.9139],
    "Setúbal":       [38.5243, -8.8926],
    "Viseu":         [40.6566, -7.9122],
    "Aveiro":        [40.6443, -8.6455],
    "Leiria":        [39.7444, -8.8072],
    "Santarém":      [39.2369, -8.6861],
    "Beja":          [38.0154, -7.8637],
    "Viana do Castelo": [41.6932, -8.8341],
    "Vila Real":     [41.3006, -7.7457],
    "Bragança":      [41.8061, -6.7589],
    "Guarda":        [40.5364, -7.2681],
    "Castelo Branco":[39.8220, -7.4908],
    "Portalegre":    [39.2967, -7.4286],
  };

  const cidadeData = Array.from(activityByCidade, ([city, count]) => ({ city, count }));
  const maxCount   = d3.max(cidadeData, d => d.count);

  // Guardar dados para inicializar o mapa quando a tab abrir
  window.cidadeData          = cidadeData;
  window.cidadeCoordenadas   = cidadeCoordenadas;
  window.maxCount            = maxCount;

  window.inicializarMapa = function() {
    const map = L.map("map-chart").setView([39.5, -8.0], 6.5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    window.cidadeData.forEach(d => {
      const coords = window.cidadeCoordenadas[d.city];
      if (!coords) return;

      const radius = 8 + (d.count / window.maxCount) * 30;

      L.circleMarker(coords, {
        radius:      radius,
        fillColor:   "#4a90d9",
        color:       "#fff",
        weight:      2,
        opacity:     1,
        fillOpacity: 0.75
      })
      .addTo(map)
      .bindTooltip(`<strong>${d.city}</strong><br>Atividades: ${d.count}`, {
        permanent:  false,
        direction:  "top"
      });
    });
  };

  // ── CONVITES ───────────────────────────────────────
  const invStatuses = ["accepted", "declined", "pending"];
  const invColors   = { accepted: "#2ecc71", declined: "#e74c3c", pending: "#f39c12" };
  const invLabels   = { accepted: "Aceites", declined: "Recusados", pending: "Pendentes" };

  const invByStatus = d3.rollup(invitation, v => v.length, d => d.status);

  const invData = invStatuses.map(s => ({
    status: s,
    count: invByStatus.get(s) || 0
  }));

  const invMargin = { top: 20, right: 20, bottom: 60, left: 50 };
  const invWidth  = 400 - invMargin.left - invMargin.right;
  const invHeight = 320 - invMargin.top  - invMargin.bottom;

  const invSvg = d3.select("#invites-chart")
    .attr("width",  invWidth  + invMargin.left + invMargin.right)
    .attr("height", invHeight + invMargin.top  + invMargin.bottom)
    .append("g")
    .attr("transform", `translate(${invMargin.left},${invMargin.top})`);

  const xInv = d3.scaleBand()
    .domain(invStatuses)
    .range([0, invWidth])
    .padding(0.3);

  const yInv = d3.scaleLinear()
    .domain([0, d3.max(invData, d => d.count)])
    .range([invHeight, 0]);

  invSvg.append("g").attr("transform", `translate(0,${invHeight})`)
    .call(d3.axisBottom(xInv).tickFormat(d => invLabels[d]));

  invSvg.append("g").call(d3.axisLeft(yInv));

  invSvg.selectAll("rect")
    .data(invData)
    .join("rect")
    .attr("x", d => xInv(d.status))
    .attr("y", d => yInv(d.count))
    .attr("width", xInv.bandwidth())
    .attr("height", d => invHeight - yInv(d.count))
    .attr("fill", d => invColors[d.status]);

  invSvg.selectAll("text.inv-label")
    .data(invData)
    .join("text")
    .attr("class", "inv-label")
    .attr("x", d => xInv(d.status) + xInv.bandwidth() / 2)
    .attr("y", d => yInv(d.count) - 6)
    .attr("text-anchor", "middle")
    .style("font-weight", "bold")
    .text(d => d.count);

  // ── PESQUISA DE UTILIZADOR ─────────────────────────
  window.searchUser = function () {
    const query = document.getElementById("search-input").value.trim().toLowerCase();
    const user  = window.dataset.find(d => d.userId.toLowerCase() === query);

    if (!user) {
      alert("Utilizador não encontrado!");
      return;
    }

    const card = document.getElementById("user-card");
    card.style.display = "block";
    document.getElementById("card-name").textContent     = user.userId;
    document.getElementById("card-rank").textContent     = `#${user.rank} de ${window.dataset.length}`;
    document.getElementById("card-score").textContent    = user.score;
    document.getElementById("card-activity").textContent = user.activityCount;
    document.getElementById("card-inv").textContent      = user.invitationTotal;
    document.getElementById("card-accepted").textContent = user.invitationAccepted;
    document.getElementById("card-matching").textContent = user.matchingCount;
    document.getElementById("card-rec").textContent      = user.recCount;

    const pieData = [
      { label: "Atividades",    value: user.activityCount },
      { label: "Aceites",       value: user.invitationAccepted },
      { label: "Matchings",     value: user.matchingCount },
      { label: "Recomendações", value: user.recCount },
    ];

    const pieColors = ["#4a90d9", "#e67e22", "#2ecc71", "#e74c3c"];

    d3.select("#pie-chart").selectAll("*").remove();

    const r   = 90;
    const pie = d3.pie().value(d => d.value);
    const arc = d3.arc().innerRadius(0).outerRadius(r);

    const pieSvg = d3.select("#pie-chart")
      .attr("width",  300)
      .attr("height", 240)
      .append("g")
      .attr("transform", "translate(110,110)");

    pieSvg.selectAll("path")
      .data(pie(pieData))
      .join("path")
      .attr("d", arc)
      .attr("fill", (d, i) => pieColors[i])
      .attr("stroke", "white")
      .style("stroke-width", "2px");

    const legend = d3.select("#pie-chart").append("g")
      .attr("transform", "translate(215, 60)");

    pieData.forEach((d, i) => {
      legend.append("rect").attr("y", i * 22).attr("width", 13).attr("height", 13).attr("fill", pieColors[i]);
      legend.append("text").attr("x", 17).attr("y", i * 22 + 11).text(`${d.label}: ${d.value}`).style("font-size", "11px");
    });

    card.scrollIntoView({ behavior: "smooth" });
  };

  // ── USERID VIA URL ─────────────────────────────
  const params = new URLSearchParams(window.location.search);
  const userIdFromUrl = params.get("userid");

  if (userIdFromUrl) {
    document.getElementById("search-input").value = userIdFromUrl;
    searchUser();
  }

      document.getElementById("ranking-link").href =
        `index.html?userid=${userIdFromUrl}`;
});