# KYNODE Pediátrico

[![CI](https://github.com/KynodeHealth/kynode-pediatric/actions/workflows/ci.yml/badge.svg)](https://github.com/KynodeHealth/kynode-pediatric/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/KynodeHealth/kynode-pediatric/main/badges/coverage.json)](https://github.com/KynodeHealth/kynode-pediatric/actions/workflows/ci.yml)
[![Demo](https://img.shields.io/badge/demo-GitHub%20Pages-0f766e)](https://kynodehealth.github.io/kynode-pediatric/)

[English](README.md) · [Español](README.es.md)

Vigilancia pediátrica climate-health de código abierto, construida desde el punto de atención.

Lo estamos construyendo desde la realidad de clínicas en Venezuela donde la conectividad intermitente es normal, no una excepción. KYNODE Pediátrico corre en una computadora pequeña dentro de la clínica, sin internet, y convierte los flujos que enfermeras y promotoras de salud ya hacen todos los días - triaje, medición de crecimiento, vacunación, reconocimiento de signos de alarma - en una señal temprana para salud infantil sensible al clima: dengue después de lluvias fuertes, diarrea después de inundaciones, golpe de calor durante olas de calor, brotes respiratorios cuando la calidad del aire baja.

Este módulo se construye sobre [KYNODE](https://kynode.io), nuestro sistema de información clínica propietario que ya corre en clínicas rurales y semiurbanas de Venezuela. Liberamos la capa pediátrica bajo Apache 2.0 porque la población a la que sirve — niños menores de cinco años en entornos desconectados y vulnerables al clima — tiene un caso más fuerte para acceso libre que para captura de ingresos.

## Cómo funciona

El repo es intencionalmente pequeño. Cuatro paquetes funcionan hoy en alpha; el paquete de reglas IMCI sigue siendo trabajo financiable por el grant. Estos componentes organizan señales pediátricas para revisión clínica y vigilancia agregada. No toman decisiones clínicas.

1. **Triaje pediátrico.** Rangos de signos vitales por edad. Un niño de 2 años no se mide contra los umbrales de un adulto. Captura datos estructurados en la entrada — capa de input para todo lo demás.
2. **Curvas de crecimiento OMS.** Peso, talla, IMC y percentiles para 0-60 meses calculados localmente desde una tabla LMS OMS empaquetada. El alpha usa tablas compactas offline con interpolación. Alimenta vigilancia de estado de crecimiento y nutrición; la evaluación formal de desnutrición aguda requiere peso-para-talla/longitud o MUAC y no se afirma en este alpha.
3. **Esquema de vacunación.** Configurable por país. El alpha trae una referencia para Venezuela basada en SVPP 2025, pendiente de validación ministerial antes de despliegue en campo. Alimenta vigilancia de cobertura y brechas de equidad por zona.
4. **Alertas IMCI.** Reglas deterministas del protocolo de la OMS — deshidratación, dificultad respiratoria, patrones de fiebre. Este paquete se implementa después de la decisión del grant y se mantendrá basado en reglas.
5. **Detección de anomalías.** Comparación semanal de indicadores agregados y anonimizados por zona contra una línea base móvil. Marca clusters de enfermedades sensibles al clima — dengue, malaria, diarrea, golpe de calor, brotes respiratorios — antes de que alcancen los umbrales de los reportes mensuales lentos. Estadística simple, no ML. Auditable.

Los identificadores se eliminan en el nodo antes de que algo salga hacia la nube. Los datos clínicos del paciente nunca salen de la clínica. Solo viaja la señal de vigilancia.

## Qué ya está construido

Los paquetes de este repo no son trabajo desde cero. Extraen lógica clínica pediátrica que ya lleva meses corriendo dentro del KYNODE proprietary:

- **Calculadora Z-Score OMS** con tablas LMS — en producción en KYNODE desde marzo de 2026, usada por el flujo de cálculo clínico.
- **Rangos de signos vitales pediátricos por edad** — en producción en el flujo de consulta de KYNODE desde marzo de 2026.
- **Radar de tendencias epidemiológicas con agregación semanal** — en producción en nuestro dashboard de la nube desde marzo de 2026.

Este alpha convierte esas piezas en paquetes standalone bajo Apache 2.0 (`growth-curves`, `triage-ranges`, `anomaly-detection`), suma un paquete nuevo (`vaccinations`) sobre una referencia pública de inmunización para Venezuela, y publica un demo bilingüe pequeño que consume los cuatro paquetes de extremo a extremo. Un quinto paquete (`imci-rules`) está especificado y se publica después de la decisión del grant.

Decidimos abrir la capa pediátrica específicamente porque la población a la que sirve tiene el caso más fuerte para acceso libre. El resto del platform KYNODE (nube, sync, pipeline de inferencia, integración de hardware) sigue siendo propietario.

## En qué etapa está

Alpha pre-piloto. A mayo de 2026 este repositorio contiene cuatro paquetes pediátricos instalables y offline-ready (`growth-curves`, `triage-ranges`, `anomaly-detection` y `vaccinations`), un demo bilingüe que consume JSON generado por esos paquetes, y documentación de arquitectura y roadmap.

Es un prototipo open-source funcional para revisión, evaluación de grant y colaboración técnica. No es software clínico validado en campo, no cubre todo el alcance OMS IMCI y no es un bundle de despliegue de extremo a extremo.

## Demo

El demo usa un caso pediátrico sintético y corre por los cuatro paquetes alpha.

Demo público: [kynodehealth.github.io/kynode-pediatric](https://kynodehealth.github.io/kynode-pediatric/)

![Screenshot del demo KYNODE Pediatric](docs/assets/demo-screenshot.png)

## Limitaciones conocidas

- El demo usa únicamente datos sintéticos.
- El paquete de crecimiento usa tablas OMS LMS compactas para 0-60 meses, con interpolación entre puntos empaquetados.
- El esquema de vacunación de Venezuela se basa en SVPP 2025 y todavía requiere validación MPPS/PAI antes de uso en campo.
- Los umbrales de anomalías son valores iniciales transparentes, no umbrales calibrados con datos de campo.
- El paquete de signos de alarma IMCI no está incluido en este alpha.

## Inicio rápido

```bash
git clone https://github.com/<org>/kynode-pediatric
cd kynode-pediatric

pip install -e packages/growth-curves
pip install -e packages/triage-ranges
pip install -e packages/anomaly-detection
pip install -e packages/vaccinations

pytest packages/growth-curves/tests
pytest packages/triage-ranges/tests
pytest packages/anomaly-detection/tests
pytest packages/vaccinations/tests

python demo/generate_demo_data.py
python -m http.server 8080 -d demo
```

Luego abre `http://localhost:8080`.

Entradas útiles:

- [Architecture](docs/architecture.md) — cómo encaja el módulo dentro de KYNODE.
- [Roadmap](ROADMAP.md) — qué existe, qué falta y qué financiaría el grant.
- [Notas del alpha pre-grant](docs/releases/v0.1.0-pregrant-alpha.md) — cambios, verificación y límites conocidos.
- [Changelog](CHANGELOG.md) — historial de releases y notas del alpha pendiente.
- [Security policy](SECURITY.md) — cómo reportar temas de seguridad o privacidad.

## Por qué open source

La atención de un niño no se decide por código cerrado. Se decide por si la herramienta llega o no llega a la clínica. El resto de KYNODE lo monetizamos; este pedazo lo devolvemos.

## Quiénes estamos detrás

Equipo pequeño en Caracas y Táchira. Construimos KYNODE porque en buena parte del país la alternativa todavía es un cuaderno y un bolígrafo, y no vemos a nadie más resolviéndolo desde adentro.

## Documentación que ya existe en español

- [Manual del trabajador de salud](docs/manual-trabajador-salud.md) — borrador inicial mientras se escribe la primera versión.

El resto de la documentación técnica vive en inglés porque es el idioma en el que se discute el código a nivel global. Si quieres aportar al módulo y tu inglés no es fluido, escribe en español sin problema — el equipo es bilingüe.

## Contacto

opensource@kynode.io · [kynode.io](https://kynode.io)
