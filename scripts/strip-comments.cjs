const fs = require('fs');
const path = require('path');
const child = require('child_process');
const esprima = require('esprima');
const root = path.resolve(__dirname, '..');
const files = child.execFileSync('git', ['ls-files', '*.js', '*.cjs', '*.swift', '*.overlay', '*.keymap'], {cwd: root, encoding: 'utf8'}).trim().split('\n');
let changed = 0;
for (const relative of files) {
  if (!/\.(c?js)$/.test(relative)) continue;
  const file = path.join(root, relative);
  if (!fs.existsSync(file)) continue;
  const original = fs.readFileSync(file, 'utf8');
  const comments = esprima.tokenize(original, {comment: true, range: true}).filter(t => /Comment$/.test(t.type));
  let source = original;
  for (const comment of comments.reverse()) {
    if (/copyright|SPDX|Author:|creativecommons.org\/licenses/i.test(comment.value)) continue;
    const [start, end] = comment.range;
    source = source.slice(0, start) + source.slice(start, end).replace(/[^\r\n]/g, '') + source.slice(end);
  }
  if (source !== original) {
    fs.writeFileSync(file, source);
    changed++;
  }
}
console.log(`Removed non-license JavaScript comments from ${changed} files.`);
