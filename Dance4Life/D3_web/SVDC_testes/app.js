
const dictionary = {
    en:{
        title:'Dance4Life Analytics Dashboard',
        subtitle:'Interactive visual narrative combining activity, invitation, matching and recommendation datasets.',
        introTitle:'Project Goal',
        introText:'This dashboard explores behavioral and engagement patterns across the Dance4Life ecosystem using multiple connected datasets.',
        chart1:'Top Users by Engagement Score',
        chart2:'Invitation Status Distribution',
        chart3:'Activity Timeline',
        chart4:'Activity by City',
        chart5:'Recommendation Types',
        chart6:'Behavior Correlation',
        story:'Key Insights',
        insight1Title:'User Engagement',
        insight1Text:'Highly active users also tend to receive more recommendations and stronger social interactions.',
        insight2Title:'Social Network',
        insight2Text:'Invitation acceptance reveals social cohesion and behavioral consistency between users.',
        insight3Title:'Mobility Patterns',
        insight3Text:'Lisbon, Porto and Coimbra dominate the activity ecosystem.'
    },
    pt:{
        title:'Dashboard Analítico Dance4Life',
        subtitle:'Narrativa visual interativa que combina os datasets de atividade, convites, matching e recomendações.',
        introTitle:'Objetivo do Projeto',
        introText:'Este dashboard explora padrões de comportamento e engagement no ecossistema Dance4Life.',
        chart1:'Top Utilizadores por Score',
        chart2:'Distribuição de Convites',
        chart3:'Linha Temporal de Atividades',
        chart4:'Atividade por Cidade',
        chart5:'Tipos de Recomendações',
        chart6:'Correlação Comportamental',
        story:'Principais Insights',
        insight1Title:'Engagement',
        insight1Text:'Utilizadores mais ativos tendem a gerar mais interações sociais.',
        insight2Title:'Rede Social',
        insight2Text:'Os convites aceites demonstram maior coesão social.',
        insight3Title:'Padrões Urbanos',
        insight3Text:'Lisboa, Porto e Coimbra concentram a maioria da atividade.'
    }
};

function setLanguage(lang){

    const d = dictionary[lang];

    document.getElementById('title').textContent = d.title;
    document.getElementById('subtitle').textContent = d.subtitle;
    document.getElementById('introTitle').textContent = d.introTitle;
    document.getElementById('introText').textContent = d.introText;

    document.getElementById('chart1Title').textContent = d.chart1;
    document.getElementById('chart2Title').textContent = d.chart2;
    document.getElementById('chart3Title').textContent = d.chart3;
    document.getElementById('chart4Title').textContent = d.chart4;
    document.getElementById('chart5Title').textContent = d.chart5;
    document.getElementById('chart6Title').textContent = d.chart6;

    document.getElementById('storyTitle').textContent = d.story;

    document.getElementById('insight1Title').textContent = d.insight1Title;
    document.getElementById('insight1Text').textContent = d.insight1Text;

    document.getElementById('insight2Title').textContent = d.insight2Title;
    document.getElementById('insight2Text').textContent = d.insight2Text;

    document.getElementById('insight3Title').textContent = d.insight3Title;
    document.getElementById('insight3Text').textContent = d.insight3Text;
}

document.getElementById('ptBtn').onclick = () => {
    setLanguage('pt');
    ptBtn.classList.add('active');
    enBtn.classList.remove('active');
};

document.getElementById('enBtn').onclick = () => {
    setLanguage('en');
    enBtn.classList.add('active');
    ptBtn.classList.remove('active');
};

Promise.all([
    d3.csv('dance4life_activity.csv'),
    d3.csv('dance4life_invitation.csv'),
    d3.csv('dance4life_matching.csv'),
    d3.csv('dance4life_movement_recommendation.csv')
]).then(([activity,invitation,matching,recommendation])=>{

    document.getElementById('activitiesTotal').textContent = activity.length;
    document.getElementById('invitesTotal').textContent = invitation.length;
    document.getElementById('matchingsTotal').textContent = matching.length;
    document.getElementById('recommendationsTotal').textContent = recommendation.length;

    const score = {};

    activity.forEach(d=>{
        if(!score[d.userId]) score[d.userId]=0;
        score[d.userId]+=1;
    });

    matching.forEach(d=>{
        if(!score[d.userId]) score[d.userId]=0;
        score[d.userId]+=2;
    });

    recommendation.forEach(d=>{
        if(!score[d.userId]) score[d.userId]=0;
        score[d.userId]+=1;
    });

    const topUsers = Object.entries(score)
        .map(([user,score])=>({user,score}))
        .sort((a,b)=>b.score-a.score)
        .slice(0,10);

    drawBar(topUsers);
    drawPie(invitation);
    drawTimeline(activity);
    drawCity(activity);
    drawRecommendation(recommendation);
    drawScatter(activity,matching);
});

function createSVG(id){
    return d3.select(id);
}

function drawBar(data){

    const svg = createSVG('#barChart');

    const width = 800;
    const height = 400;
    const margin = {top:20,right:20,bottom:90,left:50};

    svg.attr('viewBox',`0 0 ${width} ${height}`);

    const x = d3.scaleBand()
        .domain(data.map(d=>d.user))
        .range([margin.left,width-margin.right])
        .padding(.2);

    const y = d3.scaleLinear()
        .domain([0,d3.max(data,d=>d.score)])
        .range([height-margin.bottom,margin.top]);

    svg.append('g')
        .attr('transform',`translate(0,${height-margin.bottom})`)
        .attr('class','axis')
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('transform','rotate(-35)')
        .style('text-anchor','end');

    svg.append('g')
        .attr('transform',`translate(${margin.left},0)`)
        .attr('class','axis')
        .call(d3.axisLeft(y));

    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x',d=>x(d.user))
        .attr('y',d=>y(d.score))
        .attr('width',x.bandwidth())
        .attr('height',d=>height-margin.bottom-y(d.score))
        .attr('rx',10)
        .attr('fill','#3b82f6');
}

function drawPie(invitation){

    const svg = createSVG('#pieChart');
    const width = 500;
    const height = 400;
    const radius = 120;

    svg.attr('viewBox',`0 0 ${width} ${height}`);

    const counts = d3.rollup(invitation,v=>v.length,d=>d.status);

    const data = Array.from(counts,([status,value])=>({status,value}));

    const pie = d3.pie().value(d=>d.value)(data);

    const arc = d3.arc().innerRadius(50).outerRadius(radius);

    const g = svg.append('g')
        .attr('transform',`translate(${width/2},${height/2})`);

    const colors = d3.scaleOrdinal()
        .domain(data.map(d=>d.status))
        .range(['#22c55e','#f97316','#ef4444']);

    g.selectAll('path')
        .data(pie)
        .enter()
        .append('path')
        .attr('d',arc)
        .attr('fill',d=>colors(d.data.status))
        .attr('stroke','#081120')
        .style('stroke-width','3px');
}

function drawTimeline(activity){

    const svg = createSVG('#lineChart');

    const width = 1000;
    const height = 400;
    const margin = {top:20,right:20,bottom:50,left:50};

    svg.attr('viewBox',`0 0 ${width} ${height}`);

    const parse = d3.timeParse('%Y-%m-%d %H:%M:%S');

    const grouped = d3.rollup(
        activity,
        v=>v.length,
        d=>d.date?.substring(0,7)
    );

    const data = Array.from(grouped,([date,count])=>({
        date:new Date(date + '-01'),
        count
    })).sort((a,b)=>a.date-b.date);

    const x = d3.scaleTime()
        .domain(d3.extent(data,d=>d.date))
        .range([margin.left,width-margin.right]);

    const y = d3.scaleLinear()
        .domain([0,d3.max(data,d=>d.count)])
        .range([height-margin.bottom,margin.top]);

    svg.append('g')
        .attr('transform',`translate(0,${height-margin.bottom})`)
        .attr('class','axis')
        .call(d3.axisBottom(x));

    svg.append('g')
        .attr('transform',`translate(${margin.left},0)`)
        .attr('class','axis')
        .call(d3.axisLeft(y));

    const line = d3.line()
        .x(d=>x(d.date))
        .y(d=>y(d.count));

    svg.append('path')
        .datum(data)
        .attr('fill','none')
        .attr('stroke','#8b5cf6')
        .attr('stroke-width',4)
        .attr('d',line);
}

function drawCity(activity){

    const svg = createSVG('#cityChart');

    const width = 500;
    const height = 400;
    const margin = {top:20,right:20,bottom:60,left:60};

    svg.attr('viewBox',`0 0 ${width} ${height}`);

    const grouped = d3.rollup(activity,v=>v.length,d=>d.city);

    const data = Array.from(grouped,([city,count])=>({city,count}))
        .sort((a,b)=>b.count-a.count)
        .slice(0,8);

    const y = d3.scaleBand()
        .domain(data.map(d=>d.city))
        .range([margin.top,height-margin.bottom])
        .padding(.2);

    const x = d3.scaleLinear()
        .domain([0,d3.max(data,d=>d.count)])
        .range([margin.left,width-margin.right]);

    svg.append('g')
        .attr('transform',`translate(${margin.left},0)`)
        .attr('class','axis')
        .call(d3.axisLeft(y));

    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x',margin.left)
        .attr('y',d=>y(d.city))
        .attr('width',d=>x(d.count)-margin.left)
        .attr('height',y.bandwidth())
        .attr('rx',8)
        .attr('fill','#06b6d4');
}

function drawRecommendation(recommendation){

    const svg = createSVG('#recommendationChart');

    const width = 500;
    const height = 400;

    svg.attr('viewBox',`0 0 ${width} ${height}`);

    const grouped = d3.rollup(recommendation,v=>v.length,d=>d.actionId);

    const data = Array.from(grouped,([name,value])=>({name,value}));

    const radius = d3.scaleSqrt()
        .domain([0,d3.max(data,d=>d.value)])
        .range([30,90]);

    const simulation = d3.forceSimulation(data)
        .force('center',d3.forceCenter(width/2,height/2))
        .force('charge',d3.forceManyBody().strength(10))
        .force('collision',d3.forceCollide().radius(d=>radius(d.value)+4));

    for(let i=0;i<200;i++) simulation.tick();

    const g = svg.append('g');

    g.selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx',d=>d.x)
        .attr('cy',d=>d.y)
        .attr('r',d=>radius(d.value))
        .attr('fill','#ec4899');

    g.selectAll('text')
        .data(data)
        .enter()
        .append('text')
        .attr('x',d=>d.x)
        .attr('y',d=>d.y)
        .attr('text-anchor','middle')
        .attr('fill','white')
        .style('font-size','12px')
        .text(d=>d.name);
}

function drawScatter(activity,matching){

    const svg = createSVG('#scatterChart');

    const width = 1000;
    const height = 420;
    const margin = {top:20,right:20,bottom:60,left:60};

    svg.attr('viewBox',`0 0 ${width} ${height}`);

    const activityCount = d3.rollup(activity,v=>v.length,d=>d.userId);
    const matchingCount = d3.rollup(matching,v=>v.length,d=>d.userId);

    const users = [...new Set([...activityCount.keys(),...matchingCount.keys()])];

    const data = users.map(user=>({
        user,
        activity:activityCount.get(user)||0,
        matching:matchingCount.get(user)||0
    }));

    const x = d3.scaleLinear()
        .domain([0,d3.max(data,d=>d.activity)])
        .range([margin.left,width-margin.right]);

    const y = d3.scaleLinear()
        .domain([0,d3.max(data,d=>d.matching)])
        .range([height-margin.bottom,margin.top]);

    svg.append('g')
        .attr('transform',`translate(0,${height-margin.bottom})`)
        .attr('class','axis')
        .call(d3.axisBottom(x));

    svg.append('g')
        .attr('transform',`translate(${margin.left},0)`)
        .attr('class','axis')
        .call(d3.axisLeft(y));

    svg.selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx',d=>x(d.activity))
        .attr('cy',d=>y(d.matching))
        .attr('r',6)
        .attr('fill','#8b5cf6')
        .attr('opacity',.7);
}
