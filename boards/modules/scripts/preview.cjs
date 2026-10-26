// Dimensioned 2D companion to the real KiCad 3D renders.
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');
const root = path.join(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const u = yaml.safeLoad(read('output/points/units.yaml'));
const points = yaml.safeLoad(read('output/points/points.yaml'));
const geometry = fs.existsSync(path.join(root, 'kicad/geometry.json')) ? JSON.parse(read('kicad/geometry.json')) : null;
const cx = 100+1.5*u.pitch_x, scale = 4;
const X = x => 300+(x-cx)*scale, Y = y => 230+(y-100)*scale;
const esc = x => String(x).replaceAll('&','&amp;').replaceAll('<','&lt;');
const line = (x1,y1,x2,y2,color='#728097',width=1) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}"/>`;
const label = (x,y,value,size=15,color='#24364b',anchor='middle') => `<text x="${x}" y="${y}" font-family="sans-serif" font-size="${size}" fill="${color}" text-anchor="${anchor}">${esc(value)}</text>`;
const rect = (x,y,w,h,fill,stroke='#24364b',r=0,extra='') => `<rect x="${X(x-w/2)}" y="${Y(y-h/2)}" width="${w*scale}" height="${h*scale}" rx="${r*scale}" fill="${fill}" stroke="${stroke}" ${extra}/>`;
const circle = (x,y,r,fill,stroke) => `<circle cx="${X(x)}" cy="${Y(y)}" r="${r*scale}" fill="${fill}" stroke="${stroke}"/>`;
const outline = () => rect(cx,100,u.board_w,u.board_h,'#ecf3f1','#2e695b',u.board_corner);
const mounts = Object.entries(points).filter(([n])=>n.startsWith('mount_'));
const holes = () => mounts.map(([,p])=>circle(p.x,-p.y,u.mount_diameter/2,'white','#24364b')).join('');
const panel = (x,y,title,body,foot) => `<g transform="translate(${x} ${y})"><rect x="5" y="5" width="590" height="495" rx="15" fill="white" stroke="#d9e2eb"/>${label(28,38,title,21,'#142a40','start')}${body}${label(300,470,foot,14)}</g>`;
let top = outline()+holes();
for (const [name,p] of Object.entries(points).filter(([,p])=>p.meta.tags.includes('switch'))) {
  top += rect(p.x,-p.y,p.meta.width,p.meta.height,name.endsWith('middle')?'#aee1d8':'#cbd9f2','#3c526f',1.2);
  top += label(X(p.x),Y(-p.y)+3,p.meta.colrow.replace('_',' / '),11);
}
top += line(X(cx-u.board_w/2),420,X(cx+u.board_w/2),420);
top += label(300,444,`${u.board_w.toFixed(1)} × ${u.board_h.toFixed(1)} mm PCB and acrylic`,16);
let under = outline();
const mcu = points.controller;
under += rect(mcu.x,-mcu.y+0.03,17.78,33.08,'#8badd6','#314c6c');
under += label(X(mcu.x),Y(-mcu.y)-7,'nice!nano',12);
under += rect(mcu.x-0.127,-mcu.y-17.272,7.366,1.524,'#c5c8ce','#565d66');
under += rect(points.display.x,-points.display.y,14,36,'#d5b7ed','#6e4a8d');
under += label(X(points.display.x),Y(-points.display.y)-10,'nice!view',12);
under += rect(points.battery.x,-points.battery.y,u.battery_w,u.battery_h,'#e8cd7c','#8b7334');
under += label(X(points.battery.x),Y(-points.battery.y)-10,'LiPo',12);
if (geometry) for (const fp of geometry.footprints) for (const p of fp.pads) {
  if (p.drill[0]) under += circle(p.position[0],p.position[1],p.drill[0]/2,'white','#4a5364');
}
if (geometry) for (const c of geometry.accepted_header_clearances) under += circle(c.switch_hole[0],c.switch_hole[1],2.8,'none','#d12644');
under += label(X(points.reset.x)-8,Y(-points.reset.y),'RESET',11,'#8a3444','end');
under += label(X(points.power.x),Y(-points.power.y)+25,'POWER',11);
under += label(X(points.jst.x),Y(-points.jst.y)+25,'JST-PH',11);
under += holes();
let base = outline()+`<circle cx="300" cy="230" r="${u.ring_outer_diameter*scale/2}" fill="none" stroke="#a3a9b3" stroke-width="${(u.ring_outer_diameter-u.ring_inner_diameter)*scale/2}"/>`+holes();
// Ring is stroked on its centreline so the displayed outer diameter stays exact.
base = outline()+`<circle cx="300" cy="230" r="${(u.ring_outer_diameter+u.ring_inner_diameter)*scale/4}" fill="none" stroke="#a3a9b3" stroke-width="${(u.ring_outer_diameter-u.ring_inner_diameter)*scale/2}"/>`+holes();
base += label(300,425,`Provisional passive ring: Ø${u.ring_outer_diameter}/Ø${u.ring_inner_diameter} × ${u.ring_thickness} mm`,15);
let stack = '';
const sx=130, sy=180, zs=13;
const layer=(z,t,w,color) => `<rect x="${300-w/2}" y="${sy-z*zs}" width="${w}" height="${t*zs}" fill="${color}" stroke="#41556b"/>`;
stack += layer(8.5,2,290,'#cbd9f2')+layer(5.3,5.3,230,'#929ca5')+layer(0,1.6,390,'#417868');
stack += layer(-4.6,3.2,90,'#8badd6')+layer(-4.9,2.9,80,'#d5b7ed');
stack += `<rect x="${sx}" y="${sy+1.6*zs}" width="16" height="${u.standoff_height*zs}" fill="#bcc2ca"/><rect x="454" y="${sy+1.6*zs}" width="16" height="${u.standoff_height*zs}" fill="#bcc2ca"/>`;
stack += layer(-1.6-u.standoff_height,u.acrylic_thickness,390,'#d7e9ee');
stack += layer(-1.6-u.standoff_height-u.acrylic_thickness,u.ring_thickness,250,'#939aa4');
stack += label(300,390,`Standoff ${u.standoff_height} mm; acrylic ${u.acrylic_thickness} mm are placeholders`,14);
stack += label(300,415,'Bare module thickness does not determine socket or assembly clearance.',13);
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1080" viewBox="0 0 1200 1080"><rect width="1200" height="1080" fill="#f2f5f9"/>${label(30,35,'Braille keyboard · compact review draft',26,'#142a40','start')}${label(30,62,'Provisional spacing and cap envelopes · accepted clashes retained · no manufacturing release',15,'#8a3444','start')}${panel(0,75,'Top: twelve keys',top,'Outer rows 1 × 1.5 U portrait; middle row 1 U')}${panel(600,75,'Underside: viewed through the PCB',under,'Red circles mark accepted header / switch-hole clashes')}${panel(0,580,'Outside face of acrylic baseplate',base,'Matching mounting holes; ring avoids the corner fasteners')}${panel(600,580,'Assembly height study',stack,'Component solids and all vertical dimensions are review envelopes')}</svg>`;
fs.mkdirSync(path.join(root,'previews'),{recursive:true});
fs.writeFileSync(path.join(root,'previews/layout-review.svg'),svg);
console.log('Wrote dimensioned layout, underside, baseplate and stack review.');
