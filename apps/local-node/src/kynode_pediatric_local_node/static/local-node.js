// Copyright 2026 KYNODE
// Licensed under the Apache License, Version 2.0.

const I18N = {
  en: {
    eyebrow: "Pre-pilot local node",
    workflow: "Workflow",
    navHome: "Home",
    navIntake: "Local intake",
    navAssessment: "Assessment",
    navSurveillance: "Surveillance",
    navExport: "Aggregate export",
    navRecords: "Records",
    navConfig: "Configuration",
    navConfigShort: "Config",
    offlineMode: "Offline mode",
    offlineModeNote: "Local service running on this machine.",
    clinicMode: "Clinic mode",
    demoMode: "Demo mode",
    clinicModeShort: "Clinic",
    demoModeShort: "Demo",
    syntheticActive: "Synthetic walkthrough active",
    syntheticActiveText: "All weekly signal/export data is clearly marked as synthetic walkthrough data.",
    publicDemoTitle: "Public demo",
    publicDemoText: "Synthetic data only. Do not enter real patient data.",
    publicBoundary: "This public demo uses synthetic data only. Local deployments keep patient data on the clinic device.",
    publicIntakeSubtitle: "Public demo fields are locked to synthetic walkthrough data.",
    publicRecordsPageSubtitle: "Review synthetic demo records and operational events for this public session.",
    publicHistorySubtitle: "Synthetic encounter summaries only.",
    publicStorageLocal: "Public demo resets on restart",
    publicDemoLocked: "Locked in public demo mode",
    runSyntheticAssessment: "Run synthetic assessment",
    saveSyntheticEncounter: "Save synthetic encounter",
    generateSyntheticSignal: "Generate synthetic aggregate signal",
    exportSyntheticJson: "Prepare synthetic aggregate export",
    syntheticControlled: "Synthetic walkthrough controls this data in the public demo.",
    clearSynthetic: "Clear synthetic walkthrough",
    heroTitle: "Offline pediatric climate-health node",
    heroText: "Capture a local encounter, calculate deterministic pediatric support, register weekly climate context, and prepare an aggregate export without PHI.",
    heroNodeLabel: "Node",
    heroVersionLabel: "Version",
    heroLastActivityLabel: "Last activity",
    heroNoActivity: "No activity yet",
    clinicName: "Clinic name",
    nodeLabel: "Node label",
    country: "Country",
    countryHint: "2-letter ISO code (e.g. VE, CO)",
    operator: "Operator",
    saveNode: "Save node setup",
    configEyebrow: "Local node settings",
    configTitle: "Configuration",
    configSubtitle: "Clinic identity, local preferences, and pre-pilot limits.",
    localPreferencesTitle: "Local preferences",
    localPreferencesSubtitle: "Language and theme are stored in this browser.",
    languagePreference: "Language",
    themePreference: "Theme",
    toggleTheme: "Toggle theme",
    nodeSetupTitle: "Local node setup",
    nodeSetupSubtitle: "Clinic identity used only in aggregate exports.",
    workingContext: "Working context",
    contextNoChild: "No child selected",
    ageMonthsShort: "mo",
    statLocal: "Local first",
    statLocalText: "SQLite on device",
    statNoCloud: "No cloud dependency",
    statNoCloudText: "Runs offline in clinic",
    statPhi: "PHI stays local",
    statPhiText: "Aggregate JSON only",
    localBoundary: "Patient-level data stays on this device.",
    aggregateBoundary: "Only aggregated zone-level signal is exportable.",
    clinicalBoundary: "Statistical support only. No autonomous diagnosis.",
    mobileBoundary: "PHI stays local · Statistical support only",
    intakeTitle: "Encounter intake",
    intakeSubtitle: "Local patient-level data; never exported.",
    loadSynthetic: "Load synthetic walkthrough",
    localChildId: "Local child ID",
    birthDate: "Birth date",
    sex: "Sex",
    female: "Female",
    male: "Male",
    zone: "Zone",
    week: "Week",
    indicator: "Indicator",
    dengue: "Dengue suspicion",
    malaria: "Malaria suspicion",
    diarrhea: "Diarrheal disease",
    heat: "Heat-related illness",
    respiratory: "Respiratory outbreak",
    malnutrition: "Malnutrition signal",
    context: "Clinical context",
    syntheticClinicalContext: "Synthetic walkthrough case. Recent heavy rains; clinic working offline.",
    measurements: "Measurements",
    weight: "Weight kg",
    heartRate: "Heart rate",
    respRate: "Resp. rate",
    temperature: "Temp C",
    currentCount: "Current aggregate count",
    baselineCounts: "Baseline weekly counts",
    vaccines: "Vaccines received",
    runAssessment: "Run local assessment",
    saveEncounter: "Save local encounter",
    resultsTitle: "Assessment results",
    resultsSubtitle: "Computed locally from the encounter form.",
    waiting: "Waiting",
    computed: "Computed",
    saved: "Saved locally",
    triageTitle: "Pediatric triage",
    growthTitle: "WHO growth",
    vaccinationTitle: "Vaccination status",
    syndromePreviewTitle: "Syndrome indicator preview",
    weeklyTitle: "Weekly surveillance input",
    weeklySubtitle: "Manual aggregate counts by zone, week, and indicator.",
    saveWeekly: "Save weekly input",
    climateTitle: "Weekly climate context",
    climateSubtitle: "Structured local observation; no weather prediction.",
    surveillanceEyebrow: "Weekly aggregate signal",
    surveillancePageTitle: "Surveillance",
    surveillancePageSubtitle: "Register aggregate counts and climate context before preparing a privacy-safe export.",
    rainfall: "Rainfall",
    unknown: "Unknown",
    none: "None",
    light: "Light",
    moderate: "Moderate",
    heavy: "Heavy",
    flooding: "Flooding",
    no: "No",
    reported: "Reported",
    yes: "Yes",
    heatAlert: "Heat alert",
    waterDisruption: "Water disruption",
    vectorRisk: "Vector risk",
    normal: "Normal",
    increased: "Increased",
    climateSource: "Source",
    clinicObservation: "Clinic observation",
    communityReport: "Community report",
    authorityBulletin: "Authority bulletin",
    other: "Other",
    confidence: "Confidence",
    confidenceLow: "Low",
    confidenceMedium: "Medium",
    confidenceHigh: "High",
    confidenceHelp: "low — single observation, no corroboration\nmedium — multiple observations or corroborated by community\nhigh — corroborated by official authority bulletin",
    climateNotes: "Climate notes",
    saveClimate: "Save climate context",
    historyTitle: "Local encounter history",
    historySubtitle: "Stored only in SQLite on this device.",
    recordsEyebrow: "Local storage",
    recordsPageTitle: "Records",
    recordsPageSubtitle: "Review local encounters and operational events stored on this device.",
    aggregateTitle: "Export readiness",
    aggregateSubtitle: "Prepare weekly aggregate export after weekly input is saved.",
    aggregateEmptyTitle: "No aggregate signal yet",
    aggregateEmptyText: "Save weekly input, then generate the signal before preparing export.",
    briefTitle: "AI surveillance brief",
    briefSubtitle: "Plain-language interpretation of the aggregate signal. Operates only on the privacy-bounded export — never on patient-level data.",
    generateBrief: "Generate brief",
    briefEmptyTitle: "No brief generated yet",
    briefEmptyText: "Generate the brief after preparing the weekly aggregate export.",
    briefHeadline: "Headline",
    briefWhatChanged: "What changed",
    briefWhyReview: "Why this needs review",
    briefOperational: "Operational considerations",
    briefDataLimits: "Data quality limits",
    briefEscalation: "Escalation recommendation",
    briefGeneratorOffline: "Deterministic template (offline, fully auditable)",
    briefGeneratorLLM: "Local LLM brief · Ollama (offline, post-anonymisation)",
    briefRequiresExport: "Prepare the weekly aggregate export first.",
    generateSignal: "Generate aggregate signal",
    exportJson: "Prepare weekly aggregate export",
    exportOutputTitle: "Prepared aggregate file",
    copyJson: "Copy JSON",
    downloadJson: "Download file",
    technicalJsonPreview: "Technical JSON preview",
    copiedJson: "JSON copied",
    downloadedJson: "Aggregate file downloaded",
    exportReadyToShare: "Ready to share: aggregate export contains no PHI.",
    signalTrend: "Weekly signal trend",
    baselineWeeks: "Baseline weeks",
    auditTitle: "Local audit trail",
    auditSubtitle: "Operational events only; audit schema does not store PHI.",
    limitsTitle: "Pre-pilot limits",
    limitsSubtitle: "Clear scope for implementers and reviewers.",
    limitSynthetic: "Synthetic demo data available",
    limitValidation: "Not field validated",
    limitDiagnosis: "No autonomous diagnosis",
    limitGrantWork: "Sync, roles, full IMCI and institutional adapters are grant-funded work",
    footer: "Statistical support only. No autonomous diagnosis.",
    completed: "Completed",
    overdue: "Overdue",
    upcoming: "Upcoming",
    zScore: "Z-score",
    percentile: "Percentile",
    flag: "Flag",
    count: "Count",
    source: "Source",
    baseline: "Baseline",
    weekShort: "wk",
    currentWeek: "Current week",
    exportSafe: "Prepared aggregate export",
    noExportReady: "Save weekly input before preparing export.",
    savedWeekly: "Weekly input saved",
    savedClimate: "Climate context saved",
    savedNode: "Node setup saved",
    syntheticLoaded: "Synthetic walkthrough loaded",
    syntheticCleared: "Synthetic walkthrough cleared",
    loadError: "Local node request failed.",
    emptyAssessment: "Run an assessment to populate this panel.",
    assessmentEmptyTitle: "Run a local assessment to see all four analyses",
    assessmentEmptyText: "Triage, WHO growth, vaccination status, and syndrome indicator preview will populate here.",
    emptyEncounters: "No encounters saved yet. Save a local encounter to populate this list.",
    goToHome: "Go to Home to save an encounter",
    emptyAudit: "No audit events yet.",
    viewAllEvents: "View all events",
    showFewerEvents: "Show fewer",
    retry: "Retry",
    privacyChecklist: "Privacy checklist",
    climateMissing: "No climate context recorded",
    qualityWarnings: "Quality warnings",
    privacyPass: "Cleared",
    privacyNeedsReview: "Needs review",
    todayAt: "today",
    yesterdayAt: "yesterday",
    operationalStatusTitle: "Operational status",
    operationalStatusSubtitle: "Current pre-pilot runtime boundaries.",
    storageStatus: "Storage",
    storageLocal: "Local SQLite only",
    cloudSyncStatus: "Cloud sync",
    cloudSyncNotConfigured: "Not configured",
    versionLabel: "Version",
    schemaPolicyLabel: "Schema policy",
    schemaPolicyPrepilot: "Backup and recreate during pre-pilot",
    flags: {
      normal: "Normal",
      abnormal_low: "Low",
      abnormal_high: "High",
      critical_low: "Critical low",
      critical_high: "Critical high",
      severely_low: "Severely low",
      low: "Low",
      high: "High",
      very_high: "Very high",
      anomaly_high_severity: "High",
      anomaly: "Medium",
      insufficient_baseline: "Insufficient baseline"
    },
    vitals: {
      heart_rate: "Heart rate",
      respiratory_rate: "Resp. rate",
      temperature_c: "Temperature",
      spo2: "SpO2"
    },
    privacyLabels: {
      local_child_id_removed: "Child identifier removed",
      birth_date_removed: "Birth date removed",
      vitals_removed: "Individual vitals removed",
      growth_measurements_removed: "Growth measurements removed",
      vaccination_details_removed: "Vaccination details removed",
      clinical_notes_removed: "Clinical notes removed",
      climate_notes_removed: "Climate notes removed",
      operator_initials_removed: "Operator initials removed",
      aggregate_count_only: "Aggregate count only"
    },
    qualityWarningLabels: {
      prepilot_thresholds_not_field_calibrated: "Pre-pilot thresholds are not field-calibrated yet",
      vaccination_schedule_pending_moh_validation: "Vaccination schedule pending ministry validation",
      no_climate_context_recorded: "Climate context not recorded for this week",
      signal_uses_synthetic_demo_data: "Synthetic walkthrough data"
    },
    auditEventLabels: {
      node_settings_updated: "Node setup updated",
      encounter_saved: "Local encounter saved",
      weekly_input_saved: "Weekly surveillance input saved",
      climate_context_saved: "Climate context saved",
      weekly_signal_generated: "Weekly signal generated",
      weekly_export_prepared: "Aggregate export prepared",
      weekly_brief_generated: "Surveillance brief generated",
      synthetic_walkthrough_loaded: "Synthetic walkthrough loaded",
      synthetic_walkthrough_cleared: "Synthetic walkthrough cleared"
    },
    entityKindLabels: {
      node: "Node settings",
      node_settings: "Node settings",
      encounter: "Local encounter",
      weekly_signal: "Weekly Signal",
      weekly_climate_context: "Weekly Climate Context",
      demo: "Synthetic Walkthrough"
    },
    sourceLabels: {
      manual_aggregate_entry: "Manual aggregate entry",
      manual_local_entry: "Manual local entry",
      synthetic_demo: "Synthetic walkthrough",
      clinic_observation: "Clinic observation",
      community_report: "Community report",
      authority_bulletin: "Authority bulletin",
      deterministic_template: "Deterministic template",
      llm_brief_v1: "Local LLM (Ollama)",
      other: "Other"
    },
    indicatorLabels: {
      dengue_suspicion: "Dengue suspicion",
      malaria_suspicion: "Malaria suspicion",
      diarrheal_disease: "Diarrheal disease",
      heat_related_illness: "Heat-related illness",
      respiratory_outbreak: "Respiratory outbreak",
      malnutrition_signal: "Malnutrition signal"
    },
    doseLabels: {
      BCG: "BCG",
      hepB_birth: "HepB at birth",
      pentavalent_1: "Pentavalent, dose 1",
      polio_1: "Polio, dose 1",
      rotavirus_1: "Rotavirus, dose 1",
      pcv_1: "PCV, dose 1",
      pentavalent_2: "Pentavalent, dose 2",
      polio_2: "Polio, dose 2",
      rotavirus_2: "Rotavirus, dose 2",
      pcv_2: "PCV, dose 2",
      pentavalent_3: "Pentavalent, dose 3",
      polio_3: "Polio, dose 3",
      rotavirus_3: "Rotavirus, dose 3",
      pcv_3: "PCV, dose 3",
      mmr_1: "MMR, dose 1",
      yellow_fever_1: "Yellow fever, dose 1",
      pcv_booster: "PCV booster",
      pentavalent_booster: "Pentavalent booster",
      mmr_2: "MMR, 5-year dose"
    }
  },
  es: {
    eyebrow: "Nodo local pre-piloto",
    workflow: "Flujo",
    navHome: "Inicio",
    navIntake: "Captura local",
    navAssessment: "Evaluación",
    navSurveillance: "Vigilancia",
    navExport: "Export agregado",
    navRecords: "Registros",
    navConfig: "Configuración",
    navConfigShort: "Config",
    offlineMode: "Modo offline",
    offlineModeNote: "Servicio local corriendo en esta máquina.",
    clinicMode: "Modo clínica",
    demoMode: "Modo demo",
    clinicModeShort: "Clínica",
    demoModeShort: "Demo",
    syntheticActive: "Recorrido sintético activo",
    syntheticActiveText: "Toda señal y exportación semanal queda marcada como datos sintéticos de demostración.",
    publicDemoTitle: "Demo público",
    publicDemoText: "Solo datos sintéticos. No ingreses datos reales de pacientes.",
    publicBoundary: "Este demo público usa únicamente datos sintéticos. Los despliegues locales mantienen los datos del paciente en el dispositivo de la clínica.",
    publicIntakeSubtitle: "Los campos del demo público están bloqueados al recorrido sintético.",
    publicRecordsPageSubtitle: "Revisa registros sintéticos y eventos operativos de esta sesión pública.",
    publicHistorySubtitle: "Solo resúmenes de encuentros sintéticos.",
    publicStorageLocal: "El demo público se reinicia al arrancar",
    publicDemoLocked: "Bloqueado en modo demo público",
    runSyntheticAssessment: "Evaluar caso sintético",
    saveSyntheticEncounter: "Guardar encuentro sintético",
    generateSyntheticSignal: "Generar señal sintética agregada",
    exportSyntheticJson: "Preparar exportación sintética",
    syntheticControlled: "El recorrido sintético controla estos datos en el demo público.",
    clearSynthetic: "Limpiar recorrido sintético",
    heroTitle: "Nodo pediátrico clima-salud offline",
    heroText: "Captura un encuentro local, calcula apoyo pediátrico determinístico, registra contexto climático semanal y prepara una exportación agregada sin PHI.",
    heroNodeLabel: "Nodo",
    heroVersionLabel: "Versión",
    heroLastActivityLabel: "Última actividad",
    heroNoActivity: "Sin actividad aún",
    clinicName: "Nombre de clínica",
    nodeLabel: "Etiqueta del nodo",
    country: "País",
    countryHint: "Código ISO de 2 letras (ej. VE, CO)",
    operator: "Operador",
    saveNode: "Guardar nodo",
    configEyebrow: "Ajustes del nodo local",
    configTitle: "Configuración",
    configSubtitle: "Identidad de clínica, preferencias locales y límites pre-piloto.",
    localPreferencesTitle: "Preferencias locales",
    localPreferencesSubtitle: "El idioma y el tema se guardan en este navegador.",
    languagePreference: "Idioma",
    themePreference: "Tema",
    toggleTheme: "Cambiar tema",
    nodeSetupTitle: "Configuración del nodo local",
    nodeSetupSubtitle: "Identidad de la clínica usada solo en exportaciones agregadas.",
    workingContext: "Contexto activo",
    contextNoChild: "Sin niño seleccionado",
    ageMonthsShort: "meses",
    statLocal: "Local primero",
    statLocalText: "SQLite en el dispositivo",
    statNoCloud: "Sin dependencia cloud",
    statNoCloudText: "Funciona offline en clínica",
    statPhi: "Datos identificables locales",
    statPhiText: "Solo JSON agregado",
    localBoundary: "Los datos del paciente permanecen en este dispositivo.",
    aggregateBoundary: "Solo se exporta la señal agregada por zona.",
    clinicalBoundary: "Apoyo estadístico únicamente. Sin diagnóstico autónomo.",
    mobileBoundary: "Datos identificables locales · Solo apoyo estadístico",
    intakeTitle: "Captura del encuentro",
    intakeSubtitle: "Datos del paciente locales; nunca exportados.",
    loadSynthetic: "Cargar recorrido sintético",
    localChildId: "ID local del niño",
    birthDate: "Fecha de nacimiento",
    sex: "Sexo",
    female: "Femenino",
    male: "Masculino",
    zone: "Zona",
    week: "Semana",
    indicator: "Indicador",
    dengue: "Sospecha de dengue",
    malaria: "Sospecha de malaria",
    diarrhea: "Enfermedad diarreica",
    heat: "Evento asociado a calor",
    respiratory: "Brote respiratorio",
    malnutrition: "Señal de malnutrición",
    context: "Contexto clínico",
    syntheticClinicalContext: "Caso de recorrido sintético. Lluvias fuertes recientes; clínica trabajando offline.",
    measurements: "Mediciones",
    weight: "Peso kg",
    heartRate: "Frecuencia cardíaca",
    respRate: "Frecuencia resp.",
    temperature: "Temp C",
    currentCount: "Conteo agregado actual",
    baselineCounts: "Conteos semanales base",
    vaccines: "Vacunas recibidas",
    runAssessment: "Evaluar caso local",
    saveEncounter: "Guardar encuentro local",
    resultsTitle: "Resultados de evaluación",
    resultsSubtitle: "Calculado localmente a partir del formulario.",
    waiting: "Esperando",
    computed: "Calculado",
    saved: "Guardado localmente",
    triageTitle: "Triaje pediátrico",
    growthTitle: "Crecimiento OMS",
    vaccinationTitle: "Estado de vacunación",
    syndromePreviewTitle: "Vista previa de indicador sindrómico",
    weeklyTitle: "Registro semanal de vigilancia",
    weeklySubtitle: "Conteos agregados manuales por zona, semana e indicador.",
    saveWeekly: "Guardar registro semanal",
    climateTitle: "Contexto climático semanal",
    climateSubtitle: "Observación local estructurada; sin predicción meteorológica.",
    surveillanceEyebrow: "Señal agregada semanal",
    surveillancePageTitle: "Vigilancia",
    surveillancePageSubtitle: "Registra conteos agregados y contexto climático antes de preparar una exportación segura.",
    rainfall: "Lluvia",
    unknown: "Desconocido",
    none: "Ninguna",
    light: "Ligera",
    moderate: "Moderada",
    heavy: "Fuerte",
    flooding: "Inundación",
    no: "No",
    reported: "Reportada",
    yes: "Sí",
    heatAlert: "Alerta de calor",
    waterDisruption: "Interrupción de agua",
    vectorRisk: "Riesgo vectorial",
    normal: "Normal",
    increased: "Aumentado",
    climateSource: "Fuente",
    clinicObservation: "Observación clínica",
    communityReport: "Reporte comunitario",
    authorityBulletin: "Boletín de autoridad",
    other: "Otro",
    confidence: "Confianza",
    confidenceLow: "Baja",
    confidenceMedium: "Media",
    confidenceHigh: "Alta",
    confidenceHelp: "baja — una observación, sin corroboración\nmedia — múltiples observaciones o corroborada por la comunidad\nalta — corroborada por boletín oficial",
    climateNotes: "Notas climáticas",
    saveClimate: "Guardar contexto climático",
    historyTitle: "Historial local de encuentros",
    historySubtitle: "Guardado solo en SQLite en este dispositivo.",
    recordsEyebrow: "Almacenamiento local",
    recordsPageTitle: "Registros",
    recordsPageSubtitle: "Revisa encuentros locales y eventos operativos guardados en este dispositivo.",
    aggregateTitle: "Preparar exportación",
    aggregateSubtitle: "Prepara la exportación semanal agregada después de guardar el registro semanal.",
    aggregateEmptyTitle: "Aún no hay señal agregada",
    aggregateEmptyText: "Guarda el registro semanal y luego genera la señal antes de preparar la exportación.",
    briefTitle: "Briefing de vigilancia con IA",
    briefSubtitle: "Interpretación en lenguaje claro de la señal agregada. Opera únicamente sobre el export anonimizado — nunca sobre datos de paciente.",
    generateBrief: "Generar briefing",
    briefEmptyTitle: "Aún no hay briefing generado",
    briefEmptyText: "Genera el briefing después de preparar el export agregado semanal.",
    briefHeadline: "Titular",
    briefWhatChanged: "Qué cambió",
    briefWhyReview: "Por qué requiere revisión",
    briefOperational: "Consideraciones operativas",
    briefDataLimits: "Límites de calidad de los datos",
    briefEscalation: "Recomendación de escalamiento",
    briefGeneratorOffline: "Plantilla determinista (offline, totalmente auditable)",
    briefGeneratorLLM: "Briefing con LLM local · Ollama (offline, post-anonimización)",
    briefRequiresExport: "Prepara primero el export agregado semanal.",
    generateSignal: "Generar señal agregada",
    exportJson: "Preparar exportación agregada",
    exportOutputTitle: "Archivo agregado listo",
    copyJson: "Copiar JSON",
    downloadJson: "Descargar archivo",
    technicalJsonPreview: "Vista técnica del JSON",
    copiedJson: "JSON copiado",
    downloadedJson: "Archivo agregado descargado",
    exportReadyToShare: "Listo para compartir: la exportación agregada no contiene datos identificables de pacientes.",
    signalTrend: "Tendencia semanal de señal",
    baselineWeeks: "Semanas base",
    auditTitle: "Auditoría local",
    auditSubtitle: "Solo eventos operativos; la auditoría no guarda datos identificables.",
    limitsTitle: "Límites pre-piloto",
    limitsSubtitle: "Alcance claro para implementadores y evaluadores.",
    limitSynthetic: "Datos sintéticos disponibles",
    limitValidation: "No validado en campo",
    limitDiagnosis: "Sin diagnóstico autónomo",
    limitGrantWork: "Sincronización, roles, IMCI completo y adaptadores institucionales son trabajo financiado por el grant",
    footer: "Apoyo estadístico únicamente. Sin diagnóstico autónomo.",
    completed: "Completadas",
    overdue: "Atrasadas",
    upcoming: "Próximas",
    zScore: "Z-score",
    percentile: "Percentil",
    flag: "Bandera",
    count: "Conteo",
    source: "Fuente",
    baseline: "Línea base",
    weekShort: "sem",
    currentWeek: "Semana actual",
    exportSafe: "Exportación agregada preparada",
    noExportReady: "Guarda el registro semanal antes de preparar la exportación.",
    savedWeekly: "Registro semanal guardado",
    savedClimate: "Contexto climático guardado",
    savedNode: "Nodo guardado",
    syntheticLoaded: "Recorrido sintético cargado",
    syntheticCleared: "Recorrido sintético limpiado",
    loadError: "Falló la solicitud al nodo local.",
    emptyAssessment: "Evalúa un caso para poblar este panel.",
    assessmentEmptyTitle: "Evalúa un caso local para ver los cuatro análisis",
    assessmentEmptyText: "Triaje, crecimiento OMS, vacunas e indicador sindrómico aparecerán aquí.",
    emptyEncounters: "Aún no hay encuentros guardados. Guarda un encuentro local para poblar esta lista.",
    goToHome: "Ir a Inicio para guardar un encuentro",
    emptyAudit: "Aún no hay eventos de auditoría.",
    viewAllEvents: "Ver todos los eventos",
    showFewerEvents: "Mostrar menos",
    retry: "Reintentar",
    privacyChecklist: "Checklist de privacidad",
    climateMissing: "No hay contexto climático registrado",
    qualityWarnings: "Advertencias de calidad",
    privacyPass: "Verificado",
    privacyNeedsReview: "Revisar",
    todayAt: "hoy",
    yesterdayAt: "ayer",
    operationalStatusTitle: "Estado operativo",
    operationalStatusSubtitle: "Límites actuales del nodo pre-piloto.",
    storageStatus: "Almacenamiento",
    storageLocal: "Solo SQLite local",
    cloudSyncStatus: "Sincronización en nube",
    cloudSyncNotConfigured: "No configurado",
    versionLabel: "Versión",
    schemaPolicyLabel: "Política de estructura de datos",
    schemaPolicyPrepilot: "Respaldo y recreación durante pre-piloto",
    flags: {
      normal: "Normal",
      abnormal_low: "Bajo",
      abnormal_high: "Alto",
      critical_low: "Crítico bajo",
      critical_high: "Crítico alto",
      severely_low: "Severamente bajo",
      low: "Bajo",
      high: "Alto",
      very_high: "Muy alto",
      anomaly_high_severity: "Alta",
      anomaly: "Media",
      insufficient_baseline: "Línea base insuficiente"
    },
    vitals: {
      heart_rate: "Frecuencia cardíaca",
      respiratory_rate: "Frecuencia resp.",
      temperature_c: "Temperatura",
      spo2: "SpO2"
    },
    privacyLabels: {
      local_child_id_removed: "ID local del niño no incluido",
      birth_date_removed: "Fecha de nacimiento no incluida",
      vitals_removed: "Signos vitales individuales no incluidos",
      growth_measurements_removed: "Mediciones de crecimiento no incluidas",
      vaccination_details_removed: "Detalle de vacunas no incluido",
      clinical_notes_removed: "Notas clínicas no incluidas",
      climate_notes_removed: "Notas climáticas no incluidas",
      operator_initials_removed: "Iniciales del operador no incluidas",
      aggregate_count_only: "Solo conteo agregado"
    },
    qualityWarningLabels: {
      prepilot_thresholds_not_field_calibrated: "Umbrales pre-piloto aún no calibrados en campo",
      vaccination_schedule_pending_moh_validation: "Esquema de vacunación pendiente de validación ministerial",
      no_climate_context_recorded: "No hay contexto climático registrado para esta semana",
      signal_uses_synthetic_demo_data: "Datos del recorrido sintético"
    },
    auditEventLabels: {
      node_settings_updated: "Configuración del nodo actualizada",
      encounter_saved: "Encuentro local guardado",
      weekly_input_saved: "Registro semanal de vigilancia guardado",
      climate_context_saved: "Contexto climático guardado",
      weekly_signal_generated: "Señal semanal generada",
      weekly_export_prepared: "Exportación agregada preparada",
      weekly_brief_generated: "Briefing de vigilancia generado",
      synthetic_walkthrough_loaded: "Recorrido sintético cargado",
      synthetic_walkthrough_cleared: "Recorrido sintético limpiado"
    },
    entityKindLabels: {
      node: "Configuración del nodo",
      node_settings: "Configuración del nodo",
      encounter: "Encuentro local",
      weekly_signal: "Señal semanal",
      weekly_climate_context: "Contexto climático semanal",
      demo: "Recorrido sintético"
    },
    sourceLabels: {
      manual_aggregate_entry: "Entrada agregada manual",
      manual_local_entry: "Entrada local manual",
      synthetic_demo: "Recorrido sintético",
      clinic_observation: "Observación clínica",
      community_report: "Reporte comunitario",
      authority_bulletin: "Boletín de autoridad",
      deterministic_template: "Plantilla determinista",
      llm_brief_v1: "LLM local (Ollama)",
      other: "Otro"
    },
    indicatorLabels: {
      dengue_suspicion: "Sospecha de dengue",
      malaria_suspicion: "Sospecha de malaria",
      diarrheal_disease: "Enfermedad diarreica",
      heat_related_illness: "Evento asociado a calor",
      respiratory_outbreak: "Brote respiratorio",
      malnutrition_signal: "Señal de malnutrición"
    },
    doseLabels: {
      BCG: "BCG",
      hepB_birth: "HepB al nacer",
      pentavalent_1: "Pentavalente, 1ª dosis",
      polio_1: "Polio, 1ª dosis",
      rotavirus_1: "Rotavirus, 1ª dosis",
      pcv_1: "Neumococo, 1ª dosis",
      pentavalent_2: "Pentavalente, 2ª dosis",
      polio_2: "Polio, 2ª dosis",
      rotavirus_2: "Rotavirus, 2ª dosis",
      pcv_2: "Neumococo, 2ª dosis",
      pentavalent_3: "Pentavalente, 3ª dosis",
      polio_3: "Polio, 3ª dosis",
      rotavirus_3: "Rotavirus, 3ª dosis",
      pcv_3: "Neumococo, 3ª dosis",
      mmr_1: "SRP, 1ª dosis",
      yellow_fever_1: "Fiebre amarilla, 1ª dosis",
      pcv_booster: "Refuerzo neumococo",
      pentavalent_booster: "Refuerzo pentavalente",
      mmr_2: "SRP, dosis de 5 años"
    }
  }
};

const VISIBLE_I18N_FALLBACKS = {
  en: {
    assessmentEmptyTitle: "Run a local assessment to see all four analyses",
    assessmentEmptyText: "Triage, WHO growth, vaccination status, and syndrome indicator preview will populate here.",
    countryHint: "2-letter ISO code (e.g. VE, CO)"
  },
  es: {
    assessmentEmptyTitle: "Evalúa un caso local para ver los cuatro análisis",
    assessmentEmptyText: "Triaje, crecimiento OMS, vacunas e indicador sindrómico aparecerán aquí.",
    countryHint: "Código ISO de 2 letras (ej. VE, CO)"
  }
};

const DOSE_MONTHS = {
  BCG: 0,
  hepB_birth: 0,
  pentavalent_1: 2,
  polio_1: 2,
  rotavirus_1: 2,
  pcv_1: 2,
  pentavalent_2: 4,
  polio_2: 4,
  rotavirus_2: 4,
  pcv_2: 4,
  pentavalent_3: 6,
  polio_3: 6,
  rotavirus_3: 6,
  pcv_3: 6,
  mmr_1: 12,
  yellow_fever_1: 12,
  pcv_booster: 15,
  pentavalent_booster: 18,
  mmr_2: 60
};

const state = {
  lang: I18N[localStorage.getItem("kynode-local-node-lang")] ? localStorage.getItem("kynode-local-node-lang") : "en",
  mode: "clinic",
  runtime: {
    mode: "local_clinic",
    public_demo: false,
    synthetic_only: false,
    warning: ""
  },
  assessment: null,
  aggregateSignal: null,
  lastExport: null,
  auditExpanded: false
};

function t(key) {
  const lang = I18N[state.lang] ? state.lang : "en";
  return (
    I18N[lang]?.[key]
    || VISIBLE_I18N_FALLBACKS[lang]?.[key]
    || I18N.en?.[key]
    || VISIBLE_I18N_FALLBACKS.en?.[key]
    || humanizeKey(key)
  );
}

function humanizeKey(key) {
  return String(key || "")
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function mappedLabel(group, key) {
  return I18N[state.lang][group]?.[key] || humanizeKey(key);
}

function flagLabel(flag) {
  return I18N[state.lang].flags[flag] || flag;
}

function sourceLabel(source) {
  return mappedLabel("sourceLabels", source);
}

function indicatorLabel(indicator) {
  return mappedLabel("indicatorLabels", indicator);
}

function doseLabel(dose) {
  return mappedLabel("doseLabels", dose);
}

function entityKeyLabel(entityKey) {
  if (!entityKey) return "";
  if (entityKey === "synthetic_walkthrough") return entityKindLabel("demo");
  const parts = String(entityKey).split("|");
  if (parts.length === 3) return `${parts[0]} · ${parts[1]} · ${indicatorLabel(parts[2])}`;
  if (parts.length === 2) return `${parts[0]} · ${parts[1]}`;
  return humanizeKey(entityKey);
}

function entityKindLabel(entityKind) {
  return mappedLabel("entityKindLabels", entityKind);
}

function chipClass(flag) {
  if (!flag) return "ok";
  if (flag.includes("critical") || flag.includes("high_severity")) return "danger";
  if (flag.includes("abnormal") || flag === "low" || flag === "high" || flag === "anomaly" || flag === "insufficient_baseline") return "warning";
  return "ok";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function inlineIcon(name, size = 16) {
  return window.KynodeIcons?.icon ? window.KynodeIcons.icon(name, { size }) : "";
}

function todayLocalIsoDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function currentIsoWeek() {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() + 3 - ((date.getDay() + 6) % 7));
  const weekOne = new Date(date.getFullYear(), 0, 4);
  const week = 1 + Math.round(((date - weekOne) / 86400000 - 3 + ((weekOne.getDay() + 6) % 7)) / 7);
  return `${date.getFullYear()}-W${String(week).padStart(2, "0")}`;
}

function ageMonthsFromBirthDate(birthDate) {
  if (!birthDate) return null;
  const birth = new Date(`${birthDate}T00:00:00`);
  if (Number.isNaN(birth.getTime())) return null;
  const reference = state.mode === "synthetic_demo" ? new Date("2026-05-06T00:00:00") : new Date();
  let months = (reference.getFullYear() - birth.getFullYear()) * 12;
  months += reference.getMonth() - birth.getMonth();
  if (reference.getDate() < birth.getDate()) months -= 1;
  return Math.max(0, months);
}

function formatTimestamp(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  const time = date.toLocaleTimeString(state.lang === "es" ? "es-VE" : "en-US", {
    hour: "2-digit",
    minute: "2-digit"
  });
  if (sameDay) return `${t("todayAt")} ${time}`;
  if (date.toDateString() === yesterday.toDateString()) return `${t("yesterdayAt")} ${time}`;
  return date.toLocaleDateString(state.lang === "es" ? "es-VE" : "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function setLanguage(lang) {
  state.lang = I18N[lang] ? lang : "en";
  localStorage.setItem("kynode-local-node-lang", state.lang);
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll(".lang").forEach((button) => {
    const active = button.dataset.lang === state.lang;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  renderMode();
  if (state.assessment) renderAssessment(state.assessment);
  else renderEmptyAssessment();
  if (state.aggregateSignal) renderAggregate(state.aggregateSignal);
  else renderEmptyAggregate();
  if (state.lastExport) renderPrivacyChecklist(state.lastExport);
  buildVaccineGrid();
  updateContextBar();
  applyRuntimeMode();
  loadEncounters();
  loadAuditEvents();
}

function isPublicDemo() {
  return Boolean(state.runtime?.public_demo);
}

function setTextByI18nKey(selector, key) {
  const el = document.querySelector(selector);
  if (el) el.textContent = t(key);
}

function setFormControlsDisabled(formId, disabled) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.querySelectorAll("input, select, textarea").forEach((field) => {
    field.disabled = disabled;
    if (disabled) field.setAttribute("title", t("publicDemoLocked"));
    else field.removeAttribute("title");
  });
}

function applyRuntimeMode() {
  const publicDemo = isPublicDemo();
  document.body.dataset.runtimeMode = publicDemo ? "public-demo" : "local-clinic";
  document.getElementById("public-demo-banner")?.classList.toggle("hidden", !publicDemo);

  setTextByI18nKey("[data-i18n='localBoundary']", publicDemo ? "publicBoundary" : "localBoundary");
  setTextByI18nKey("[data-i18n='mobileBoundary']", publicDemo ? "publicDemoText" : "mobileBoundary");
  setTextByI18nKey("[data-i18n='intakeSubtitle']", publicDemo ? "publicIntakeSubtitle" : "intakeSubtitle");
  setTextByI18nKey("[data-i18n='recordsPageSubtitle']", publicDemo ? "publicRecordsPageSubtitle" : "recordsPageSubtitle");
  setTextByI18nKey("[data-i18n='historySubtitle']", publicDemo ? "publicHistorySubtitle" : "historySubtitle");
  setTextByI18nKey("[data-i18n='storageLocal']", publicDemo ? "publicStorageLocal" : "storageLocal");
  setTextByI18nKey("[data-i18n='runAssessment']", publicDemo ? "runSyntheticAssessment" : "runAssessment");
  setTextByI18nKey("[data-i18n='saveEncounter']", publicDemo ? "saveSyntheticEncounter" : "saveEncounter");
  setTextByI18nKey("[data-i18n='generateSignal']", publicDemo ? "generateSyntheticSignal" : "generateSignal");
  setTextByI18nKey("[data-i18n='exportJson']", publicDemo ? "exportSyntheticJson" : "exportJson");

  setFormControlsDisabled("case-form", publicDemo);
  setFormControlsDisabled("weekly-form", publicDemo);
  setFormControlsDisabled("climate-form", publicDemo);
  setFormControlsDisabled("node-settings-form", publicDemo);

  for (const id of ["save-weekly-input", "save-climate-context", "save-node-settings"]) {
    const button = document.getElementById(id);
    if (!button) continue;
    button.disabled = publicDemo;
    if (publicDemo) button.setAttribute("title", t("syntheticControlled"));
    else button.removeAttribute("title");
  }
}

function renderMode() {
  const pill = document.getElementById("mode-pill");
  const banner = document.getElementById("synthetic-banner");
  if (!pill || !banner) return;
  const isDemo = state.mode === "synthetic_demo";
  const compact = typeof window !== "undefined" && window.matchMedia("(max-width: 760px)").matches;
  pill.textContent = isDemo
    ? t(compact ? "demoModeShort" : "demoMode")
    : t(compact ? "clinicModeShort" : "clinicMode");
  pill.classList.toggle("warning", isDemo);
  pill.classList.toggle("ok", !isDemo);
  banner.classList.toggle("hidden", !isDemo);
}

const VIEW_IDS = ["home", "surveillance", "records", "configuration"];

function viewFromHash(hash = window.location.hash) {
  const target = (hash || "#home").replace("#", "");
  if (VIEW_IDS.includes(target)) return target;
  const targetEl = document.getElementById(target);
  return targetEl?.closest(".page-view")?.dataset.view || "home";
}

function showView(viewId = viewFromHash()) {
  const resolved = VIEW_IDS.includes(viewId) ? viewId : "home";
  const target = (window.location.hash || "").replace("#", "");
  const targetEl = target && !VIEW_IDS.includes(target) ? document.getElementById(target) : null;
  document.querySelectorAll(".page-view").forEach((view) => {
    view.classList.toggle("active", view.dataset.view === resolved);
  });
  document.querySelectorAll("[data-view-link]").forEach((link) => {
    const active = link.dataset.viewLink === resolved;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  setMobileNav(false);
  // A toast that fired in the previous view is no longer relevant
  // — dismiss it so it doesn't overlap content on the new view.
  dismissToastIfPresent();
  requestAnimationFrame(() => {
    if (targetEl) targetEl.scrollIntoView({ block: "start" });
    else window.scrollTo({ top: 0, behavior: "auto" });
  });
}

function setExportActionsEnabled(enabled) {
  for (const id of ["copy-export", "download-export"]) {
    const button = document.getElementById(id);
    if (button) button.disabled = !enabled;
  }
  document.querySelector(".export-actions")?.classList.toggle("hidden", !enabled);
}

function parseCounts(value) {
  return String(value || "")
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((item) => Number.isFinite(item));
}

function isoDateAddMonths(dateText, months) {
  const date = new Date(`${dateText}T00:00:00`);
  const originalDay = date.getDate();
  date.setMonth(date.getMonth() + months);
  if (date.getDate() < originalDay) date.setDate(0);
  return date.toISOString().slice(0, 10);
}

function numberValue(form, name) {
  const value = form.elements[name].value;
  return value === "" ? null : Number(value);
}

function collectAssessmentPayload() {
  const form = document.getElementById("case-form");
  const birthDate = form.elements.birth_date.value;
  const vaccinations = [...document.querySelectorAll(".vaccine-option input:checked")].map((input) => ({
    vaccine: input.value,
    date: isoDateAddMonths(birthDate, Number(input.dataset.month))
  }));
  return {
    local_child_id: form.elements.local_child_id.value.trim(),
    birth_date: birthDate,
    sex: form.elements.sex.value,
    zone: form.elements.zone.value.trim(),
    context: form.elements.context.value.trim(),
    weight_kg: numberValue(form, "weight_kg"),
    vitals: {
      heart_rate: numberValue(form, "heart_rate"),
      respiratory_rate: numberValue(form, "respiratory_rate"),
      temperature_c: numberValue(form, "temperature_c"),
      spo2: numberValue(form, "spo2")
    },
    vaccinations_received: vaccinations,
    syndrome_indicator: form.elements.syndrome_indicator.value,
    week: form.elements.week.value.trim(),
    reference_date: state.mode === "synthetic_demo" ? "2026-05-06" : todayLocalIsoDate()
  };
}

function resolveZoneWeekIndicator() {
  const caseForm = document.getElementById("case-form");
  const weeklyForm = document.getElementById("weekly-form");
  return {
    zone: weeklyForm.elements.zone.value.trim() || caseForm.elements.zone.value.trim(),
    week: weeklyForm.elements.week.value.trim() || caseForm.elements.week.value.trim(),
    indicator: weeklyForm.elements.indicator.value || caseForm.elements.syndrome_indicator.value
  };
}

function updateContextBar() {
  const caseForm = document.getElementById("case-form");
  if (!caseForm) return;
  const resolved = resolveZoneWeekIndicator();
  const childId = caseForm.elements.local_child_id.value.trim();
  const sex = caseForm.elements.sex.value;
  const ageMonths = ageMonthsFromBirthDate(caseForm.elements.birth_date.value);
  const sexShort = sex ? sex.charAt(0).toUpperCase() : "";
  const ageText = ageMonths === null ? "" : `${ageMonths} ${t("ageMonthsShort")}`;
  const childParts = childId ? [childId, sexShort, ageText].filter(Boolean) : [];
  const childEl = document.getElementById("context-child");
  const mobileChildEl = document.getElementById("context-mobile-child");
  const mobileMetaEl = document.getElementById("context-mobile-meta");
  const zoneEl = document.getElementById("context-zone");
  const weekEl = document.getElementById("context-week");
  const indicatorEl = document.getElementById("context-indicator");
  const childText = childParts.length ? childParts.join(" · ") : t("contextNoChild");
  const metaParts = [
    resolved.zone,
    resolved.week,
    resolved.indicator ? indicatorLabel(resolved.indicator) : ""
  ].filter(Boolean);
  if (childEl) childEl.textContent = childText;
  if (mobileChildEl) mobileChildEl.textContent = childText;
  if (mobileMetaEl) mobileMetaEl.textContent = metaParts.length ? metaParts.join(" · ") : "-";
  if (zoneEl) zoneEl.textContent = resolved.zone || "-";
  if (weekEl) weekEl.textContent = resolved.week || "-";
  if (indicatorEl) indicatorEl.textContent = resolved.indicator ? indicatorLabel(resolved.indicator) : "-";
}

function collectWeeklyPayload() {
  const form = document.getElementById("weekly-form");
  const resolved = resolveZoneWeekIndicator();
  return {
    zone: resolved.zone,
    indicator: resolved.indicator,
    week: resolved.week,
    historical_counts: parseCounts(form.elements.historical_counts.value),
    current_count: numberValue(form, "current_count") || 0,
    source: state.mode === "synthetic_demo" ? "synthetic_demo" : "manual_aggregate_entry",
    operator_initials: document.getElementById("node-settings-form").elements.operator_initials.value.trim()
  };
}

function collectClimatePayload() {
  const form = document.getElementById("climate-form");
  const resolved = resolveZoneWeekIndicator();
  return {
    zone: resolved.zone,
    week: resolved.week,
    rainfall: form.elements.rainfall.value,
    flooding: form.elements.flooding.value,
    heat_alert: form.elements.heat_alert.value,
    water_disruption: form.elements.water_disruption.value,
    vector_risk: form.elements.vector_risk.value,
    source: form.elements.source.value,
    confidence: form.elements.confidence.value,
    notes: form.elements.notes.value.trim(),
    operator_initials: document.getElementById("node-settings-form").elements.operator_initials.value.trim()
  };
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    // FastAPI returns string `detail` for HTTPException (4xx) and an
    // ARRAY of validation-error objects for 422. Without this branch
    // the array gets stringified to "[object Object]" inside the toast.
    const detail = body && body.detail;
    let message;
    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail
        .map((entry) => entry?.msg || JSON.stringify(entry))
        .join("; ") || t("loadError");
    } else {
      message = t("loadError");
    }
    throw new Error(message);
  }
  return response.json();
}

async function loadRuntime() {
  try {
    state.runtime = await api("/api/runtime");
  } catch (_err) {
    state.runtime = {
      mode: "local_clinic",
      public_demo: false,
      synthetic_only: false,
      warning: ""
    };
  }
  applyRuntimeMode();
}

function setStatus(key, mode = null) {
  const status = document.getElementById("assessment-status");
  if (!status) return;
  status.textContent = t(key);
  status.classList.remove("loading", "ok", "error");
  if (mode === "loading") status.classList.add("loading");
  else if (mode === "ok" || mode === true) status.classList.add("ok");
  else if (mode === "error") status.classList.add("error");
}

const TOAST_DEFAULT_TIMEOUT_MS = 3200;
let _toastDismissTimer = null;

function showToast(message, { variant = "ok", iconName, timeoutMs = TOAST_DEFAULT_TIMEOUT_MS } = {}) {
  const region = document.getElementById("toast-region");
  if (!region) return;
  if (_toastDismissTimer) {
    clearTimeout(_toastDismissTimer);
    _toastDismissTimer = null;
  }
  const resolvedIcon = iconName || (variant === "error" ? "alert-triangle" : "check-circle");
  const cls = variant === "error" ? "toast toast-error" : "toast";
  region.innerHTML = `
    <div class="${cls}" role="status">
      ${(window.KynodeIcons && window.KynodeIcons.icon)
        ? window.KynodeIcons.icon(resolvedIcon, { size: 16 })
        : ""}
      <span>${escapeHtml(message)}</span>
    </div>
  `;
  const node = region.firstElementChild;
  if (!node) return;
  const dismiss = () => {
    if (!node.isConnected) return;
    node.classList.add("toast-leaving");
    setTimeout(() => {
      if (node.isConnected) node.remove();
    }, 200);
  };
  _toastDismissTimer = setTimeout(dismiss, timeoutMs);
  node.addEventListener("mouseenter", () => {
    if (_toastDismissTimer) clearTimeout(_toastDismissTimer);
  });
  node.addEventListener("mouseleave", () => {
    _toastDismissTimer = setTimeout(dismiss, timeoutMs / 2);
  });
  // Click anywhere on the toast dismisses it. Useful when the toast
  // happens to overlap content the user wants to read (e.g. the last
  // row of the audit list right after preparing an export).
  node.addEventListener("click", dismiss);
}

function dismissToastIfPresent() {
  if (_toastDismissTimer) {
    clearTimeout(_toastDismissTimer);
    _toastDismissTimer = null;
  }
  const region = document.getElementById("toast-region");
  if (region) region.innerHTML = "";
}

async function withButtonLoading(button, statusKey, fn) {
  if (button) {
    button.classList.add("loading");
    button.disabled = true;
  }
  if (statusKey) setStatus(statusKey, "loading");
  try {
    return await fn();
  } finally {
    if (button) {
      button.classList.remove("loading");
      button.disabled = false;
    }
  }
}

function renderFact(label, value, flag) {
  const chip = flag ? `<span class="chip ${chipClass(flag)}">${escapeHtml(flagLabel(flag))}</span>` : "";
  return `<div class="fact-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>${chip}</div>`;
}

function setResultCardState(cardId, flags = []) {
  const card = document.getElementById(cardId);
  if (!card) return;
  const normalized = flags.filter(Boolean).map(String);
  const isCritical = normalized.some((flag) => flag.includes("critical") || flag === "very_high" || flag === "severely_low");
  const isWarning = normalized.some((flag) => chipClass(flag) === "warning" || chipClass(flag) === "danger");
  card.classList.toggle("result-critical", isCritical);
  card.classList.toggle("result-warning", !isCritical && isWarning);
  const alert = card.querySelector(".result-alert");
  if (alert) alert.innerHTML = isCritical ? inlineIcon("alert-triangle", 15) : "";
}

function renderEmptyAssessment() {
  // Clear individual result panels (kept in DOM so the .has-results
  // toggle on .results-panel can swap CSS visibility cheaply, and so
  // the contract tests that check for these element ids still pass).
  for (const id of ["triage-results", "growth-results", "vaccination-results", "syndrome-preview-results"]) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = "";
  }
  for (const id of ["triage-card", "growth-card", "vaccination-card", "syndrome-card"]) {
    setResultCardState(id, []);
  }
  // Show the unified empty state (one big "run an assessment" message)
  // instead of repeating the same copy in each of the four cards.
  document.querySelector(".results-panel")?.classList.remove("has-results");
}

function renderAssessment(data) {
  state.assessment = data;
  setStatus("computed", true);
  updateContextBar();
  // Reveal the .result-grid and hide the unified empty state. CSS does
  // the swap based on the .has-results class on .results-panel.
  document.querySelector(".results-panel")?.classList.add("has-results");

  const triage = document.getElementById("triage-results");
  triage.innerHTML = Object.entries(data.triage.values)
    .filter(([, value]) => value !== null)
    .map(([key, value]) => {
      const label = I18N[state.lang].vitals[key] || key;
      const range = data.triage.ranges[key];
      const flag = data.triage.flags[key];
      const rangeText = range ? `${range[0]}-${range[1]}` : "";
      return `<div class="metric-row"><span>${escapeHtml(label)}<br><small>${escapeHtml(rangeText)}</small></span><strong>${escapeHtml(value)}</strong><span class="chip ${chipClass(flag)}">${escapeHtml(flagLabel(flag))}</span></div>`;
    })
    .join("");

  document.getElementById("growth-results").innerHTML = [
    renderFact(t("zScore"), data.growth.z_score, data.growth.interpretation),
    renderFact(t("percentile"), `${data.growth.percentile}%`),
    renderFact(t("flag"), flagLabel(data.growth.interpretation))
  ].join("");

  const vaccination = data.vaccinations;
  document.getElementById("vaccination-results").innerHTML = [
    renderFact(t("completed"), vaccination.completed.length),
    renderFact(t("overdue"), vaccination.overdue.length, vaccination.overdue.length ? "abnormal_high" : "normal"),
    renderFact(t("upcoming"), vaccination.upcoming.length)
  ].join("");

  const preview = data.syndrome_indicator_preview;
  document.getElementById("syndrome-preview-results").innerHTML = [
    renderFact(t("zone"), preview.zone),
    renderFact(t("week"), preview.week),
    renderFact(t("indicator"), indicatorLabel(preview.indicator)),
    `<p class="field-help">${escapeHtml(preview.boundary)}</p>`
  ].join("");

  setResultCardState("triage-card", Object.values(data.triage.flags));
  setResultCardState("growth-card", [data.growth.interpretation]);
  setResultCardState("vaccination-card", [vaccination.overdue.length ? "abnormal_high" : "normal"]);
  setResultCardState("syndrome-card", []);
}

function renderWeeklySummary(input) {
  const el = document.getElementById("weekly-summary");
  if (!el) return;
  if (!input) {
    el.innerHTML = "";
    return;
  }
  el.innerHTML = `
    <div><span>${t("zone")}</span><strong>${escapeHtml(input.zone)}</strong></div>
    <div><span>${t("week")}</span><strong>${escapeHtml(input.week)}</strong></div>
    <div><span>${t("count")}</span><strong>${escapeHtml(input.current_count)}</strong></div>
    <div><span>${t("source")}</span><strong>${escapeHtml(sourceLabel(input.source))}</strong></div>
  `;
  updateContextBar();
}

function renderSparkline(signal) {
  const baseline = Array.isArray(signal.historical_counts) ? signal.historical_counts : [];
  const baselineNumbers = baseline.map(Number).filter(Number.isFinite);
  const current = Number(signal.current_count ?? signal.count);
  const values = [...baselineNumbers, current].filter(Number.isFinite);
  if (values.length < 2) return "";
  const width = 420;
  const height = 170;
  const padX = 38;          // wider left pad to fit Y-axis tick labels
  const padY = 22;
  const minValue = Math.min(...values, 0);
  const maxValue = Math.max(...values, 1);
  const spread = Math.max(maxValue - minValue, 1);
  // Mean of the baseline-only window (the threshold the spike is measured
  // against). Drawn as a dashed horizontal line so the reviewer can SEE
  // the gap between baseline and current count instead of only reading it.
  const baselineMean = baselineNumbers.length
    ? baselineNumbers.reduce((sum, value) => sum + value, 0) / baselineNumbers.length
    : minValue;
  const step = (width - padX * 2) / Math.max(values.length - 1, 1);
  const yFor = (value) => height - padY - ((value - minValue) / spread) * (height - padY * 2);
  const points = values.map((value, index) => ({ x: padX + index * step, y: yFor(value), value }));
  const baselinePoints = points.slice(0, -1).map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
  const allPoints = points.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
  const currentPoint = points[points.length - 1];
  const severity = chipClass(signal.flag || "");
  // Three Y-axis ticks: floor of baseline range, baseline mean, ceiling
  // (current OR max baseline, whichever is higher). This gives the reader
  // a scale without crowding the chart.
  const ticks = [Math.round(minValue), Math.round(baselineMean), Math.round(maxValue)]
    .filter((value, index, arr) => arr.indexOf(value) === index);
  const meanLineY = yFor(baselineMean);
  const meanText = baselineMean.toFixed(1);
  const zScore = signal.z_score !== undefined && signal.z_score !== null
    ? Number(signal.z_score).toFixed(2)
    : "—";
  const sourceText = sourceLabel(signal.signal_source || signal.source || "manual_aggregate_entry");
  const zoneText = signal.zone || "";
  return `
    <div class="sparkline-card ${severity}">
      <div class="sparkline-heading">
        <div>
          <span>${t("signalTrend")}</span>
          <strong>${escapeHtml(indicatorLabel(signal.indicator))}</strong>
          ${zoneText ? `<small class="sparkline-zone">${escapeHtml(zoneText)}</small>` : ""}
        </div>
        <span class="chip ${severity}">${escapeHtml(flagLabel(signal.flag || "normal"))}</span>
      </div>
      <svg class="signal-sparkline" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(t("signalTrend"))} ${escapeHtml(zoneText)} ${escapeHtml(current)}">
        ${ticks.map((value) => {
          const y = yFor(value).toFixed(1);
          return `
            <line x1="${padX}" y1="${y}" x2="${width - padX}" y2="${y}" class="sparkline-grid"></line>
            <text x="${padX - 6}" y="${y}" class="sparkline-tick-label" text-anchor="end" dominant-baseline="middle">${value}</text>
          `;
        }).join("")}
        <line x1="${padX}" y1="${meanLineY.toFixed(1)}" x2="${width - padX}" y2="${meanLineY.toFixed(1)}" class="sparkline-mean"></line>
        <text x="${(width - padX).toFixed(1)}" y="${(meanLineY - 4).toFixed(1)}" class="sparkline-mean-label" text-anchor="end">${escapeHtml(t("baseline"))} ø ${escapeHtml(meanText)}</text>
        <line x1="${padX}" y1="${height - padY}" x2="${width - padX}" y2="${height - padY}" class="sparkline-axis"></line>
        <polyline points="${baselinePoints}" class="sparkline-baseline"></polyline>
        <polyline points="${allPoints}" class="sparkline-current"></polyline>
        ${points.map((point, index) => `<circle cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="${index === points.length - 1 ? 5 : 3}" class="${index === points.length - 1 ? "sparkline-dot current" : "sparkline-dot"}"></circle>`).join("")}
        <text x="${currentPoint.x.toFixed(1)}" y="${Math.max(16, currentPoint.y - 10).toFixed(1)}" class="sparkline-label" text-anchor="middle">${escapeHtml(current)}</text>
      </svg>
      <div class="sparkline-meta">
        <span><strong>${t("zScore")}:</strong> ${escapeHtml(zScore)} · <strong>${t("source")}:</strong> ${escapeHtml(sourceText)}</span>
        <span>${t("baselineWeeks")}: ${escapeHtml(baseline.join(", ") || "-")}</span>
        <span>${t("currentCount")}: ${escapeHtml(current)}</span>
      </div>
    </div>
  `;
}

function renderEmptyAggregate() {
  const el = document.getElementById("aggregate-summary");
  if (!el) return;
  el.innerHTML = `
    <div class="empty-state aggregate-empty-state">
      <strong>${escapeHtml(t("aggregateEmptyTitle"))}</strong>
      <span>${escapeHtml(t("aggregateEmptyText"))}</span>
    </div>
  `;
}

function renderAggregate(signal) {
  state.aggregateSignal = signal;
  // Removed the four ZONE/COUNT/Z-SCORE/SOURCE stat cards that used to
  // sit below the sparkline — the sparkline-card heading + meta already
  // surface zone, indicator, count, baseline and severity. Keeping both
  // produced visual triplication with the weekly-summary at the bottom
  // of the form. The sparkline is now the single source of truth for
  // signal status in the surveillance view.
  document.getElementById("aggregate-summary").innerHTML = renderSparkline(signal);
}

function renderPrivacyChecklist(exported) {
  state.lastExport = exported;
  const el = document.getElementById("privacy-checklist");
  if (!el) return;
  const checks = Object.entries(exported.privacy_checklist || {})
    .map(([key, value]) => `
      <li class="${value ? "ok" : "danger"}">
        <span>${escapeHtml(mappedLabel("privacyLabels", key))}</span>
        <strong>${escapeHtml(value ? t("privacyPass") : t("privacyNeedsReview"))}</strong>
      </li>
    `)
    .join("");
  const warnings = (exported.quality_warnings || [])
    .map((warning) => `<span class="chip warning">${escapeHtml(mappedLabel("qualityWarningLabels", warning))}</span>`)
    .join("");
  el.innerHTML = `
    <h3>${t("privacyChecklist")}</h3>
    <ul>${checks}</ul>
    <h3>${t("qualityWarnings")}</h3>
    <div class="chip-list">${warnings || `<span class="chip ok">${t("none")}</span>`}</div>
    <p class="export-ready-note">${inlineIcon("shield-check", 16)} ${escapeHtml(t("exportReadyToShare"))}</p>
  `;
}

function buildVaccineGrid() {
  const grid = document.getElementById("vaccine-grid");
  const checked = new Set([...grid.querySelectorAll("input:checked")].map((input) => input.value));
  grid.innerHTML = Object.entries(DOSE_MONTHS).map(([id, month]) => `
    <label class="vaccine-option">
      <input type="checkbox" value="${id}" data-month="${month}" ${checked.has(id) ? "checked" : ""} />
      <span>${escapeHtml(doseLabel(id))}</span>
    </label>
  `).join("");
  grid.onchange = updateVaccineCount;
  updateVaccineCount();
}

function updateVaccineCount() {
  const badge = document.getElementById("vaccine-count");
  if (!badge) return;
  const checked = document.querySelectorAll(".vaccine-option input:checked").length;
  const total = Object.keys(DOSE_MONTHS).length;
  badge.textContent = `${checked} / ${total}`;
}

function fillFromSynthetic(data) {
  const form = document.getElementById("case-form");
  const child = data.child;
  form.elements.local_child_id.value = child.local_child_id;
  form.elements.birth_date.value = child.birth_date;
  form.elements.sex.value = child.sex;
  form.elements.zone.value = child.zone;
  form.elements.week.value = data.week;
  form.elements.syndrome_indicator.value = data.weekly_signal_input.indicator;
  form.elements.context.value = t("syntheticClinicalContext");
  form.elements.weight_kg.value = data.weight_kg;
  form.elements.heart_rate.value = data.vitals.heart_rate;
  form.elements.respiratory_rate.value = data.vitals.respiratory_rate;
  form.elements.temperature_c.value = data.vitals.temperature_c;
  form.elements.spo2.value = data.vitals.spo2;
  document.querySelectorAll(".vaccine-option input").forEach((input) => {
    input.checked = ["BCG", "hepB_birth", "pentavalent_1", "polio_1", "rotavirus_1", "pcv_1", "pentavalent_2"].includes(input.value);
  });
  updateVaccineCount();

  const weeklyForm = document.getElementById("weekly-form");
  weeklyForm.elements.zone.value = child.zone;
  weeklyForm.elements.week.value = data.week;
  weeklyForm.elements.indicator.value = data.weekly_signal_input.indicator;
  weeklyForm.elements.current_count.value = data.weekly_signal_input.current_count;
  weeklyForm.elements.historical_counts.value = data.weekly_signal_input.historical_counts.join(", ");
  renderWeeklySummary({ ...data.weekly_signal_input, zone: child.zone, week: data.week });

  const climateForm = document.getElementById("climate-form");
  Object.entries(data.climate_context).forEach(([key, value]) => {
    if (climateForm.elements[key]) climateForm.elements[key].value = value;
  });
  updateContextBar();
}

function clearForms() {
  document.getElementById("case-form").reset();
  document.getElementById("weekly-form").reset();
  document.getElementById("climate-form").reset();
  document.querySelector("#case-form [name='week']").value = currentIsoWeek();
  document.querySelector("#weekly-form [name='week']").value = currentIsoWeek();
  document.querySelectorAll(".vaccine-option input").forEach((input) => {
    input.checked = false;
  });
  updateVaccineCount();
  state.assessment = null;
  state.aggregateSignal = null;
  state.lastExport = null;
  setStatus("waiting");
  renderEmptyAssessment();
  renderWeeklySummary(null);
  renderEmptyAggregate();
  document.getElementById("privacy-checklist").innerHTML = "";
  document.getElementById("export-output").textContent = "{}";
  setExportActionsEnabled(false);
  updateContextBar();
}

async function loadNodeSettings() {
  const data = await api("/api/node-settings");
  const form = document.getElementById("node-settings-form");
  form.elements.clinic_name.value = data.clinic_name;
  form.elements.node_label.value = data.node_label;
  form.elements.country.value = data.country;
  // Mirror the node label into the hero status card so the home view
  // shows live identity instead of decorative copy alone.
  const heroNode = document.getElementById("hero-node-label");
  if (heroNode) heroNode.textContent = data.node_label || "—";
}

function updateHeroLastActivity(items) {
  const target = document.getElementById("hero-last-activity");
  if (!target) return;
  const newest = Array.isArray(items) ? items[0] : null;
  target.textContent = newest ? formatTimestamp(newest.timestamp) : t("heroNoActivity");
}

async function saveNodeSettings(event) {
  event.preventDefault();
  if (isPublicDemo()) {
    showToast(t("syntheticControlled"));
    return;
  }
  const form = document.getElementById("node-settings-form");
  const button = document.getElementById("save-node-settings");
  try {
    await withButtonLoading(button, null, async () => {
      await api("/api/node-settings", {
        method: "PUT",
        body: JSON.stringify({
          clinic_name: form.elements.clinic_name.value.trim(),
          node_label: form.elements.node_label.value.trim(),
          country: form.elements.country.value.trim().toUpperCase(),
          operator_initials: form.elements.operator_initials.value.trim()
        })
      });
      showToast(t("savedNode"));
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("loadError"), { variant: "error" });
  }
}

async function runAssessment(event) {
  if (event && typeof event.preventDefault === "function") event.preventDefault();
  const form = document.getElementById("case-form");
  if (!isPublicDemo() && !form.reportValidity()) return null;
  const button = document.getElementById("run-assessment");
  try {
    return await withButtonLoading(button, "computed", async () => {
      const result = isPublicDemo()
        ? await api("/api/demo/assessment", { method: "POST" })
        : await api("/api/assessments", {
            method: "POST",
            body: JSON.stringify(collectAssessmentPayload())
          });
      renderAssessment(result);
      setStatus("computed", "ok");
      return result;
    });
  } catch (err) {
    setStatus("loadError", "error");
    showToast(err.message || t("loadError"), { variant: "error" });
    return null;
  }
}

async function saveEncounter() {
  const form = document.getElementById("case-form");
  if (!isPublicDemo() && !form.reportValidity()) return;
  const button = document.getElementById("save-encounter");
  try {
    await withButtonLoading(button, "saved", async () => {
      const data = isPublicDemo()
        ? await api("/api/demo/encounter", { method: "POST" })
        : await api("/api/encounters", {
            method: "POST",
            body: JSON.stringify(collectAssessmentPayload())
          });
      renderAssessment(data.assessment);
      setStatus("saved", "ok");
      showToast(t("saved"));
      await Promise.all([loadEncounters(), loadAuditEvents()]);
    });
  } catch (err) {
    setStatus("loadError", "error");
    showToast(err.message || t("loadError"), { variant: "error" });
  }
}

async function saveWeeklyInput(event) {
  event.preventDefault();
  if (isPublicDemo()) {
    showToast(t("syntheticControlled"));
    return;
  }
  const form = document.getElementById("weekly-form");
  if (!form.reportValidity()) return;
  const button = document.getElementById("save-weekly-input");
  try {
    await withButtonLoading(button, null, async () => {
      const data = await api("/api/weekly-inputs", {
        method: "PUT",
        body: JSON.stringify(collectWeeklyPayload())
      });
      renderWeeklySummary(data);
      state.aggregateSignal = null;
      state.lastExport = null;
      renderEmptyAggregate();
      document.getElementById("privacy-checklist").innerHTML = "";
      document.getElementById("export-output").textContent = "{}";
      setExportActionsEnabled(false);
      showToast(t("savedWeekly"));
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("loadError"), { variant: "error" });
  }
}

async function saveClimateContext(event) {
  event.preventDefault();
  if (isPublicDemo()) {
    showToast(t("syntheticControlled"));
    return;
  }
  const form = document.getElementById("climate-form");
  if (!form.reportValidity()) return;
  const button = document.getElementById("save-climate-context");
  try {
    await withButtonLoading(button, null, async () => {
      await api("/api/climate-context", {
        method: "PUT",
        body: JSON.stringify(collectClimatePayload())
      });
      showToast(t("savedClimate"));
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("loadError"), { variant: "error" });
  }
}

async function loadEncounters() {
  const list = document.getElementById("encounter-history");
  if (!list) return;
  try {
    const data = await api("/api/encounters");
    if (!data.items.length) {
      list.innerHTML = `
        <div class="empty-state">
          <span>${t("emptyEncounters")}</span>
          <a class="empty-action" href="#home">${t("goToHome")}</a>
        </div>
      `;
      return;
    }
    list.innerHTML = data.items.map((item) => `
      <div class="history-row">
        <div>
          <strong>${escapeHtml(item.local_child_id)}</strong>
          <small>${escapeHtml(item.zone)} · ${escapeHtml(item.week)} · ${escapeHtml(indicatorLabel(item.indicator))}</small>
          <small>${escapeHtml(formatTimestamp(item.created_at))}</small>
        </div>
        <span class="chip ${chipClass(item.growth_flag)}">${escapeHtml(flagLabel(item.growth_flag))}</span>
      </div>
    `).join("");
  } catch (err) {
    list.innerHTML = `<div class="error-state"><span>${escapeHtml(err.message || t("loadError"))}</span></div>`;
  }
}

async function loadAuditEvents() {
  const list = document.getElementById("audit-events");
  if (!list) return;
  try {
    const data = await api("/api/audit-events?limit=25");
    updateHeroLastActivity(data.items);
    if (!data.items.length) {
      list.innerHTML = `<div class="empty-state"><span>${t("emptyAudit")}</span></div>`;
      return;
    }
    const visibleItems = state.auditExpanded ? data.items : data.items.slice(0, 5);
    const rows = visibleItems.map((item) => {
      const sourceFull = sourceLabel(item.source);
      const entityKindText = entityKindLabel(item.entity_kind);
      const entityKeyText = entityKeyLabel(item.entity_key);
      const entityText = entityKeyText && entityKeyText !== entityKindText
        ? `${entityKindText} · ${entityKeyText}`
        : entityKindText;
      // The chip is truncated to 110px on mobile (see .history-row .chip).
      // Set `title` so the full label is reachable via long-press / hover
      // when the visible text is clipped to ellipsis.
      return `
        <div class="history-row audit-row">
          <div>
            <strong>${escapeHtml(mappedLabel("auditEventLabels", item.event_type))}</strong>
            <small>${escapeHtml(entityText)}</small>
            <small>${escapeHtml(formatTimestamp(item.timestamp))}</small>
          </div>
          <span class="chip ${item.source === "synthetic_demo" ? "warning" : "ok"}" title="${escapeHtml(sourceFull)}">${escapeHtml(sourceFull)}</span>
        </div>
      `;
    }).join("");
    const toggle = data.items.length > 5
      ? `<button id="toggle-audit-events" class="secondary audit-toggle" type="button">${state.auditExpanded ? t("showFewerEvents") : t("viewAllEvents")}</button>`
      : "";
    list.innerHTML = `${rows}${toggle}`;
  } catch (err) {
    list.innerHTML = `<div class="error-state"><span>${escapeHtml(err.message || t("loadError"))}</span></div>`;
  }
}

async function generateSignal() {
  const button = document.getElementById("generate-signal");
  try {
    await withButtonLoading(button, null, async () => {
      const payload = collectWeeklyPayload();
      const params = new URLSearchParams({
        zone: payload.zone,
        indicator: payload.indicator,
        week: payload.week
      });
      const signal = await api(`/api/signals/weekly?${params.toString()}`);
      renderAggregate(signal);
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("noExportReady"), { variant: "error" });
  }
}

async function exportJson() {
  const button = document.getElementById("export-json");
  try {
    await withButtonLoading(button, null, async () => {
      const payload = collectWeeklyPayload();
      const params = new URLSearchParams({
        zone: payload.zone,
        indicator: payload.indicator,
        week: payload.week
      });
      const signal = await api(`/api/signals/weekly?${params.toString()}`);
      const exported = await api(`/api/export/weekly?${params.toString()}`);
      renderAggregate({
        ...signal,
        ...exported,
        historical_counts: signal.historical_counts,
        current_count: signal.current_count ?? exported.count
      });
      renderPrivacyChecklist(exported);
      document.getElementById("export-output").textContent = JSON.stringify(exported, null, 2);
      setExportActionsEnabled(true);
      showToast(t("exportSafe"), { iconName: "download" });
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("noExportReady"), { variant: "error" });
  }
}

function renderBrief(brief) {
  const empty = document.getElementById("brief-empty");
  const output = document.getElementById("brief-output");
  if (!output) return;
  if (empty) empty.classList.add("hidden");
  output.classList.remove("hidden");
  const generatorLabel = brief.generator === "llm_brief_v1"
    ? t("briefGeneratorLLM")
    : t("briefGeneratorOffline");
  const operationalItems = (brief.operational_considerations || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const limitItems = (brief.data_quality_limits || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  output.innerHTML = `
    <header class="brief-header">
      <h3>${escapeHtml(brief.headline)}</h3>
      <span class="brief-generator chip ok" title="${escapeHtml(generatorLabel)}">
        ${inlineIcon("sparkles", 14)}
        <span>${escapeHtml(generatorLabel)}</span>
      </span>
    </header>
    <section class="brief-section">
      <h4>${t("briefWhatChanged")}</h4>
      <p>${escapeHtml(brief.what_changed)}</p>
    </section>
    <section class="brief-section">
      <h4>${t("briefWhyReview")}</h4>
      <p>${escapeHtml(brief.why_review_needed)}</p>
    </section>
    <section class="brief-section">
      <h4>${t("briefOperational")}</h4>
      <ul>${operationalItems}</ul>
    </section>
    <section class="brief-section">
      <h4>${t("briefDataLimits")}</h4>
      <ul>${limitItems}</ul>
    </section>
    <section class="brief-section">
      <h4>${t("briefEscalation")}</h4>
      <p>${escapeHtml(brief.escalation_recommendation)}</p>
    </section>
    <footer class="brief-disclaimer">
      ${inlineIcon("shield-check", 14)}
      <span>${escapeHtml(brief.disclaimer)}</span>
    </footer>
  `;
}

async function generateBriefRequest() {
  const button = document.getElementById("generate-brief");
  if (!button) return;
  try {
    await withButtonLoading(button, null, async () => {
      const payload = collectWeeklyPayload();
      const params = new URLSearchParams({
        zone: payload.zone,
        indicator: payload.indicator,
        week: payload.week,
        lang: state.lang
      });
      const response = await api(`/api/brief/generate?${params.toString()}`, {
        method: "POST"
      });
      renderBrief(response.brief);
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("briefRequiresExport"), { variant: "error" });
  }
}

async function copyExportJson() {
  const output = document.getElementById("export-output");
  const text = output?.textContent || "{}";
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    showToast(t("copiedJson"), { iconName: "copy" });
  } catch (_err) {
    showToast(t("loadError"), { variant: "error" });
  }
}

function downloadExportJson() {
  const output = document.getElementById("export-output");
  const text = output?.textContent || "{}";
  const payload = collectWeeklyPayload();
  const safeZone = (payload.zone || "zone").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const filename = `kynode-pediatric-weekly-aggregate-${safeZone}-${payload.week || "week"}-${payload.indicator || "indicator"}.json`;
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast(t("downloadedJson"), { iconName: "download" });
}

async function loadSyntheticWalkthrough() {
  const button = document.getElementById("load-synthetic");
  try {
    await withButtonLoading(button, null, async () => {
      const data = await api("/api/demo/load", { method: "POST" });
      state.mode = "synthetic_demo";
      fillFromSynthetic(data);
      state.lastExport = null;
      document.getElementById("privacy-checklist").innerHTML = "";
      document.getElementById("export-output").textContent = "{}";
      setExportActionsEnabled(false);
      renderMode();
      await runAssessment();
      showToast(t("syntheticLoaded"));
      await loadAuditEvents();
    });
  } catch (err) {
    showToast(err.message || t("loadError"), { variant: "error" });
  }
}

async function clearSyntheticWalkthrough() {
  const button = document.getElementById("clear-synthetic");
  try {
    await withButtonLoading(button, null, async () => {
      await api("/api/demo/clear", { method: "POST" });
      state.mode = "clinic";
      clearForms();
      renderMode();
      showToast(t("syntheticCleared"));
      await Promise.all([loadEncounters(), loadAuditEvents()]);
    });
  } catch (err) {
    showToast(err.message || t("loadError"), { variant: "error" });
  }
}

document.querySelectorAll(".lang").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});
document.getElementById("node-settings-form").addEventListener("submit", saveNodeSettings);
document.getElementById("case-form").addEventListener("submit", runAssessment);
document.getElementById("load-synthetic").addEventListener("click", loadSyntheticWalkthrough);
document.getElementById("clear-synthetic").addEventListener("click", clearSyntheticWalkthrough);
document.getElementById("save-encounter").addEventListener("click", saveEncounter);
document.getElementById("weekly-form").addEventListener("submit", saveWeeklyInput);
document.getElementById("climate-form").addEventListener("submit", saveClimateContext);
document.getElementById("generate-signal").addEventListener("click", generateSignal);
document.getElementById("export-json").addEventListener("click", exportJson);
document.getElementById("copy-export").addEventListener("click", copyExportJson);
document.getElementById("generate-brief")?.addEventListener("click", generateBriefRequest);
document.getElementById("download-export").addEventListener("click", downloadExportJson);
document.getElementById("audit-events")?.addEventListener("click", (event) => {
  if (!event.target.closest("#toggle-audit-events")) return;
  state.auditExpanded = !state.auditExpanded;
  loadAuditEvents();
});
document.getElementById("open-config").addEventListener("click", () => {
  window.location.hash = "configuration";
});
document.getElementById("theme-toggle-config").addEventListener("click", () => {
  document.getElementById("theme-toggle").click();
});
window.addEventListener("hashchange", () => showView(viewFromHash()));

for (const formId of ["case-form", "weekly-form"]) {
  const form = document.getElementById(formId);
  form?.addEventListener("input", updateContextBar);
  form?.addEventListener("change", updateContextBar);
}

const mobileNavToggle = document.getElementById("mobile-nav-toggle");
const mobileNavBackdrop = document.getElementById("mobile-nav-backdrop");
const appFrame = document.querySelector(".app-frame");

function setMobileNav(open) {
  if (!appFrame) return;
  const wasOpen = appFrame.getAttribute("data-mobile-nav") === "open";
  const nextState = open ? "open" : "closed";
  appFrame.setAttribute("data-mobile-nav", nextState);
  if (mobileNavToggle) {
    mobileNavToggle.setAttribute("aria-expanded", String(open));
    mobileNavToggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  }
  if (mobileNavBackdrop) mobileNavBackdrop.setAttribute("aria-hidden", String(!open));
  document.body.style.overflow = open ? "hidden" : "";
  if (open) {
    const firstLink = document.querySelector("#sidebar a.sidebar-link");
    if (firstLink && typeof firstLink.focus === "function") {
      requestAnimationFrame(() => firstLink.focus({ preventScroll: true }));
    }
  } else if (wasOpen && mobileNavToggle && typeof mobileNavToggle.focus === "function") {
    mobileNavToggle.focus({ preventScroll: true });
  }
}

document.addEventListener("keydown", (event) => {
  if (event.key !== "Tab") return;
  if (appFrame?.getAttribute("data-mobile-nav") !== "open") return;
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;
  const focusables = sidebar.querySelectorAll(
    'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );
  if (!focusables.length) return;
  const first = focusables[0];
  const last = focusables[focusables.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});

if (mobileNavToggle) {
  mobileNavToggle.addEventListener("click", () => {
    const isOpen = appFrame?.getAttribute("data-mobile-nav") === "open";
    setMobileNav(!isOpen);
  });
}

if (mobileNavBackdrop) {
  mobileNavBackdrop.addEventListener("click", () => setMobileNav(false));
}

document.getElementById("sidebar")?.addEventListener("click", (event) => {
  if (event.target.closest(".sidebar-link")) setMobileNav(false);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && appFrame?.getAttribute("data-mobile-nav") === "open") {
    setMobileNav(false);
  }
});

window.addEventListener("resize", () => {
  renderMode();
  if (window.innerWidth > 980 && appFrame?.getAttribute("data-mobile-nav") === "open") {
    setMobileNav(false);
  }
});

const THEME_STORAGE_KEY = "kynode-pediatric-theme";
const themeToggle = document.getElementById("theme-toggle");
if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch (_err) {
      /* Ignore storage failures. */
    }
  });
}

if (typeof window !== "undefined" && window.KynodeIcons) {
  window.KynodeIcons.hydrateIcons();
}

async function bootstrap() {
  buildVaccineGrid();
  await loadRuntime();
  setLanguage(state.lang);
  renderMode();
  renderEmptyAssessment();
  renderEmptyAggregate();
  const week = currentIsoWeek();
  document.getElementById("current-week-pill").textContent = week;
  document.querySelector("#case-form [name='week']").value = week;
  document.querySelector("#weekly-form [name='week']").value = week;
  setExportActionsEnabled(false);
  updateContextBar();
  showView(viewFromHash());
  await Promise.allSettled([
    loadNodeSettings(),
    loadEncounters(),
    loadAuditEvents()
  ]);
  if (isPublicDemo()) {
    await loadSyntheticWalkthrough();
  }
}

bootstrap();
