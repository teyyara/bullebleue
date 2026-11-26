// SPDX-License-Identifier: MIT
// What Kyutai's Pocket TTS needs besides ONNX Runtime (D455): its text, prepared and cut into chunks as
// pocket-tts 4.0.0 does (models/text_chunking.py), as the ids its SentencePiece Unigram tokenizer gives,
// byte fallback included; and its weights, expanded from 8-bit numbers into the fp32 data its graphs read.
// Tested under node --test.

/**
 * A graph's external data, fp32: each tensor's 8-bit numbers times its channel's scale.
 * @param {ArrayBuffer} bin @param {{ bytes: number, tensors: number[][] }} graph [offset in the data, count, values a channel spans, channels, at in bin, scales at]
 */
export function expand(bin, { bytes, tensors }) {
  const out = new Float32Array(bytes / 4)
  for (const [at, count, inner, channels, values, scales] of tensors) {
    const q = new Int8Array(bin, values, count)
    const scale = new Float32Array(bin, scales, channels)
    for (let i = 0, o = at / 4; i < count; i++) out[o + i] = q[i] * scale[((i / inner) | 0) % channels]
  }
  return new Uint8Array(out.buffer)
}

/**
 * A tokenizer.json's Unigram model: ids by Viterbi over its pieces' scores, words split before each "▁" as
 * Metaspace splits them, a character it lacks as its UTF-8 bytes; and back to text.
 * @param {{ model: { vocab: [string, number][], unk_id: number } }} json
 */
export function tokenizer({ model: { vocab, unk_id: unknown } }) {
  const ids = new Map(vocab.map(([piece], i) => [piece, i]))
  const longest = Math.max(...vocab.map(([piece]) => [...piece].length))
  const missing = Math.min(...vocab.map(([, score]) => score)) - 10
  const byte = (/** @type {number} */ b) => ids.get(`<0x${b.toString(16).toUpperCase().padStart(2, '0')}>`) ?? unknown
  /** @param {string[]} chars */
  const best = (chars) => {
    const score = new Float64Array(chars.length + 1).fill(-Infinity)
    const from = new Int32Array(chars.length + 1)
    const piece = new Int32Array(chars.length + 1)
    score[0] = 0
    for (let i = 0; i < chars.length; i++) {
      let known = false
      for (let j = i + 1, text = ''; j <= Math.min(chars.length, i + longest); j++) {
        text += chars[j - 1]
        const id = ids.get(text)
        if (id === undefined) continue
        known ||= j === i + 1
        if (score[i] + vocab[id][1] > score[j]) [score[j], from[j], piece[j]] = [score[i] + vocab[id][1], i, id]
      }
      if (!known && score[i] + missing > score[i + 1]) [score[i + 1], from[i + 1], piece[i + 1]] = [score[i] + missing, i, -1]
    }
    /** @type {number[]} */
    const out = []
    for (let j = chars.length; j > 0; j = from[j]) out.unshift(...(piece[j] < 0 ? [...new TextEncoder().encode(chars[j - 1])].map(byte) : [piece[j]]))
    return out
  }
  return {
    /** @param {string} text */
    encode: (text) => `▁${text}`.replaceAll(' ', '▁').split(/(?=▁)/).flatMap((word) => best([...word])),
    /** Each piece's bytes, a byte token's its own, read as one text without the space a first word starts with. @param {number[]} list */
    decode: (list) => new TextDecoder().decode(new Uint8Array(list.flatMap((id) => {
      const raw = /^<0x([0-9A-F]{2})>$/.exec(vocab[id][0])
      return raw ? [parseInt(raw[1], 16)] : [...new TextEncoder().encode(vocab[id][0].replaceAll('▁', ' '))]
    }))).replace(/^ /, ''),
  }
}

/** @typedef {{ replace: Record<string, string>, semicolons: boolean, pad: boolean, final: boolean, capitalize: boolean }} Rules */
/** @typedef {ReturnType<typeof tokenizer>} Tokenizer */

const FINAL = '.!?…'
const WEAK = ',;:-–—'
const CLOSERS = '"\'”’)]»'
const OPENERS = "\"'“‘([«"
const ENDS_WITH_DECIMAL_NUMBER = /\d[.,]\d+\W*$/
const TITLES = new Set(['Mr.','Mrs.','Ms.','Dr.','Prof.','Rev.','vs.','e.g.','i.e.'])
/** @param {string} text @param {string} set */
const trimEnd = (text, set) => {
  while (text && set.includes(text.at(-1) ?? '')) text = text.slice(0, -1)
  return text
}

/**
 * A chunk as the model reads it, and how many frames to go on after it says it is done: characters it
 * wasn't trained on replaced, a capital first, a final mark. @param {string} text @param {Rules} rules
 */
export function prepare(text, rules) {
  text = text.trim()
  if (Object.keys(rules.replace).length) {
    text = [...text].map((c) => rules.replace[c] ?? c).join('').split(/\s+/).filter(Boolean).join(' ')
    text = text.replace(/([.!?…])\s*[,;:]/g, '$1')
  }
  text = text.replaceAll('\n', ' ').replaceAll('\r', ' ').replaceAll('  ', ' ')
  if (rules.semicolons) text = text.replaceAll(';', ',')
  const words = text.split(/\s+/).filter(Boolean).length
  if (rules.capitalize) {
    let start = 0
    while (start < text.length && OPENERS.includes(text[start])) start++
    if (start < text.length && text[start] !== text[start].toUpperCase()) text = text.slice(0, start) + text[start].toUpperCase() + text.slice(start + 1)
  }
  if (rules.final) {
    const core = trimEnd(text, `${CLOSERS} `)
    const closers = text.slice(core.length).trim()
    if (core && !FINAL.includes(core.at(-1) ?? '')) text = WEAK.includes(core.at(-1) ?? '') ? `${trimEnd(core, `${WEAK} `)}.${closers}` : `${text}.`
  }
  if (rules.pad && words < 5) text = `        ${text}`
  return { text, after: (words <= 4 ? 3 : 1) + 2 }
}

/**
 * Prepare the next chunk with its predecessor as context, matching Pocket TTS'
 * teacher-forced continuation path.
 * @param {string} previous
 * @param {string} current
 * @param {ReturnType<typeof tokenizer>} tokens
 * @param {Rules} rules
 */
export function continuationPrompt(previous, current, tokens, rules) {
  const text = prepare(previous ? `${previous} ${current}` : current, rules).text
  return { text, ids: tokens.encode(text) }
}

/**
 * Pack the previous chunk's generated latents the way Pocket TTS expects for
 * teacher-forced continuation: BOS followed by every old frame except the last.
 * The final old frame becomes the first autoregressive input for the new chunk.
 * @param {Float32Array[]} frames
 */
export function teacherForcedSequence(frames) {
  if (!frames?.length) return { sequence: new Float32Array(0), firstInput: null }
  const sequence = new Float32Array(frames.length * 32)
  sequence.fill(NaN, 0, 32)
  for (let i = 0; i < frames.length - 1; i++) sequence.set(frames[i], (i + 1) * 32)
  return { sequence, firstInput: frames[frames.length - 1].slice() }
}

/** Join a set of 32-value latent frames for the decoder's [1, frames, 32] input. */
export function packLatents(frames) {
  const packed = new Float32Array(frames.length * 32)
  frames.forEach((frame, index) => packed.set(frame, index * 32))
  return packed
}

/** Advance ONNX decoder step counters after decoding latent frames, as Mimi requires. */
export function advanceDecoderSteps(parts, state, amount) {
  for (const part of parts) {
    if (part.key !== 'step') continue
    const tensor = state[part.input_name]
    const values = tensor?.data ?? tensor
    if (!values || typeof values.length !== 'number') continue
    for (let i = 0; i < values.length; i++) {
      values[i] += typeof values[i] === 'bigint' ? BigInt(amount) : amount
    }
  }
}

/**
 * Pocket TTS sentence chunking, adapted from Kyutai's text_chunking.py.
 * Long sentences are split only at commas/semicolons/colons, with decimal
 * punctuation and titles protected. Raw text is retained for continuation.
 * @param {string} text @param {Tokenizer} tokens @param {Rules} rules
 */
function innerPunctuation(list, start, tokens) {
  const after = tokens.decode(list.slice(start - 1, start + 1))
  if (after.length >= 2 && /[\p{L}\p{N}]/u.test(after[1])) return true
  const windowStart = Math.max(0, start - 6)
  const words = tokens.decode(list.slice(windowStart, start)).split(/\s+/).filter(Boolean)
  return words.length > 0 && TITLES.has(words[words.length - 1]) && (words.length > 1 || windowStart === 0)
}
const MAX_CLOSER_TOKENS = 8
const CLOSERS_OR_PARTIAL = CLOSERS + '\uFFFD'
function skipClosers(list, start, tokens) {
  const punctuation = tokens.decode(list.slice(start - 1, start))
  let kept = start
  const stop = Math.min(list.length, start + MAX_CLOSER_TOKENS)
  for (let end = start + 1; end <= stop; end++) {
    const window = tokens.decode(list.slice(start - 1, end))
    const after = window.slice(punctuation.length)
    if (!after || [...after].some((c) => !CLOSERS_OR_PARTIAL.includes(c))) break
    if (!after.includes('\uFFFD')) kept = end
  }
  return kept
}
function boundaryIndices(list, marks, tokens, ignoreInner = false) {
  const boundarySet = new Set(marks), indices = [0]
  let previousBoundary = false
  list.forEach((token, index) => {
    if (boundarySet.has(token)) { previousBoundary = true; return }
    if (previousBoundary && !(ignoreInner && innerPunctuation(list, index, tokens))) {
      const start = skipClosers(list, index, tokens)
      if (start < list.length) indices.push(start)
    }
    previousBoundary = false
  })
  indices.push(list.length)
  return indices
}
function segments(list, boundaries, tokens) {
  const out = []
  for (let i = 0; i < boundaries.length - 1; i++) {
    const start = boundaries[i], end = boundaries[i + 1]
    out.push([end - start, tokens.decode(list.slice(start, end))])
  }
  return out
}
export function chunks(text, tokens, rules, most = 25) {
  const preparedText = prepare(text, rules).text.trim()
  const all = tokens.encode(preparedText)
  const sentenceMarks = tokens.encode('.!...?').slice(1)
  const sentenceParts = segments(all, boundaryIndices(all, sentenceMarks, tokens, true), tokens)
  const fallbackMarks = tokens.encode(',;:').slice(1)
  const refined = sentenceParts.flatMap(([count, sentence]) => {
    if (count <= most) return [[count, sentence]]
    const localTokens = tokens.encode(sentence.trim())
    const local = segments(localTokens, boundaryIndices(localTokens, fallbackMarks, tokens, true), tokens)
    return local.length > 1 ? local : [[count, sentence]]
  })
  const glued = []
  for (const [count, part] of refined) {
    const last = glued[glued.length - 1]
    if (last && ENDS_WITH_DECIMAL_NUMBER.test(last[1])) {
      glued[glued.length - 1] = [last[0] + count, last[1].trimEnd() + ' ' + part.trimStart()]
    } else glued.push([count, part])
  }
  const grouped = []
  for (const [, part] of glued) {
    const last = grouped[grouped.length - 1]
    const candidate = last ? last.text + ' ' + part : part
    const actualCount = tokens.encode(prepare(candidate, rules).text).length
    if (last && actualCount <= most) { last.text = candidate; last.count = actualCount }
    else grouped.push({ text: part, count: tokens.encode(prepare(part, rules).text).length })
  }
  return grouped.map(({ text }) => ({ text: text.trim(), after: prepare(text, rules).after }))
}

/** Whether a sentence mark is a decimal point: a digit before it and after. @param {string} before @param {string} next */
const decimal = (before, next) => before.length >= 2 && before.at(-1) === '.' && /\p{Nd}/u.test(before.at(-2) ?? '') && /^\p{Nd}/u.test(next)
