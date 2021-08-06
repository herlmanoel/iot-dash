
function createElementChart(idElement) {
  let divNova = document.createElement("div");
  divNova.setAttribute("id", idElement);
  let main = document.getElementById("main-cards");
  main.appendChild(divNova);
}

function createGraph(fieldNumber, title, nameLine, prev) {
  let idElement;
  let URL;
  if (prev) {
    URL = `http://127.0.0.1:8000/getJson/?id=${fieldNumber}&prev=1`;
    idElement = `chart_prev_${fieldNumber}`;
  } else {
    URL = `http://127.0.0.1:8000/getJson/?id=${fieldNumber}`;
    idElement = `chart_${fieldNumber}`;
  }
  createElementChart(idElement);
  let dataTable = [];
  let dataJson = [];
  let dataTableMedia = [];
  let media = 0;

  fetch(URL)
    .then(function (response) {
      return response.json();
    })
    .then(function (responde) {
      let soma = 0;
      let cont = 1;
      responde.forEach(function (item, index) {
        cont++;
        let xDate = new Date(item.ds);
        dataTable.push([xDate, item.y]);
        dataJson.push(xDate);
        let i = parseFloat(item.y);
        soma = i + soma;
      });

      media = soma / cont;
      dataJson.forEach(function (item) {
        dataTableMedia.push([item, media]);
      });
    });

  var options = {
    series: [{
      name: nameLine,
      data: dataTable
    },
    {
      name: "Média",
      data: dataTableMedia,
    }],
    chart: {
      height: 350,
      type: 'line',
      stacked: false,
      zoom: {
        type: 'x',
        enabled: true,
        autoScaleYaxis: true
      },
      toolbar: {
        autoSelected: 'zoom'
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'straight'
    },
    title: {
      text: title,
      align: 'left'
    },
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
        opacity: 0.5
      },
    },
    dataLabels: {
      enabled: false
    },
    markers: {
      size: 0,
      style: 'hollow',
    },
    xaxis: {
      type: 'datetime',
      tickAmount: 6,
    },
    yaxis: {
      labels: {
        formatter: function (value) {
          let v = parseFloat(value)
          return v.toFixed(2);
        }
      },
    },
  };
  let chart = new ApexCharts(document.querySelector(`#${idElement}`), options);
  chart.render();
}

function renderizarGraficos() {
  createGraph(`1`, 'Outdoor Temperature (DS18B20)', 'Temperature [C]', false);
  createGraph(`2`, 'Temperature (Si7021)', 'Temperature [C]', false);
  createGraph(`3`, 'Air Pressure (BMP280)', 'Pressure [mmHg]', false);
  createGraph(`4`, 'Humidity (Si7021)', 'Humidity [%]', false);
  createGraph(`1`, 'Prevision - Outdoor Temperature (DS18B20)', 'Temperature [C]', true);
  createGraph(`2`, 'Prevision - Temperature (Si7021)', 'Temperature [C]', true);
}

// createElementChart('chart112');
function atualizarDados() {
  console.log("Chamou!");
  fetch(`http://127.0.0.1:8000/getData`)
    .then(function (response) {
      console.log(response.json());
      renderizarGraficos();
    }).catch(function (err) {
      console.log(err)
    });
}
window.onload = function () {
  atualizarDados();
  renderizarGraficos();

  let timeOut = setInterval(atualizarDados, 300000);
  
}