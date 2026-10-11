/**
 * DomoVida · HU-12 · Crea el formulario SUS en Google Forms (texto de 02_cuestionario_sus.md).
 *
 * Uso (una sola vez):
 *   1. Con la cuenta del proyecto DomoVida, en una ventana de incógnito, abrir https://script.google.com y crear un "Proyecto nuevo".
 *   2. Borrar el contenido, pegar este archivo completo y guardar (Ctrl + S).
 *   3. Elegir la función crearFormularioSUS y pulsar "Ejecutar". Autorizar los permisos que pida.
 *   4. En "Registro de ejecución" aparecen 3 enlaces: editar, responder y planilla de respuestas.
 *
 * No recoge correos ni nombres: la encuesta es anónima (Ley N° 21.719).
 */
function crearFormularioSUS() {
  var form = FormApp.create('DomoVida · Evaluación de usabilidad (SUS)');
  form.setDescription(
    'Esta encuesta es parte del proyecto de título DomoVida (Ingeniería en Informática, Duoc UC). ' +
    'Su participación es voluntaria y anónima: no se le pedirá su nombre, RUT ni datos de contacto, ' +
    'y puede retirarse en cualquier momento. Las respuestas se usan solo para evaluar el sistema.'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false); // true obligaría a iniciar sesión en Google
  // En cuentas institucionales (ej. duocuc.cl) el formulario nace restringido al dominio:
  // se abre para que cuidadores externos respondan sin iniciar sesión.
  try { form.setRequireLogin(false); } catch (e) { Logger.log('Aviso: no se pudo abrir a usuarios externos: ' + e); }
  form.setProgressBar(true);
  form.setShuffleQuestions(false);
  form.setConfirmationMessage('¡Muchas gracias por su tiempo! Sus respuestas ayudan a mejorar DomoVida.');

  // ---------- Sección 1 · Consentimiento ----------
  var consentimiento = form.addMultipleChoiceItem()
    .setTitle('¿Acepta participar en esta evaluación?')
    .setRequired(true);

  // ---------- Sección 2 · Datos generales ----------
  var seccion2 = form.addPageBreakItem()
    .setTitle('Datos generales')
    .setHelpText('Sin datos personales. Solo se usan para describir al grupo de participantes.');

  form.addTextItem()
    .setTitle('Código de participante (lo entrega el facilitador)')
    .setHelpText('Ejemplo: P01')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .requireTextMatchesPattern('^[Pp][0-9]{2}$')
      .setHelpText('Use el formato P01, P02…')
      .build());

  form.addMultipleChoiceItem()
    .setTitle('Rango de edad')
    .setChoiceValues(['18–29', '30–44', '45–59', '60 o más'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Tipo de cuidador')
    .setChoiceValues(['Familiar', 'Profesional (técnico/a, enfermero/a u otro)', 'Ex cuidador/a'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿Con qué frecuencia usa aplicaciones en el celular o computador?')
    .setChoiceValues(['Diaria', 'Semanal', 'Pocas veces'])
    .setRequired(true);

  // Consentimiento: "Sí" continúa, "No" envía y termina
  consentimiento.setChoices([
    consentimiento.createChoice('Sí, acepto participar', seccion2),
    consentimiento.createChoice('No acepto', FormApp.PageNavigationType.SUBMIT)
  ]);

  // ---------- Sección 3 · Escala SUS (Brooke, 1996) ----------
  form.addPageBreakItem()
    .setTitle('Su experiencia con el panel DomoVida')
    .setHelpText('Marque de 1 a 5 cuánto está de acuerdo con cada frase. No hay respuestas correctas ni incorrectas.');

  var preguntas = [
    'Creo que me gustaría usar este sistema con frecuencia.',
    'Encontré el sistema innecesariamente complejo.',
    'Pensé que el sistema era fácil de usar.',
    'Creo que necesitaría el apoyo de una persona con conocimientos técnicos para poder usar este sistema.',
    'Encontré que las distintas funciones del sistema estaban bien integradas.',
    'Pensé que había demasiada inconsistencia en este sistema.',
    'Imagino que la mayoría de las personas aprendería a usar este sistema muy rápidamente.',
    'Encontré el sistema muy engorroso de usar.',
    'Me sentí muy seguro/a usando el sistema.',
    'Necesité aprender muchas cosas antes de poder empezar a usar este sistema.'
  ];
  preguntas.forEach(function (texto, i) {
    form.addScaleItem()
      .setTitle((i + 1) + '. ' + texto)
      .setBounds(1, 5)
      .setLabels('Totalmente en desacuerdo', 'Totalmente de acuerdo')
      .setRequired(true);
  });

  // ---------- Sección 4 · Comentarios (opcional) ----------
  form.addPageBreakItem().setTitle('Comentarios (opcional)');
  form.addParagraphTextItem().setTitle('¿Qué fue lo más fácil de usar?');
  form.addParagraphTextItem().setTitle('¿Qué cambiaría o mejoraría?');

  // Planilla de respuestas (para copiar luego a 03_resultados_sus.xlsx)
  var hoja = SpreadsheetApp.create('DomoVida · Respuestas SUS');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());

  Logger.log('Editar el formulario:   ' + form.getEditUrl());
  Logger.log('Enlace para responder:  ' + form.getPublishedUrl());
  Logger.log('Planilla de respuestas: ' + hoja.getUrl());
}
