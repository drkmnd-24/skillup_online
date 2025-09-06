/* =========================================================================
   PRONOVE TAI – DASHBOARD.JS
   ========================================================================= */

/* -------------------------------------------------- */
/*  0 · Basic options reused by tiny spark-area charts */
/* -------------------------------------------------- */
const tinyAreaOptions = {
    chart: {height: 80, type: "area", toolbar: {show: false}},
    stroke: {width: 2},
    grid: {show: false},
    dataLabels: {enabled: false},
    xaxis: {
        type: "datetime",
        categories: [
            "2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z",
            "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z",
            "2018-09-19T06:30:00.000Z", "2018-09-19T07:30:00.000Z", "2018-09-19T08:30:00.000Z",
            "2018-09-19T09:30:00.000Z", "2018-09-19T10:30:00.000Z", "2018-09-19T11:30:00.000Z"
        ],
        axisBorder: {show: false},
        axisTicks: {show: false},
        labels: {show: false}
    },
    yaxis: {labels: {show: false}},
    tooltip: {x: {format: "dd/MM/yy HH:mm"}}
};

/* -------------------------------------------------- */
/*  1 · OD-Form bar chart – starts empty              */
/* -------------------------------------------------- */
const optionsProfileVisit = {
    chart: {type: "bar", height: 300},
    colors: ["#435ebe"],
    dataLabels: {enabled: false},
    xaxis: {categories: ["Active", "Done Deal", "Inactive"]},
    series: [{name: "OD Forms", data: [0, 0, 0]}]
};

/* -------------------------------------------------- */
/*  2 · Visitors donut chart (unchanged)              */
/* -------------------------------------------------- */
const optionsVisitorsProfile = {
    series: [70, 30],
    labels: ["Male", "Female"],
    colors: ["#435ebe", "#55c6e8"],
    chart: {type: "donut", width: "100%", height: 350},
    legend: {position: "bottom"},
    plotOptions: {pie: {donut: {size: "30%"}}}
};

/* -------------------------------------------------- */
/*  3 · three tiny area charts (Europe, America, Indo)*/
/* -------------------------------------------------- */
const optionsEurope = {
    ...tinyAreaOptions,
    colors: ["#5350e9"],
    series: [{data: [310, 800, 600, 430, 540, 340, 605, 805, 430, 540, 340, 605]}]
};
const optionsAmerica = {
    ...tinyAreaOptions,
    colors: ["#008b75"],
    series: [{data: [410, 700, 500, 330, 640, 440, 705, 605, 330, 640, 440, 705]}]
};
const optionsIndonesia = {
    ...tinyAreaOptions,
    colors: ["#dc3545"],
    series: [{data: [510, 900, 700, 530, 740, 540, 805, 905, 530, 740, 540, 805]}]
};

/* -------------------------------------------------- */
/*  4 · Create every chart                            */
/* -------------------------------------------------- */
const chartProfileVisit = new ApexCharts(document.querySelector("#chart-profile-visit"), optionsProfileVisit);
const chartVisitors = new ApexCharts(document.querySelector("#chart-visitors-profile"), optionsVisitorsProfile);
const chartEurope = new ApexCharts(document.querySelector("#chart-europe"), optionsEurope);
const chartAmerica = new ApexCharts(document.querySelector("#chart-america"), optionsAmerica);
const chartIndonesia = new ApexCharts(document.querySelector("#chart-indonesia"), optionsIndonesia);

chartProfileVisit.render();
chartVisitors.render();
chartEurope.render();
chartAmerica.render();
chartIndonesia.render();

/* -------------------------------------------------- */
/*  5 · Fetch live OD-Form counts & update bar chart  */
/* -------------------------------------------------- */
(function updateODFormChart() {
    const token = localStorage.getItem("access");
    if (!token) return;

    fetch("/api/odforms/?page_size=1000", {
        headers: {Authorization: `Bearer ${token}`}
    })
        .then(r => r.status === 401 ? (localStorage.clear(), location.href = "/") : r.json())
        .then(data => {
            if (!data || !data.results) return;
            const counts = {active: 0, done_deal: 0, inactive: 0};
            data.results.forEach(o => {
                if (counts[o.status] !== undefined) counts[o.status]++;
            });

            chartProfileVisit.updateSeries([{
                name: "OD Forms",
                data: [counts.active, counts.done_deal, counts.inactive]
            }]);
        })
        .catch(console.error);
})();
