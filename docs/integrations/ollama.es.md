# Opcional · Capa de briefing con LLM local vía Ollama

KYNODE Pediátrico incluye un briefing de vigilancia determinista basado en reglas que funciona 100% offline y no requiere configuración. Este documento explica cómo activar opcionalmente un **briefing más rico** generado por un **LLM local**, sin romper la promesa offline-first del producto.

> **¿Por qué Ollama y no Anthropic / OpenAI?**
> El contrato del producto es que cada capa de inteligencia — cálculo clínico, anonimización, interpretación con IA — corre en el edge, sin enviar datos a un API SaaS hospedada. Ollama corre el modelo en la misma máquina del nodo local (o en un servidor pequeño dentro de la red local de la clínica), de forma que la capa de briefing mantiene las mismas garantías offline que el resto del sistema.

---

## Qué obtienes al activarlo

| Característica | Determinista (default) | LLM local (Ollama) |
|---|---|---|
| Internet requerido | ❌ No | ❌ No |
| Datos del paciente enviados a algún lado | ❌ No | ❌ No |
| Costo por llamada | $0 | $0 |
| Tono | Basado en reglas, repetitivo | Naturalmente variado |
| Consideraciones operativas | 2-4 bullets curados por indicador | Bullets formulados a los números reales |
| Frase del titular | Plantilla fija | Generada para la señal específica |
| Auditable | ✅ las reglas están en `brief.py` | ⚠️ la salida depende de los pesos del modelo |

El generador determinista por default **siempre está disponible como fallback**. Si Ollama no responde, el modelo no está descargado, o la respuesta es malformada, el sistema cae silenciosamente al briefing determinista.

---

## Contrato de privacidad (sin cambios)

Ya sea que uses el generador determinista o el LLM, el briefing solo ve el **export agregado semanal ya anonimizado**. El chokepoint es la función `safe_payload()` en `apps/local-node/src/kynode_pediatric_local_node/brief.py`, que copia únicamente campos de la lista permitida:

```
zone, week, indicator, count, baseline_mean, baseline_std,
z_score, flag, severity, signal_source, climate_context (sin notes),
quality_warnings, contains_phi
```

Un test (`test_brief_module_has_no_phi_field_in_safe_export_allowlist`) mantiene esta lista permitida disjunta de cualquier campo que pueda contener PHI, incluso si la capa de almacenamiento cambia.

Cuando apuntas el nodo local a una instancia remota de Ollama dentro de la red local de la clínica, el mismo payload de la lista permitida es lo único que viaja — no hay identificadores de paciente en el cuerpo de la solicitud.

---

## Instalación

### 1 · Instala Ollama en el nodo local

Ollama es un binario único que corre en Linux, macOS y Windows. El instalador toma unos minutos.

**Linux** (target típico de un nodo de clínica):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS** (máquinas de desarrollo / demos de piloto):

Descarga el instalador desde [ollama.com/download](https://ollama.com/download) y ejecútalo.

**Windows** (tabletas Surface usadas como nodos clínicos portátiles):

Descarga el instalador de Windows desde el mismo enlace.

Después de instalar, Ollama corre como servicio en background y escucha en `127.0.0.1:11434` por default. El servicio arranca automáticamente al encender la máquina.

### 2 · Descarga un modelo

Los modelos se descargan una sola vez y se almacenan localmente (tamaños típicos: 1.5GB – 7GB). Para despliegues de clínicas pediátricas recomendamos un modelo pequeño, rápido y multilingüe que quepa en el presupuesto de recursos de un Mini PC:

```bash
ollama pull llama3.2
```

Otras opciones probadas (elige una):

| Modelo | Tamaño | Mejor para |
|---|---|---|
| `llama3.2` | 2GB | **Default recomendado** · calidad sólida en EN/ES, rápido en Mini PC |
| `qwen2.5:3b` | 1.9GB | Español ligeramente mejor, velocidad similar |
| `phi3:mini` | 2.3GB | Modelo instruct pequeño de Microsoft, buen fallback |
| `mistral:7b` | 4.1GB | Mayor calidad, requiere ≥8GB RAM |

Solo necesitas un modelo instalado a la vez. El briefing usa el mismo modelo para inglés y español; el idioma se controla por el system prompt que envía el nodo local.

### 3 · Verifica que Ollama está respondiendo

```bash
curl http://localhost:11434/api/tags
```

Deberías ver una lista JSON con el modelo que descargaste. Si recibes un error de conexión, arranca el servicio manualmente:

```bash
ollama serve
```

---

## Conecta KYNODE Pediátrico con Ollama

El nodo local lee tres variables de entorno. Configúralas donde inicies el nodo local (unidad systemd, archivo Docker compose, archivo `.env` cargado por tu launcher, etc.):

```bash
export KYNODE_AI_BRIEF_PROVIDER=ollama
export KYNODE_AI_BRIEF_MODEL=llama3.2          # opcional · default es llama3.2
export KYNODE_AI_BRIEF_ENDPOINT=http://localhost:11434/api/chat   # opcional · default
```

Reinicia el nodo local. A partir de ahora, el botón **"Briefing de vigilancia con IA"** en la página de Vigilancia llama a Ollama. El chip en la salida del briefing dice **"Briefing con LLM local · Ollama (offline, post-anonimización)"** en lugar del chip determinista.

### Despliegue LAN · un solo Ollama para varias clínicas

Si despliegas varios nodos KYNODE Pediátrico en el mismo edificio o campus, puedes correr **una sola instancia de Ollama** en una máquina ligeramente más grande y apuntar cada nodo de clínica a esta:

```bash
# En el host de Ollama (ej. 10.0.0.10):
OLLAMA_HOST=0.0.0.0 ollama serve

# En cada nodo de clínica:
export KYNODE_AI_BRIEF_ENDPOINT=http://10.0.0.10:11434/api/chat
```

Esto sigue siendo offline — la red LAN es el límite de confianza. Asegúrate de que el host de Ollama no esté expuesto más allá de la red de la clínica (regla de firewall, acceso solo VPN, etc.).

---

## Notas operativas

- **La primera llamada después de un cold start es lenta** (5-10 segundos mientras el modelo se carga en RAM). Las llamadas subsiguientes son típicamente 1-3 segundos.
- **Ollama mantiene el modelo en memoria** por ~5 minutos de inactividad, luego lo descarga. Esto está bien para el uso típico de clínica donde los briefings se generan una vez por semana.
- **Ollama no envía registros de uso a ningún lado**. Si quieres auditar prompts y respuestas para revisión, activa el logging local de Ollama vía `OLLAMA_DEBUG=1`.
- **Desactivable a media jornada si hace falta**: simplemente desactiva `KYNODE_AI_BRIEF_PROVIDER` y reinicia el nodo local — el generador determinista toma el control sin cambios en la UI.

## Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| El briefing siempre muestra el chip "Plantilla determinista" | `KYNODE_AI_BRIEF_PROVIDER` no está configurada o tiene un valor distinto a `ollama` | Verifica la variable; debe ser igual a `ollama` (sin importar mayúsculas) |
| El panel del briefing muestra el toast "Local LLM request failed" | El servicio Ollama no está corriendo, o el endpoint es incorrecto | Ejecuta `ollama serve`, luego verifica `curl http://localhost:11434/api/tags` |
| La generación del briefing es lenta en la primera llamada | El modelo se está cargando en RAM | Normal — las llamadas siguientes son de 1-3s |
| El contenido del briefing está en el idioma equivocado | El modelo es muy pequeño o no maneja bien tu idioma | Prueba `qwen2.5:3b` para español, o usa el generador determinista |
| El URL de revisión hospedada todavía muestra el chip determinista | El demo público hospedado intencionalmente NO activa Ollama (las respuestas LLM cuestan tiempo/RAM y no son necesarias para revisión). Corre localmente para ver el path LLM. | Comportamiento esperado |

## Espacio en disco

| Componente | Disco |
|---|---|
| Binario de Ollama | ~150 MB |
| Un modelo (llama3.2) | ~2 GB |
| Cache del modelo, logs | ~50 MB |
| **Total** | **~2.2 GB** |

Esto está bien dentro del presupuesto de disco del Mini PC de referencia (256 GB SSD) y deja espacio para un segundo modelo si quieres hacer pruebas A/B.

## Desinstalar Ollama

Si una clínica decide no usar el LLM local después de todo:

```bash
# Detener y desinstalar en Linux:
sudo systemctl stop ollama
sudo rm /usr/local/bin/ollama
rm -rf ~/.ollama   # elimina los modelos descargados

# Luego desactiva la variable de entorno en el nodo local:
unset KYNODE_AI_BRIEF_PROVIDER
```

Reinicia el nodo local. La capa de briefing vuelve transparentemente al generador determinista. Sin cambios en el schema, la UI, ni el rastro de auditoría.
