// El panel. Tres cosas: pinta el grafo, escucha la ejecucion y enciende nodos.

const diagrama = document.getElementById("diagrama");
const pasos = document.getElementById("pasos");
const factura = document.getElementById("factura");
const boton = document.getElementById("ejecutar");

// Lienzo claro, contenedores blancos, texto negro. El estado se dice con
// borde y con la etiqueta de la leyenda, nunca solo con el color.
const COLORES = {
  dormido: { relleno: "#ffffff", borde: "#d4d4d8", texto: "#71717a" },
  activo: { relleno: "#fffbeb", borde: "#f59e0b", texto: "#78350f" },
  hecho: { relleno: "#ecfdf5", borde: "#10b981", texto: "#065f46" },
};
const LINEA = { dormida: "#b1b1b7", recorrida: "#10b981" };

// ---------------------------------------------------------------- 1 · pintar

// LangGraph mete su propio `classDef` con `fill ... !important` en linea, y eso
// gana a cualquier CSS nuestro. Lo quitamos para poder colorear los nodos.
// De paso lo ponemos en horizontal, que se lee mucho mejor en pantalla ancha.
function limpiar(textoMermaid) {
  return textoMermaid
    .split("\n")
    .filter((linea) => !linea.trim().startsWith("classDef"))
    .map((linea) => linea.replace(/graph\s+TD;?/, "graph LR;"))
    .map((linea) => linea.replace(/:::\w+/g, ""))
    .join("\n");
}

async function pintar() {
  const { mermaid: texto } = await (await fetch("/grafo")).json();
  document.getElementById("fuente").textContent = texto;

  // La tipografia va aqui y NO en el CSS: Mermaid mide el ancho de cada caja
  // con esta fuente. Si se cambia despues por CSS, el texto ya no cabe y sale
  // recortado.
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      background: "#ffffff",
      lineColor: LINEA.dormida,
      primaryColor: "#ffffff",
      primaryBorderColor: "#d4d4d8",
      primaryTextColor: "#18181b",
      fontFamily: '"Cascadia Mono", Consolas, monospace',
      fontSize: "17px",
    },
    flowchart: { curve: "basis", nodeSpacing: 64, rankSpacing: 78, padding: 18 },
  });

  const { svg } = await mermaid.render("grafo", limpiar(texto));
  diagrama.innerHTML = svg;

  // Mermaid deja un `max-width` en linea con el ancho calculado. Sin quitarlo,
  // el diagrama se queda diminuto en medio de la caja.
  const dibujo = diagrama.querySelector("svg");
  dibujo.style.maxWidth = "none";
  dibujo.setAttribute("preserveAspectRatio", "xMidYMid meet");

  limpiarPintura();
}

// ---------------------------------------------------------- 2 · encontrar y colorear

// El id real que pone Mermaid es `grafo-flowchart-<nombre>-<n>`.
// Buscar solo por `flowchart-<nombre>-` no encuentra nada: falta el prefijo.
const todosLosNodos = () => [...diagrama.querySelectorAll("svg g.node")];
const nombreDe = (g) => (g.id.match(/flowchart-(.+)-\d+$/) || [, ""])[1];
const buscarNodo = (nombre) =>
  diagrama.querySelector(`svg [id*="flowchart-${nombre}-"]`);

function pintarNodo(nombre, estado) {
  const g = buscarNodo(nombre);
  if (!g) return;
  const { relleno, borde, texto } = COLORES[estado];

  // `setProperty(..., "important")` es la unica forma de ganarle al estilo en
  // linea que trae el SVG.
  g.querySelectorAll("rect, path.basic, polygon, circle").forEach((forma) => {
    forma.style.setProperty("fill", relleno, "important");
    forma.style.setProperty("stroke", borde, "important");
    forma.style.setProperty("stroke-width", "2px", "important");
  });
  g.querySelectorAll(".nodeLabel, .nodeLabel *, text, tspan").forEach((t) => {
    t.style.setProperty("color", texto, "important");
    t.style.setProperty("fill", texto, "important");
  });

  // El brillo lo pone la animacion `latido` del CSS. Aqui solo se marca cual
  // esta activo, y se limpia el filtro de los que ya no lo estan.
  g.classList.toggle("g-activo", estado === "activo");
  if (estado !== "activo") g.style.filter = "";
}

// Las flechas corren SIEMPRE, para que se lea hacia donde va el flujo aunque
// no se este ejecutando nada. Al pasar por una, se marca en verde.
function pintarArista(desde, hasta) {
  const arista = diagrama.querySelector(`svg [id*="L_${desde}_${hasta}_"]`);
  if (!arista) return;
  arista.style.setProperty("stroke", LINEA.recorrida, "important");
  arista.style.setProperty("stroke-width", "2.6px", "important");
}

function limpiarPintura() {
  todosLosNodos().forEach((g) => pintarNodo(nombreDe(g), "dormido"));
  diagrama.querySelectorAll("svg path.flowchart-link").forEach((a) => {
    a.style.setProperty("stroke", LINEA.dormida, "important");
    a.style.setProperty("stroke-width", "1.8px", "important");
  });
}

// ------------------------------------------------------------- 3 · la lista

// `gasto` es lo que costo ESTE paso, en dolares. Va al lado del nombre del
// nodo: asi se ve de un vistazo que `leer_encargo` no cuesta nada (no llama al
// modelo) y que redactar es el caro.
function anotar(titulo, cambios, esError = false, gasto = null) {
  const fila = document.createElement("div");
  fila.className = esError ? "paso error" : "paso";
  fila.innerHTML = `<b>${titulo}</b>`;
  if (gasto !== null) {
    const etiqueta = document.createElement("span");
    etiqueta.className = gasto > 0 ? "gasto" : "gasto cero";
    etiqueta.textContent = gasto > 0 ? `+$${gasto.toFixed(6)}` : "gratis";
    fila.appendChild(etiqueta);
  }
  if (cambios) {
    const dl = document.createElement("dl");
    for (const [campo, valor] of Object.entries(cambios)) {
      const dt = document.createElement("dt");
      dt.textContent = campo;
      const dd = document.createElement("dd");
      dd.textContent = valor;
      dl.append(dt, dd);
    }
    fila.appendChild(dl);
  } else if (esError) {
    fila.innerHTML += `<dl><dd>${titulo}</dd></dl>`;
  }
  pasos.appendChild(fila);
  fila.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

// ------------------------------------------------------- 3 bis · la factura

// Se repinta en CADA evento, no solo al final: el numero sube segun el agente
// avanza. Los tokens los da la API; los dolares salen de la tabla de precios
// de `agente/precios.py`, que es nuestra y caduca — por eso la fecha va debajo.
function pintarFactura(dato, esFinal) {
  const tokens = Object.values(dato.uso || {})[0] || {};
  factura.innerHTML =
    `<strong>$${(dato.coste || 0).toFixed(6)}</strong>` +
    `${tokens.input_tokens || 0} tokens de entrada · ` +
    `${tokens.output_tokens || 0} de salida` +
    `${esFinal ? "" : " <em>y subiendo…</em>"}<br>` +
    `precios del ${dato.fecha_precios} — si cambian, cambia el número`;
}

// ---------------------------------------------------------- 4 · ejecutar

function ejecutar() {
  boton.disabled = true;
  pasos.innerHTML = "";
  factura.textContent = "";
  limpiarPintura();

  // Lo que llevabamos gastado antes de este paso. La resta da lo que costo el
  // paso que acaba de terminar.
  let costePrevio = 0;

  // Los nodos que estan corriendo ahora mismo. Es una lista y no uno solo
  // porque LangGraph puede ejecutar varios a la vez: en la parte 4 se veran
  // tres encendidos al mismo tiempo.
  let activos = ["__start__"];
  pintarNodo("__start__", "hecho");

  const fuente = new EventSource("/ejecutar");

  fuente.onmessage = (evento) => {
    const dato = JSON.parse(evento.data);

    if (dato.error) {
      anotar(dato.error, null, true);
      fuente.close();
      boton.disabled = false;
      return;
    }

    if (dato.fin) {
      activos.forEach((n) => pintarNodo(n, "hecho"));
      activos.forEach((n) => pintarArista(n, "__end__"));
      pintarNodo("__end__", "hecho");
      pintarFactura(dato, true);
      fuente.close();
      boton.disabled = false;
      return;
    }

    // Lo que costo el paso que acaba de terminar: el acumulado de ahora menos
    // el de antes. Cuando la tanda trae varios nodos (parte 5) el gasto es de
    // la tanda entera y no se puede repartir, asi que se dice tal cual.
    const gasto = (dato.coste || 0) - costePrevio;
    costePrevio = dato.coste || 0;
    const suelto = dato.nodos.length === 1;

    // Un super-step termino: lo que estaba corriendo pasa a hecho, y se
    // encienden los nodos de esta tanda.
    activos.forEach((n) => pintarNodo(n, "hecho"));
    for (const paso of dato.nodos) {
      activos.forEach((previo) => pintarArista(previo, paso.nombre));
      pintarNodo(paso.nombre, "activo");
      anotar(paso.nombre, paso.cambios, false, suelto ? gasto : null);
    }
    if (!suelto) anotar(`${dato.nodos.length} nodos a la vez`, null, false, gasto);
    pintarFactura(dato, false);
    activos = dato.nodos.map((p) => p.nombre);
  };

  fuente.onerror = () => {
    fuente.close();
    boton.disabled = false;
  };
}

boton.addEventListener("click", ejecutar);
pintar();
