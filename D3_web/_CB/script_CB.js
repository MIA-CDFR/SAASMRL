const svg = d3.select("svg");

const width = 900;
const height = 600;

const margin = {
  top: 40,
  right: 40,
  bottom: 60,
  left: 70
};

d3.csv("../dance4life_activity.csv").then(data => {

  data.forEach(d => {
    d.hr = +d.hr;
    d.ritmo = +d.ritmo;
  });

  // Escalas
  const x = d3.scaleLinear()
    .domain(d3.extent(data, d => d.hr))
    .range([margin.left, width - margin.right]);

  const y = d3.scaleLinear()
    .domain(d3.extent(data, d => d.ritmo))
    .range([height - margin.bottom, margin.top]);

  // Eixo X
  svg.append("g")
    .attr("transform", `translate(0, ${height - margin.bottom})`)
    .call(d3.axisBottom(x));

  // Eixo Y
  svg.append("g")
    .attr("transform", `translate(${margin.left}, 0)`)
    .call(d3.axisLeft(y));

  // Pontos
  svg.selectAll(".dot")
    .data(data)
    .enter()
    .append("circle")
    .attr("class", "dot")
    .attr("cx", d => x(d.hr))
    .attr("cy", d => y(d.ritmo))
    .attr("r", 5);

  // Título
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", 25)
    .attr("text-anchor", "middle")
    .style("font-size", "20px")
    .text("Relação entre HR e Ritmo");

  // Label X
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .attr("text-anchor", "middle")
    .text("Heart Rate (HR)");

  // Label Y
  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", 20)
    .attr("text-anchor", "middle")
    .text("Ritmo");

});