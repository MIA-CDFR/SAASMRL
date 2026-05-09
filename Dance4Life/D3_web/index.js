import { db } from "./firebase-config.js";

import {
    collection,
    query,
    where,
    getDocs
} from "https://www.gstatic.com/firebasejs/12.12.1/firebase-firestore.js";

const params = new URLSearchParams(window.location.search);

const userId = params.get("userid");

document.getElementById("dashboard-link").href =
    `dashboard.html?userid=${userId}`;
// ─────────────────────────────────────
// DATE PARSER
// DD-MM-YYYY HH:mm:ss
// ─────────────────────────────────────

function parseDate(dateStr) {

  if (!dateStr)
    return new Date(0);

  const [datePart, timePart] =
    String(dateStr).split(" ");

  const [day, month, year] =
    datePart.split("-");

  return new Date(
    Number(year),
    Number(month) - 1,
    Number(day),
    ...(timePart || "00:00:00")
      .split(":")
      .map(Number)
  );
}

async function loadUserData() {

    if (!userId) {
        alert("userid não encontrado");
        return;
    }

    // ── LOAD COLLECTIONS ─────────────────────

    const [
        activitySnap,
        invitationSnap,
        matchingSnap,
        recSnap
    ] = await Promise.all([

        getDocs(collection(db, "dance4life_activity")),

        getDocs(collection(db, "dance4life_invitation")),

        getDocs(collection(db, "dance4life_matching")),

        getDocs(collection(db, "dance4life_movement_recommendation"))
    ]);


    // ── CONVERT DOCS ─────────────────────────

    const activity = activitySnap.docs.map(d => d.data());

    const invitation = invitationSnap.docs.map(d => d.data());

    const matching = matchingSnap.docs.map(d => d.data());

    const recommendation = recSnap.docs.map(d => d.data());

    // ── AGGREGATION ──────────────────────────

    const users = {};

    function ensureUser(id) {

        if (!users[id]) {

            users[id] = {
                userId: id,
                activityCount: 0,
                invitationTotal: 0,
                invitationAccepted: 0,
                matchingCount: 0,
                recCount: 0,
                score: 0
            };
        }

        return users[id];
    }

    // ── ACTIVITY ─────────────────────────────

    activity.forEach(d => {

        const u = ensureUser(d.userId);

        u.activityCount++;
    });

    // ── INVITATIONS ──────────────────────────

    invitation.forEach(d => {

        const u = ensureUser(d.userId);

        u.invitationTotal++;

        if (d.status === true || d.status === "accepted") {
            u.invitationAccepted++;
        }
    });

    // ── MATCHINGS ────────────────────────────

    matching.forEach(d => {

        const u = ensureUser(d.userId);

        u.matchingCount++;
    });

    // ── RECOMMENDATIONS ──────────────────────

    recommendation.forEach(d => {

        const u = ensureUser(d.userId);

        u.recCount++;
    });

    // ── SCORE ────────────────────────────────

    const dataset = Object.values(users);

    dataset.forEach(u => {

        u.score =
            u.activityCount
            + u.invitationAccepted
            + u.matchingCount
            + u.recCount;
    });

    // ── SORT + RANK ──────────────────────────

    dataset.sort((a, b) => b.score - a.score);

    dataset.forEach((u, index) => {
        u.rank = index + 1;
    });

    // ── FIND CURRENT USER ────────────────────

    const user = dataset.find(u => u.userId === userId);

    if (!user) {
        alert("Utilizador não encontrado");
        return;
    }

    // ── PAGE TITLE ───────────────────────────

    document.title = `Dance4Life User ${user.userId} Ranking`;

    // ── UI ───────────────────────────────────

    document.getElementById("card-title").textContent =
        `Ranking`;

    document.getElementById("card-name").textContent =
        `User ${userId}`;

    document.getElementById("card-rank").textContent =
        `#${user.rank} de ${dataset.length}`;

    document.getElementById("card-score").textContent =
        user.score;

    document.getElementById("card-activity").textContent =
        user.activityCount;

    document.getElementById("card-inv").textContent =
        user.invitationTotal;

    document.getElementById("card-accepted").textContent =
        user.invitationAccepted;

    document.getElementById("card-matching").textContent =
        user.matchingCount;

    document.getElementById("card-rec").textContent =
        user.recCount;

    // document.getElementById("dashboard-link").href =
    //     `dashboard.html?userid=${userId}`;

    drawPieChart(user);
}

/*async function loadUserData() {

  if (!userId) {
    alert("userid não encontrado");
    return;
  }

  // ── ACTIVITY ─────────────────────────────

  const activityQuery = query(
    collection(db, "dance4life_activity"),
    where("userId", "==", userId)
  );

  const activitySnap = await getDocs(activityQuery);

  const activityCount = activitySnap.size;

  // ── INVITATIONS ──────────────────────────

  const invitationQuery = query(
    collection(db, "dance4life_invitation"),
    where("userId", "==", userId)
  );

  const invitationSnap = await getDocs(invitationQuery);

  const invitationTotal = invitationSnap.size;

  const invitationAccepted = invitationSnap.docs.filter(
    d => d.data().status === true
  ).length;

  // ── MATCHINGS ────────────────────────────

  const matchingQuery = query(
    collection(db, "dance4life_matching"),
    where("userId", "==", userId)
  );

  const matchingSnap = await getDocs(matchingQuery);

  const matchingCount = matchingSnap.size;

  // ── RECOMMENDATIONS ──────────────────────

  const recQuery = query(
    collection(db, "dance4life_movement_recommendation"),
    where("userId", "==", userId)
  );

  const recSnap = await getDocs(recQuery);

  const recCount = recSnap.size;

  // ── SCORE ────────────────────────────────

  const score =
      activityCount
    + invitationAccepted
    + matchingCount
    + recCount;

  // ── UI ───────────────────────────────────

  document.getElementById("card-title").textContent = `Dance4LifeUser Ranking`;

  document.getElementById("card-name").textContent = `User ${userId}`;

  document.getElementById("card-rank").textContent =
    "-";

  document.getElementById("card-score").textContent =
    score;

  document.getElementById("card-activity").textContent =
    activityCount;

  document.getElementById("card-inv").textContent =
    invitationTotal;

  document.getElementById("card-accepted").textContent =
    invitationAccepted;

  document.getElementById("card-matching").textContent =
    matchingCount;

  document.getElementById("card-rec").textContent =
    recCount;

  drawPieChart({
    activityCount,
    invitationAccepted,
    matchingCount,
    recCount
  });
}*/

/*
function drawPieChart(user) {

  const pieData = [
    { label: "Atividades", value: user.activityCount },
    { label: "Aceites", value: user.invitationAccepted },
    { label: "Matchings", value: user.matchingCount },
    { label: "Recomendações", value: user.recCount }
  ];

  const pieColors = [
    "#4a90d9",
    "#e67e22",
    "#2ecc71",
    "#e74c3c"
  ];

  d3.select("#pie-chart").selectAll("*").remove();

  const r = 90;

  const pie = d3.pie().value(d => d.value);

  const arc = d3.arc()
    .innerRadius(0)
    .outerRadius(r);

  const pieSvg = d3.select("#pie-chart")
    .attr("width", 300)
    .attr("height", 240)
    .append("g")
    .attr("transform", "translate(110,110)");

  pieSvg.selectAll("path")
    .data(pie(pieData))
    .join("path")
    .attr("d", arc)
    .attr("fill", (d, i) => pieColors[i]);

}*/

function drawPieChart(user) {

    const pieData = [
        { label: "Atividades", value: user.activityCount },
        { label: "Aceites", value: user.invitationAccepted },
        { label: "Matchings", value: user.matchingCount },
        { label: "Recomendações", value: user.recCount }
    ];

    const pieColors = [
        "#4a90d9",
        "#e67e22",
        "#2ecc71",
        "#e74c3c"
    ];

    d3.select("#pie-chart").selectAll("*").remove();

    const r = 90;

    const pie = d3.pie()
        .value(d => d.value);

    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(r);

    const pieSvg = d3.select("#pie-chart")
        .attr("width", 420)
        .attr("height", 260)
        .append("g")
        .attr("transform", "translate(120,130)");

    // ── PIE ───────────────────────────────

    pieSvg.selectAll("path")
        .data(pie(pieData))
        .join("path")
        .attr("d", arc)
        .attr("fill", (d, i) => pieColors[i])
        .attr("stroke", "white")
        .style("stroke-width", "2px");

    // ── LEGEND ────────────────────────────

    const legend = d3.select("#pie-chart")
        .append("g")
        .attr("transform", "translate(250,70)");

    pieData.forEach((d, i) => {

        legend.append("rect")
            .attr("x", 0)
            .attr("y", i * 24)
            .attr("width", 14)
            .attr("height", 14)
            .attr("fill", pieColors[i]);

        legend.append("text")
            .attr("x", 22)
            .attr("y", i * 24 + 12)
            .style("font-size", "12px")
            .text(`${d.label}: ${d.value}`);
    });
}

async function buildNetwork() {

    const snap = await getDocs(
        collection(db, "dance4life_matching")
    );

    const docs = snap.docs.map(d => d.data());

    // ── USER EVENTS ─────────────────────────

    const currentUserEvents = docs.filter(
        d => d.userId === userId
    );

    const connections = {};

    currentUserEvents.forEach(event => {

        // ignorar eventos sem data
        if (!event.date)
            return;

        const eventDay = String(event.date).substring(0, 10);

        docs.forEach(other => {

            // ignorar utilizadores inválidos
            if (!other.userId)
                return;

            // ignorar docs inválidos
            if (!other.date)
                return;

            // ignorar o próprio utilizador
            if (other.userId === userId)
                return;

            const otherDay = String(other.date).substring(0, 10);

            const sameDay =
                otherDay === eventDay;

            const sameCity =
                other.city === event.city;

            const sameCluster =
                other.cluster === event.cluster;

            if (sameDay && sameCity && sameCluster) {

                if (!connections[other.userId]) {

                    connections[other.userId] = {
                        count: 0,
                        cluster: other.cluster
                    };
                }

                connections[other.userId].count++;
            }
        });
    });
    // ── NODES ───────────────────────────────

    const nodes = [
        {
            id: userId,
            group: "CURRENT"
        }
    ];

    Object.entries(connections).forEach(([id, data]) => {

        nodes.push({
            id,
            group: data.cluster
        });
    });

    // ── LINKS ───────────────────────────────

    const links = [];

    Object.entries(connections).forEach(([id, data]) => {

        links.push({
            source: userId,
            target: id,
            value: data.count
        });
    });

    renderGraph({ nodes, links });
}

function renderGraph(graph) {

    // const width = 1000;
    // const height = 700;

    const width =
    document.getElementById("graph")
        .clientWidth;

    const height = 650;

    // const svg = d3.select("#graph")
    //     .attr("width", width)
    //     .attr("height", height);
const svg = d3.select("#graph")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet")
    .style("width", "100%")
    .style("height", `${height}px`);

    const g = svg.append("g");

    // svg.call(
    //     d3.zoom()
    //         .scaleExtent([0.5, 5])
    //         .on("zoom", (event) => {
    //             g.attr("transform", event.transform);
    //         })
    // );

    const simulation = d3.forceSimulation(graph.nodes)
        .force(
            "link",
            d3.forceLink(graph.links)
                .id(d => d.id)
                .distance(90)
        )
        .force(
            "charge",
            d3.forceManyBody().strength(-80)
        )
        .force(
            "center",
            d3.forceCenter(width / 2, height / 2)
        );

    // ── LINKS ───────────────────────────────

    //   const link = svg.append("g")
    //     .selectAll("line")
    //     .data(graph.links)
    //     .join("line")
    //     .attr("stroke", "#999")
    //     .attr("stroke-width", d => 1 + d.value);
    const link = g.append("g")
        .attr("stroke", "#bbb")
        .attr("stroke-opacity", 0.25)
        .selectAll("line")
        .data(graph.links)
        .join("line")
        .attr("stroke", "#999")
        .attr("stroke-width", d =>
            Math.min(2, 0.5 + d.value * 0.15)
        );
    // ── NODES ───────────────────────────────

    const color = d3.scaleOrdinal()
        .domain(["CURRENT", "Iniciante", "Moderado", "Avançado"])
        .range([
            "#e74c3c",
            "#3498db",
            "#f39c12",
            "#2ecc71"
        ]);

    //   const node = g.append("g")
    //     .selectAll("circle")
    //     .data(graph.nodes)
    //     .join("circle")
    //     //.attr("r", d => d.group === "CURRENT" ? 20 : 12)
    //     .attr("r", d => d.group === "CURRENT" ? 18 : 7)
    //     .attr("fill", d => color(d.group))
    //     .call(drag(simulation));
    const node = g.append("g")
        .selectAll("g")
        .data(graph.nodes)
        .join("g")
        .call(drag(simulation));

    // node
    //     .filter(d => d.group !== "CURRENT")
    //     .append("circle")
    //     .attr("r", 7)
    //     .attr("fill", d => color(d.group));

    // node
    //     .filter(d => d.group === "CURRENT")
    //     .append("image")
    //     .attr("href", "./img/dance4life_icon.png")
    //     .attr("width", 48)
    //     .attr("height", 48)
    //     .attr("x", -24)
    //     .attr("y", -24);

// ─────────────────────────────
// RANDOM AVATARS
// ─────────────────────────────

const avatars = [
    "./img/avatar_man.png",
    "./img/avatar_woman.png"
];

// utilizador atual
node
    .filter(d => d.group === "CURRENT")
    .append("image")
    .attr("href", "./img/dance4life_icon.png")
    .attr("width", 64)
    .attr("height", 64)
    .attr("x", -32)
    .attr("y", -32);

// restantes utilizadores
node
    .filter(d => d.group !== "CURRENT")
    .append("image")
    .attr("href", d => {

        // avatar fixo baseado no userid
        const hash =
            d.id
                .split("")
                .reduce((a, c) => a + c.charCodeAt(0), 0);

        return avatars[
            hash % avatars.length
        ];
    })
    .attr("width", 64)
    .attr("height", 64)
    .attr("x", -32)
    .attr("y", -32)
    .style("filter", `
        drop-shadow(0 0 6px rgba(255,255,255,.5))
    `);
    // ── LABELS ──────────────────────────────

    const label = g.append("g")
        .selectAll("text")
        .data(graph.nodes)
        .join("text")
        .text(d => d.id)
        .style("font-size", "10px")
        .style("font-family", "sans-serif")
        .style("pointer-events", "none");
    //.style("font-size", "12px");

    // ── TOOLTIP ─────────────────────────────

    node.append("title")
        .text(d => `${d.id}`);

    // ── TICK ────────────────────────────────

    simulation.on("tick", () => {

        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        // node
        //   .attr("cx", d => d.x)
        //   .attr("cy", d => d.y);

        node
            .attr("transform", d =>
                `translate(${d.x},${d.y})`
            );

        label
            .attr("x", d => d.x + 10)
            .attr("y", d => d.y + 4);
    });
}

function drag(simulation) {

    function dragstarted(event) {

        if (!event.active)
            simulation.alphaTarget(0.3).restart();

        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {

        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {

        if (!event.active)
            simulation.alphaTarget(0);

        event.subject.fx = null;
        event.subject.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
}

async function loadLatestActivityMetrics() {

    if (!userId)
        return;

    // ─────────────────────────────────────
    // ACTIVITY
    // ─────────────────────────────────────

    const activityQuery = query(
        collection(db, "dance4life_activity"),
        where("userId", "==", userId)
    );


    const activitySnap =
        await getDocs(activityQuery);


    if (activitySnap.empty)
        return;

//     const activities =
//         activitySnap.docs.map(d => d.data());

//     activities.sort((a, b) =>
//         new Date(b.date) - parseDate(a.date)
//     );

//     const latestActivity =
//         activities[0];

//     // ─────────────────────────────────────
//     // LAST ACTIVITY DATE
//     // ─────────────────────────────────────

//     const lastActivityDate =
//         latestActivity.date || "-";

//     document.getElementById(
//         "last-activity-date"
//     ).textContent =
//         `Última atividade • ${lastActivityDate}`;
// console.log(
//   activities.map(a => a.date)
// );
const activities =
  activitySnap.docs
    .map(d => d.data())
    .filter(a => a.date);

activities.sort((a, b) =>
  parseDate(b.date) - parseDate(a.date)
);

console.log(
  "Todas datas ordenadas:",
  activities.map(a => a.date)
);

const latestActivity =
  activities[0];

    // ─────────────────────────────────────
    // LAST ACTIVITY DATE
    // ─────────────────────────────────────

    const lastActivityDate =
        latestActivity.date || "-";

    document.getElementById(
        "last-activity-date"
    ).textContent =
        `Última atividade • ${lastActivityDate}`;
    // ─────────────────────────────────────
    // RECOMMENDATION
    // ─────────────────────────────────────

    const recQuery = query(
        collection(db, "dance4life_movement_recommendation"),
        where("userId", "==", userId)
    );

    const recSnap =
        await getDocs(recQuery);

    let latestRecommendation = null;

    if (!recSnap.empty) {

const recs =
  recSnap.docs
    .map(d => d.data())
    .filter(r => r.date);

recs.sort((a, b) =>
  parseDate(b.date) - parseDate(a.date)
);

        latestRecommendation =
            recs[0];
    }

    // ─────────────────────────────────────
    // MATCHING
    // ─────────────────────────────────────

    const matchingQuery = query(
        collection(db, "dance4life_matching"),
        where("userId", "==", userId)
    );

    const matchingSnap =
        await getDocs(matchingQuery);

    let latestMatching = null;

    if (!matchingSnap.empty) {

const matchings =
  matchingSnap.docs
    .map(d => d.data())
    .filter(m => m.date);

matchings.sort((a, b) =>
  parseDate(b.date) - parseDate(a.date)
);

        latestMatching =
            matchings[0];
    }

    // ─────────────────────────────────────
    // VALUES
    // ─────────────────────────────────────

    const hr =
        Number(latestActivity.hr || 0);

    const ritmo =
        Number(latestActivity.ritmo || 0);

    const city =
        latestActivity.city || "-";

    const temp =
        latestActivity.weather_temperature || "-";

    const level =
        latestRecommendation?.title || "-";

    const wellbeing =
        latestMatching?.cluster || "-";

    // ─────────────────────────────────────
    // UI
    // ─────────────────────────────────────

    document.getElementById("activity-hr")
        .textContent = Math.round(hr);

    document.getElementById("activity-ritmo")
        .textContent = ritmo.toFixed(1);

    document.getElementById("activity-level")
        .textContent = level;

    document.getElementById("activity-wellbeing")
        .textContent = wellbeing;

    document.getElementById("activity-city")
        .textContent = city;

    document.getElementById("activity-temp")
        .textContent = `${temp}°`;

    // ─────────────────────────────────────
    // CIRCLE ANIMATION
    // ─────────────────────────────────────

    const circle =
        document.querySelector(".activity-circle");

    const deg =
        (Math.min(hr, 120) / 120) * 360;

    circle.style.background =
        `conic-gradient(
      #8b5cf6 0deg,
      #06b6d4 ${deg}deg,
      rgba(255,255,255,.25) ${deg}deg
    )`;

    // ─────────────────────────────────────
    // MAP
    // ─────────────────────────────────────

    const lat =
        Number(latestActivity.latitude);

    const lng =
        Number(latestActivity.longitude);

    if (!isNaN(lat) && !isNaN(lng)) {

        // evitar múltiplos mapas
        if (window.userMap) {
            window.userMap.remove();
        }

        const map = L.map("user-map", {
            zoomControl: false
        }).setView([lat, lng], 13);

        window.userMap = map;

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution:
                    "© OpenStreetMap"
            }
        ).addTo(map);

        // ── CUSTOM MARKER ─────────────────

        const markerHtml = `
    <div class="user-marker"></div>
  `;

        const icon = L.divIcon({
            className: "",
            html: markerHtml,
            iconSize: [28, 28]
        });

        L.marker([lat, lng], { icon })
            .addTo(map)
            .bindPopup(`
      <strong>${city}</strong><br>
      ❤️ HR: ${hr} bpm<br>
        💃 Ritmo: ${ritmo.toFixed(1)}<br>
        ✨ Plano: ${level}<br>
        ❤️ Grupo: ${wellbeing}<br>
        📍 CIDADE: ${city}<br>
         🌡️ ${temp}°
    `)
            .openPopup();
    }
}

// ─────────────────────────────────────
// AUTO REFRESH
// ─────────────────────────────────────

function startAutoRefresh() {

    console.log("Auto refresh iniciado");

    setInterval(async () => {

        console.log("Refreshing data...");

        try {

            // atualizar dados utilizador
            await loadUserData();

            // atualizar métricas
            await loadLatestActivityMetrics();

            // atualizar network graph
            d3.select("#graph").selectAll("*").remove();

            await buildNetwork();

        } catch (err) {

            console.error(
                "Erro no refresh:",
                err
            );
        }

    }, 10000); // 10 segundos
}

loadUserData();
buildNetwork();
loadLatestActivityMetrics();

startAutoRefresh();