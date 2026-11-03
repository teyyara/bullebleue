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
    listeners, attributes, textContent: '',
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

function boot({ reducedMotion = false, revealCount = 2, storyCount = 3 } = {}) {
  const toggle = createElement();
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'Ouvrir le menu');
  const navigation = createElement();
  const link = createElement();
  navigation.children = [link];
  navigation.querySelectorAll = () => [link];
  const year = createElement();
  const revealItems = Array.from({ length: revealCount }, createElement);
  const storySteps = Array.from({ length: storyCount }, createElement);
  const documentListeners = {};
  const observers = [];

  class MockIntersectionObserver {
    constructor(callback, options) {
      this.callback = callback;
      this.options = options;
      this.observed = [];
      this.unobserved = [];
      observers.push(this);
    }
    observe(target) { this.observed.push(target); }
    unobserve(target) { this.unobserved.push(target); }
  }

  const document = {
    documentElement: createElement(),
    querySelector(selector) {
      if (selector === '.menu-toggle') return toggle;
      if (selector === '#navigation') return navigation;
      if (selector === '#year') return year;
      return null;
    },
    querySelectorAll(selector) {
      if (selector === '.reveal') return revealItems;
      if (selector === '.story-step') return storySteps;
      return [];
    },
    addEventListener(name, callback) { (documentListeners[name] ||= []).push(callback); },
    dispatch(name, event = {}) { for (const callback of documentListeners[name] || []) callback(event); }
  };
  const window = {
    matchMedia() { return { matches: reducedMotion }; },
    IntersectionObserver: MockIntersectionObserver
  };
  const source = fs.readFileSync(path.join(__dirname, '..', 'script.js'), 'utf8');
  vm.runInNewContext(source, { document, Date, window, IntersectionObserver: MockIntersectionObserver });
  return { toggle, navigation, link, year, document, revealItems, storySteps, observers };
}

const env = boot();
const { toggle, navigation, link, document } = env;
const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';

// Keyboard and mobile navigation behavior.
document.dispatch('keydown', { key: 'Escape' });
assert.equal(isOpen(), false);
assert.equal(toggle.focusCount || 0, 0, 'closed-menu Escape must not focus hidden menu toggle');

toggle.dispatch('click');
assert.equal(isOpen(), true);
assert.equal(toggle.getAttribute('aria-label'), 'Fermer le menu');
assert.equal(navigation.classList.contains('is-open'), true);
document.dispatch('keydown', { key: 'Escape' });
assert.equal(isOpen(), false);
assert.equal(toggle.getAttribute('aria-label'), 'Ouvrir le menu');
assert.equal(navigation.classList.contains('is-open'), false);
assert.equal(toggle.focusCount, 1, 'open-menu Escape restores trigger focus once');

document.dispatch('keydown', { key: 'Escape' });
assert.equal(toggle.focusCount, 1);

toggle.dispatch('click');
link.dispatch('click');
assert.equal(isOpen(), false);
assert.equal(toggle.focusCount, 1);

toggle.dispatch('click');
document.dispatch('click', { target: createElement() });
assert.equal(isOpen(), false);
assert.equal(toggle.focusCount, 1);

// Existing progressive reveal behavior.
assert.equal(env.observers.length, 2, 'reveal and sticky-story observers are both installed');
assert.equal(env.document.documentElement.classList.contains('has-reveal'), true);
assert.equal(env.observers[0].observed.length, env.revealItems.length);
env.observers[0].callback(env.revealItems.map(target => ({ isIntersecting: true, target })), env.observers[0]);
assert.ok(env.revealItems.every(item => item.classList.contains('is-visible')));
assert.equal(env.observers[0].unobserved.length, env.revealItems.length);

// Sticky homepage keeps a single active text step as the same illustration remains in place.
assert.equal(env.document.documentElement.classList.contains('has-scroll-story'), true);
assert.equal(env.storySteps[0].classList.contains('is-current'), true, 'opening chapter is visible before the first observer callback');
assert.equal(env.observers[1].observed.length, env.storySteps.length);
env.observers[1].callback([
  { target: env.storySteps[0], isIntersecting: true, intersectionRatio: 0.55 },
  { target: env.storySteps[1], isIntersecting: false, intersectionRatio: 0 },
  { target: env.storySteps[2], isIntersecting: false, intersectionRatio: 0 }
], env.observers[1]);
assert.equal(env.storySteps[0].classList.contains('is-current'), true);
env.observers[1].callback([
  { target: env.storySteps[0], isIntersecting: false, intersectionRatio: 0 },
  { target: env.storySteps[1], isIntersecting: true, intersectionRatio: 0.62 }
], env.observers[1]);
assert.equal(env.storySteps[0].classList.contains('is-current'), false);
assert.equal(env.storySteps[1].classList.contains('is-current'), true);

// Reduced-motion visitors receive all story copy without reveal observers.
const reduced = boot({ reducedMotion: true });
assert.equal(reduced.document.documentElement.classList.contains('has-reveal'), false);
assert.equal(reduced.document.documentElement.classList.contains('has-scroll-story'), false);
assert.equal(reduced.observers.length, 0);

console.log('PASS: menu keyboard/outside-click behavior; progressive reveals; sticky-story transitions; reduced-motion fallback.');
