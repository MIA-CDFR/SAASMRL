const svg = d3.select("svg");

const width = 1000;
const height = 600;

const margin = {
  top: 50,
  right: 50,
  bottom: 70,
  left: 70
};

d3.csv("../dance4life_activity.csv").then(data => {

  // Converter dados
  data.forEach(d => {
    d.ritmo = +d.ritmo;

    // Ajusta ao nome REAL da tua coluna de data
    d.date = new Date(d.date);
  });

  // Remover valores inválidos
  data = data.filter(d => d.date && !isNaN(d.ritmo));

  // Escala X (tempo)
  const x = d3.scaleTime()
    .domain(d3.extent(data, d => d.date))
    .range([margin.left, width - margin.right]);

  // Escala Y (ritmo)
  const y = d3.scaleLinear()
    .domain([
      d3.min(data, d => d.ritmo) - 5,
      d3.max(data, d => d.ritmo) + 5
    ])
    .range([height - margin.bottom, margin.top]);

  // Eixo X
  svg.append("g")
    .attr("transform", `translate(0, ${height - margin.bottom})`)
    .call(
      d3.axisBottom(x)
        .ticks(d3.timeMonth.every(1))
        .tickFormat(d3.timeFormat("%b %Y"))
    )
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end");

  // Eixo Y
  svg.append("g")
    .attr("transform", `translate(${margin.left}, 0)`)
    .call(d3.axisLeft(y));

  // Linha
  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.ritmo));

  svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 3)
    .attr("d", line);

  // Título
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", 30)
    .attr("text-anchor", "middle")
    .style("font-size", "22px")
    .style("font-weight", "bold")
    .text("Evolução do Ritmo ao Longo do Tempo");

  // Label X
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .attr("text-anchor", "middle")
    .text("Tempo");

  // Label Y
  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", 20)
    .attr("text-anchor", "middle")
    .text("Ritmo");

}).catch(error => {
  console.error("Erro ao carregar CSV:", error);
});