const {test} = require('node:test');
const assert = require('node:assert/strict');
const {tituloDe, textoDe, recortar, editorialDe} = require('../api/instagram-latest.js')._internals;

test('el titulo respeta el primer renglon sin sumar creditos', () => {
  assert.equal(tituloDe('.\nOficinas IOL\nConcept Design\nEquipo de proyecto'), 'Oficinas IOL');
});
test('el resumen no corta palabras ni repite el titulo', () => {
  assert.equal(textoDe('Oficinas IOL\nNueva obra en Palermo.', 'Oficinas IOL'), 'Nueva obra en Palermo.');
  assert.equal(recortar('Una nueva arquitectura para trabajar', 20), 'Una nueva…');
});
test('el ajuste editorial corresponde solo al post de IOL', () => {
  const nota = editorialDe('https://www.instagram.com/p/Dc1ktAKlFQy/?utm_source=test');
  assert.ok(nota.image.endsWith('instagram-iol-20260904.jpg'));
  assert.ok(nota.titleEn && nota.textEn);
  assert.equal(editorialDe('https://www.instagram.com/p/OTRA/'), null);
});
