//funcion para esconder o mostrar el menu de hamburguesa
function toggleMenu() {
  const menuResponsive = document.getElementById('menu_responsive');
  menuResponsive.classList.toggle('mostrarmenu');
}

//funcion para esconder el menu al scrollear
let prevScrollPos = window.scrollY;
const nav = document.querySelector('.nav');

// window.onscroll = function() {
//   let currentScrollPos = window.scrollY;
  
//   if (prevScrollPos > currentScrollPos) {
//     nav.classList.remove("nav-hidden");
//   } else {
//     nav.classList.add("nav-hidden");
//   }
  
//   prevScrollPos = currentScrollPos;
// };

//verifica que estamos en el index.html
if (window.location.href.includes("index.html")) {
  //verifica que este cargado todo el DOM
  document.addEventListener('DOMContentLoaded', () => {
    //Realiza el fetch para traer las cotizaciones actuales
    fetch("http://127.0.0.1:5000/api/cotizaciones")
    .then(response => response.json())
    .then(data => {
      console.log(data);
      if (data.cotizaciones) {
        // Itera sobre las cotizaciones y las agrega al DOM
        data.cotizaciones.forEach(cotizacion => {
          let nombre = cotizacion.nombre;
          agregarCotizacion(cotizacion.moneda,cotizacion.tipo,cotizacion.venta, cotizacion.compra, cotizacion.fecha);
        });
        actualizarFecha(data.ultima_actualizacion);
      }
    })
    .catch(error => {
      console.error("Error al obtener las cotizaciones:", error);
      //en caso de falla intenta traer del archivo json guardado las ultimas cotizaciones disponibles
      console.log("Intentar traer del cache")
      fetch("../back/cotizaciones.json")
      .then(response => response.json())
      .then(data => {
      console.log(data);
      if (data.cotizaciones) {
        // Itera sobre las cotizaciones y las agrega al DOM
        data.cotizaciones.forEach(cotizacion => {
          agregarCotizacion(cotizacion.moneda,cotizacion.tipo,cotizacion.venta, cotizacion.compra, cotizacion.fecha);
        });
        actualizarFecha(data.ultima_actualizacion);
      }
    })
    });
})}

//funcion para agregar tarjetas copiando una ya creada
function agregarCotizacion(moneda,tipo, venta, compra,fecha) {
  let contenedor = document.querySelector(".principal_tarjeta");
  let tarjeta = document.getElementsByClassName("tarjeta")[0].cloneNode(true);
  let fechaFormateada = '';
  fechaFormateada = fechaFormateada.concat(fecha.slice(0,10)," ",fecha.slice(11,19));
  tarjeta.querySelector("#nombre-moneda").innerHTML = moneda;
  tarjeta.querySelector("#tipo").innerHTML = tipo;
  tarjeta.querySelector("#precio-compra").innerHTML ='Compra: ' + compra;
  tarjeta.querySelector("#precio-venta").innerHTML ='Venta: ' +  venta;
  tarjeta.querySelector("#fecha-actualizacion").innerHTML = 'Fecha actualizacion: <br>' + fechaFormateada;
  contenedor.appendChild(tarjeta);
}

// Función para actualizar la fecha de la última actualización
function actualizarFecha(fecha) {
  let fechaActualizada = new Date(fecha);

  // Formateamos la fecha
  let fechaFormateada = fechaActualizada.toLocaleString('es-ES', {
    dateStyle: 'long',
    timeStyle: 'short'
  });

  // Actualizamos el contenido del elemento en el DOM
  let elementoFecha = document.getElementById("ultima_actualizacion");
  
  if (elementoFecha) {
    elementoFecha.innerHTML ="Ultima actualizacion: " + fechaFormateada;
  } else {
    console.error("No se encontró el elemento con el id 'ultima_actualizacion'.");
  }
  //EVento para hacer aparecer el formulario para enviar las cotizaciones actuales
  document.getElementById('envioCotizacionesMostrar').addEventListener('click', function(event) {
    document.getElementById('enviarCotizaciones').style.display = 'flex';
  })
  //Evento para al completar el formulario enviar las cotizaciones actuales por mail
  const formulario3 = document.getElementById('enviarCotizaciones');
  formulario3.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita que el formulario se envíe de manera tradicional
    
        const data = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            email: document.getElementById('email').value,
        };

        fetch('http://127.0.0.1:5000/api/cotizaciones/email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            mode: "cors",
            body: JSON.stringify(data) // Convierte los datos a formato JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            alert('Cotizaciones enviadas exitosamente.');
            formulario3.reset(); // Resetea el formulario después de enviar
            formulario3.style.display='none';
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Hubo un error al enviar las cotizaciones.');
        });
    })
}

//Verifica que estemos en el historico.html
if (window.location.href.includes("historico.html")){
  document.getElementById('datosHistorico').addEventListener('submit', function(event) {
    event.preventDefault();
  
    // Obtener valores del formulario del historico para hacer la peticion
    const dolar = document.getElementById('dolar').value;
    const fechainicio = document.getElementById('fechainicio').value;
    const fechafin = document.getElementById('fechafin').value;
    const valores = parseInt(document.getElementById('valores').value);
  
    const peticion = `http://127.0.0.1:5000/api/historico/${dolar}/${fechainicio}/${fechafin}/${valores}`;
    //hace la peticion de los datos para graficar los formulario
    fetch(peticion, {mode: 'cors'})
      .then(response => response.json())
      .then(data => {
        console.log(data);
  
        // Preparar datos para el gráfico
        const labels = data.map(item => item.fecha);
        const compraData = data.map(item => item.compra);
        const ventaData = data.map(item => item.venta);
  
        // Configuración de los datos y estilo de los datasets
        const chartData = {
          labels: labels,
          datasets: [
            {
              label: 'Compra',
              data: compraData,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2,
              pointRadius: 3,
              tension: 0.3  // Curvatura de la línea
            },
            {
              label: 'Venta',
              data: ventaData,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 2,
              pointRadius: 3,
              tension: 0.3
            }
          ]
        };
  
        // Opciones del gráfico
        const config = {
          type: 'line',
          data: chartData,
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: `Histórico del Dólar (${dolar})`,
                font: {
                  size: 18
                }
              },
              tooltip: {
                mode: 'index',
                intersect: false,
              },
              legend: {
                position: 'top',
              }
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Fecha'
                }
              },
              y: {
                beginAtZero: false,
                title: {
                  display: true,
                  text: 'Cotización (Pesos)'
                }
              }
            }
          }
        };
  
        // Crear o actualizar el gráfico revisa que no haya grafico para destruir el que este en caso de que pidamos otro grafico
        const ctx = document.getElementById('Grafico').getContext('2d');
        if (window.myChart) {
          window.myChart.destroy();  // Destruir gráfico previo si existe
        }
        window.myChart = new Chart(ctx, config);
      })
      .catch(error => console.error('Error en la petición:', error));
  });
  //Evento para mostrar el formulario para enviar los datos del historico por mail
  document.getElementById('envioHistoricoMostrar').addEventListener('click', function(event) {
    document.getElementById('enviarHistorico').style.display = 'flex';
  })
  //Evento  del formulario para enviar los datos del historico por mail
  const formulario2 = document.getElementById('enviarHistorico');
  formulario2.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita que el formulario se envíe de manera tradicional
    
        const data = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            email: document.getElementById('email').value,
            dolar: document.getElementById('dolar').value,
            fechainicio: document.getElementById('fechainicio').value,
            fechafin: document.getElementById('fechafin').value,
            valores: parseInt(document.getElementById('valores').value)
        };

        fetch('http://127.0.0.1:5000/api/historico/email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            mode: "cors",
            body: JSON.stringify(data) // Convierte los datos a formato JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            alert('Historico enviado exitosamente.');
            formulario2.reset(); // Resetea el formulario después de enviar
            formulario2.style.display='none';
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Hubo un error al enviar el historico.');
        });
  
  
    })
};

//Reviso que este en contacto.html
if (window.location.href.includes("contacto.html")){
  //Reviso que haya terminado de cargar la pagina
  document.addEventListener('DOMContentLoaded', () => {
    //Evento al enviar el formulario de contacto
    const formulario = document.getElementById('formularioContacto');

    formulario.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita que el formulario se envíe de manera tradicional

        const data = {
            nombre: document.getElementById('nombre').value,
            apellido: document.getElementById('apellido').value,
            email: document.getElementById('email').value,
            mensaje: document.getElementById('mensaje').value
        };

        fetch('http://127.0.0.1:5000/api/contacto/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            mode: "cors",
            body: JSON.stringify(data) // Convierte los datos a formato JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            alert('Contacto enviado exitosamente.');
            formulario.reset(); // Resetea el formulario después de enviar
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Hubo un error al enviar el contacto.');
        });
    });
});}   


