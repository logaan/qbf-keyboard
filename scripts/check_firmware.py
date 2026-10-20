from pathlib import Path
import hashlib
import json
import pickle
import re
import sys

OUTPUT,WORKSPACE=map(Path,sys.argv[1:])
ROOT=Path(__file__).resolve().parents[1]
cache=(OUTPUT/'build/CMakeCache.txt').read_text()
zephyr=Path(re.search(r'^ZEPHYR_BASE:PATH=(.+)$',cache,re.M).group(1))
sys.path.insert(0,str(zephyr/'scripts/dts/python-devicetree/src'))
with (OUTPUT/'build/zephyr/edt.pickle').open('rb') as f:edt=pickle.load(f)
spec=json.loads((ROOT/'ergogen-kikad/design/assembly.json').read_text())
config=(OUTPUT/'build/zephyr/.config').read_text()
inputs=edt.get_node('/kscan0').props['input-gpios'].val
assert len(inputs)==10
mapping=[]
for index,gpio in enumerate(inputs):
    port=0 if 'gpio0' in gpio.controller.labels else 1 if 'gpio1' in gpio.controller.labels else -1
    pin=gpio.data['pin'];flags=gpio.data['flags']
    assert [port,pin]==spec['gpio']['D'+str(index)]
    assert flags==17,(index,flags)
    mapping.append({'key':('t' if index<5 else 'b')+str(index%5+1),'net':'D'+str(index),'gpio':[port,pin],'active_low':True,'internal_pull_up':True})
for symbol in ['CONFIG_ZMK_USB','CONFIG_ZMK_BLE','CONFIG_BUILD_OUTPUT_UF2','CONFIG_GPIO_HOGS']:
    assert re.search('^'+symbol+'=y$',config,re.M),symbol
for symbol in ['CONFIG_ZMK_DISPLAY','CONFIG_ZMK_SPLIT']:
    assert not re.search('^'+symbol+'=y$',config,re.M),symbol
for label in ['xiao_i2c','xiao_spi','xiao_serial']:
    assert edt.label2node[label].status=='disabled',label
charge=edt.get_node('/soc/gpio@50000000/qbf_charge_slow')
assert charge.props['input'].val
assert not charge.props['output-low'].val and not charge.props['output-high'].val
assert charge.props['gpios'].val==[13,0]
assert edt.label2node['default_transform'].props['map'].val==list(range(10))
keymap=(ROOT/'ergogen-kikad/config/boards/shields/qbf_macropad/qbf_macropad.keymap').read_text()
assert re.findall(r'&kp\s+(N[0-9])',keymap)==['N1','N2','N3','N4','N9','N5','N6','N7','N8','N0']
uf2=OUTPUT/'qbf_macropad.uf2'
data=uf2.read_bytes()
assert data[:8]==bytes.fromhex('5546320a57515d9e') and len(data)%512==0
result={'passed':True,'board':'xiao_ble/nrf52840/zmk','shield':'qbf_macropad','zmk_revision':(OUTPUT/'zmk-revision.txt').read_text().strip(),'standalone':True,'display':False,'usb':True,'bluetooth':True,'charge_control':{'gpio':[0,13],'mode':'input, no pulls; native approximately 50 mA setting'},'gpio_mapping':mapping,'keymap':['1','2','3','4','9','5','6','7','8','0'],'uf2_bytes':len(data),'uf2_sha256':hashlib.sha256(data).hexdigest(),'limitations':['Compiled and resolved device tree checked; flashing and physical key, USB/Bluetooth and charging behavior require a prototype.']}
(OUTPUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('Firmware validation passed: ten matching GPIO inputs, standalone USB/BLE, no display, slow-charge input')
