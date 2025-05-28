import tempfile
import webbrowser

labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai']

cenarios = {
    "D1": {
        "dados1": [10, 20, 15, 30, 25],
        "dados2": [5, 15, 10, 20, 30],
        "dados3a": [12, 22, 18, 28, 24],
        "dados3b": [15, 25, 20, 30, 27]
    },
    "D5": {
        "dados1": [20, 30, 25, 35, 40],
        "dados2": [10, 25, 15, 35, 45],
        "dados3a": [22, 32, 28, 38, 34],
        "dados3b": [25, 35, 30, 40, 37]
    },
    "D10": {
        "dados1": [30, 40, 35, 45, 50],
        "dados2": [20, 35, 25, 40, 50],
        "dados3a": [32, 42, 38, 48, 44],
        "dados3b": [35, 45, 40, 50, 47]
    }
}

html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Dashboard comparativo Fase 3</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
    }}
    h1 {{
      text-align: center;
      font-size: 28px;
      margin-top: 0;
    }}
    .botoes {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: center;
    }}
    .graficos {{
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      justify-content: center;
      width: 100%;
    }}
    .grafico-container {{
      width: 30%;
      min-width: 300px;
      background: #f9f9f9;
      padding: 10px;
      border-radius: 10px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
      cursor: pointer;
      position: relative;
      text-align: center;
    }}
    .expandido {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 1000;
      background: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      box-shadow: none;
      box-sizing: border-box;
      overflow: auto;
    }}
    .expandido canvas {{
      height: 80vh !important;
    }}
    canvas {{
      width: 100% !important;
      height: 300px !important;
    }}
    button {{
      padding: 10px 20px;
      font-size: 16px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }}
    button:hover {{
      background-color: #45a049;
    }}
    .btn-voltar {{
      position: absolute;
      top: 15px;
      right: 15px;
      background-color: #d9534f;
      z-index: 1001;
    }}
  </style>
</head>
<body>

  <h1>Dashboard comparativo Fase 3</h1>

  <div class="botoes">
    <button onclick="atualizarGraficos('D1')">D1</button>
    <button onclick="atualizarGraficos('D5')">D5</button>
    <button onclick="atualizarGraficos('D10')">D10</button>
    <button onclick="baixarHTML()">Salvar como HTML</button>
  </div>

  <div class="graficos">
    <div class="grafico-container" onclick="expandirGrafico(this)">
      <button class="btn-voltar" style="display:none;" onclick="voltar(event)">Voltar</button>
      <canvas id="grafico1"></canvas>
      <p>Mensagens temporizadas</p>
    </div>
    <div class="grafico-container" onclick="expandirGrafico(this)">
      <button class="btn-voltar" style="display:none;" onclick="voltar(event)">Voltar</button>
      <canvas id="grafico2"></canvas>
      <p>Ignição ligada</p>
    </div>
    <div class="grafico-container" onclick="expandirGrafico(this)">
      <button class="btn-voltar" style="display:none;" onclick="voltar(event)">Voltar</button>
      <canvas id="grafico3"></canvas>
      <p>Ignição desligada</p>
    </div>
  </div>

  <script>
    const labels = ["Jan", "Fev", "Mar", "Abr", "Mai"];

    const cenarios = {{
      D1: {{
        dados1: {cenarios["D1"]["dados1"]},
        dados2: {cenarios["D1"]["dados2"]},
        dados3a: {cenarios["D1"]["dados3a"]},
        dados3b: {cenarios["D1"]["dados3b"]}
      }},
      D5: {{
        dados1: {cenarios["D5"]["dados1"]},
        dados2: {cenarios["D5"]["dados2"]},
        dados3a: {cenarios["D5"]["dados3a"]},
        dados3b: {cenarios["D5"]["dados3b"]}
      }},
      D10: {{
        dados1: {cenarios["D10"]["dados1"]},
        dados2: {cenarios["D10"]["dados2"]},
        dados3a: {cenarios["D10"]["dados3a"]},
        dados3b: {cenarios["D10"]["dados3b"]}
      }}
    }};

    let chart1, chart2, chart3;

    function criarGrafico(id, datasets) {{
      const ctx = document.getElementById(id).getContext('2d');
      return new Chart(ctx, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: datasets
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{
              display: true
            }}
          }},
          scales: {{
            y: {{
              beginAtZero: true
            }}
          }}
        }}
      }});
    }}

    function atualizarGraficos(cenario) {{
      const dados = cenarios[cenario];
      chart1.data.datasets[0].data = dados.dados1;
      chart2.data.datasets[0].data = dados.dados2;
      chart3.data.datasets[0].data = dados.dados3a;
      chart3.data.datasets[1].data = dados.dados3b;
      chart1.update(); chart2.update(); chart3.update();
    }}

    function expandirGrafico(element) {{
      document.querySelectorAll('.grafico-container').forEach(el => el.style.display = 'none');
      element.classList.add('expandido');
      element.querySelector('.btn-voltar').style.display = 'block';
      element.style.display = 'flex';
    }}

    function voltar(event) {{
      event.stopPropagation();
      const container = event.target.closest('.grafico-container');
      container.classList.remove('expandido');
      container.querySelector('.btn-voltar').style.display = 'none';
      document.querySelectorAll('.grafico-container').forEach(div => {{
        div.style.display = 'block';
      }});
    }}

    function baixarHTML() {{
      const htmlContent = document.documentElement.outerHTML;
      const blob = new Blob([htmlContent], {{ type: "text/html" }});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "dashboard_fase3.html";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    window.onload = function() {{
      chart1 = criarGrafico('grafico1', [
        {{
          label: 'Sensor 1',
          data: cenarios.D1.dados1,
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.3
        }}
      ]);
      chart2 = criarGrafico('grafico2', [
        {{
          label: 'Sensor 2',
          data: cenarios.D1.dados2,
          borderColor: 'rgba(54, 162, 235, 1)',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          tension: 0.3
        }}
      ]);
      chart3 = criarGrafico('grafico3', [
        {{
          label: 'Sensor 3A',
          data: cenarios.D1.dados3a,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.3
        }},
        {{
          label: 'Sensor 3B',
          data: cenarios.D1.dados3b,
          borderColor: 'rgba(153, 102, 255, 1)',
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          tension: 0.3
        }}
      ]);
    }}
  </script>

</body>
</html>
"""

# Salvar em arquivo temporário e abrir no navegador
with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
    f.write(html)
    file_path = f.name

webbrowser.open(f"file://{file_path}")
