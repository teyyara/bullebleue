'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function createElement() {
  const listeners = {};
  const attributes = {};
  const classes = new Set();
  return {
    listeners,
    attributes,
    textContent: '',
    addEventListener(name, callback) { (listeners[name] ||= []).push(callback); },
    dispatch(name, event = {}) { for (const callback of listeners[name] || []) callback(event); },
    setAttribute(name, value) { attributes[name] = value; },
    getAttribute(name) { return attributes[name] ?? null; },
    focus() { this.focusCount = (this.focusCount || 0) + 1; },
    contains(target) { return target === this || (this.children || []).includes(target); },
    classList: {
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
      toggle(name, force) {
        const shouldAdd = force === undefined ? !classes.has(name) : Boolean(force);
        if (shouldAdd) classes.add(name); else classes.delete(name);
        return shouldAdd;
      },
      contains(name) { return classes.has(name); }
    }
  };
}

const toggle = createElement();
toggle.setAttribute('aria-expanded', 'false');
toggle.setAttribute('aria-label', 'Ouvrir le menu');
const navigation = createElement();
const link = createElement();
navigation.children = [link];
navigation.querySelectorAll = () => [link];
const year = createElement();
const documentListeners = {};
const document = {
  querySelector(selector) {
    if (selector === '.menu-toggle') return toggle;
    if (selector === '#navigation') return navigation;
    if (selector === '#year') return year;
    return null;
  },
  addEventListener(name, callback) { (documentListeners[name] ||= []).push(callback); },
  dispatch(name, event = {}) { for (const callback of documentListeners[name] || []) callback(event); }
};

const source = fs.readFileSync(path.join(__dirname, '..', 'script.js'), 'utf8');
vm.runInNewContext(source, { document, Date });
const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';

// Escape while closed must not steal focus (desktop and idle keyboard use).
document.dispatch('keydown', { key: 'Escape' });
assert.equal(isOpen(), false);
assert.equal(toggle.focusCount || 0, 0, 'closed-menu Escape must not focus hidden menu toggle');

// Open then Escape closes the menu and restores focus to its trigger.
toggle.dispatch('click');
assert.equal(isOpen(), true);
assert.equal(toggle.getAttribute('aria-label'), 'Fermer le menu');
assert.equal(navigation.classList.contains('is-open'), true);
document.dispatch('keydown', { key: 'Escape' });
assert.equal(isOpen(), false);
assert.equal(toggle.getAttribute('aria-label'), 'Ouvrir le menu');
assert.equal(navigation.classList.contains('is-open'), false);
assert.equal(toggle.focusCount, 1, 'open-menu Escape restores trigger focus once');

// Repeated Escape after closing must not repeatedly steal focus.
document.dispatch('keydown', { key: 'Escape' });
assert.equal(toggle.focusCount, 1);

// Selecting a navigation link closes the menu without moving focus unexpectedly.
toggle.dispatch('click');
link.dispatch('click');
assert.equal(isOpen(), false);
assert.equal(toggle.focusCount, 1);

// Clicking outside closes an open menu without forcing focus to the trigger.
toggle.dispatch('click');
const outside = createElement();
document.dispatch('click', { target: outside });
assert.equal(isOpen(), false);
assert.equal(toggle.focusCount, 1);

console.log('PASS: closed Escape is inert; open Escape closes/restores focus; nav selection and outside click close safely.');
