# Battery research for the continuous upper roof

Research date: 21 October 2026. No battery was purchased and no supplier was contacted.

## Selected design battery

Use **VCELL VP301230**, a protected 110 mAh single-cell 3.7 V lithium-polymer pack. The [manufacturer's product specification](https://www.vcellpower-battery.com/3.7v/3-7v-110mah-301230-mini-lipo-battery-with-connector.html) explicitly gives a **maximum finished size including PCM of 32.5 × 12.5 × 3.2 mm**, a 4.2 V charging limit, and a maximum charge current of 1 C, equal to **110 mA**. This supports the unboosted nice!nano charger. The original 301055 envelope was 57.5 × 10.5 × 3.5 mm.

The manufacturer offers this model by inquiry; stock, minimum order quantity, price and delivery to Australia have not been established. The wire/connector configuration is listed as TBD. Specify a factory-fitted two-pin **JST-PH** lead compatible with the board's side-entry S2B-PH-K-S header, with positive to board pad 1 (`BAT_POS`) and negative to board pad 2 (`GND`). Require the completed protected and wrapped pack to retain the published maximum dimensions. Confirm those terms before buying; do not substitute a generic 301230 using its nominal cell code alone. No supplier has been contacted.

## Mechanical arrangement

Recess the smaller pack through a main-PCB opening onto the existing baseplate. Relative to the main PCB top, the baseplate top is z = −1.6 mm. With 0.20 mm insulating adhesive, the pack bottom is z = −1.4 mm and its maximum top is z = 1.8 mm. A continuous 1 mm roof with its underside at z = 2.2 mm therefore clears the battery by 0.40 mm and finishes at z = 3.2 mm. The fully depressed keycap underside is z = 4.0 mm, leaving 0.80 mm vertical clearance above that roof. These are design calculations, not a physical fit measurement.

Allow at least 0.30 mm lateral clearance around the maximum pack, requiring a minimum 33.1 × 13.1 mm opening before corner-radius allowance. The selected well center is x = 20.55 mm, y = 27.5 mm in the case reference coordinates. Round or line the opening edges, keep all copper and solder features away from the pouch and its wire exit, and do not clamp the battery in the screw sandwich. The baseplate and insulating adhesive support the pack; the opening wall must not press against it. Route leads in the remaining corridor toward the existing connector and retain the full factory-insulated lead rather than requiring battery-tab or surface-mount soldering.

Without the PCB recess, 0.20 mm adhesive, 0.20 mm roof clearance, a 1 mm roof and 0.20 mm keycap clearance restrict a top-mounted pack to 2.40 mm maximum thickness. No electrically compatible protected pack within that thickness and the available corridor was verified. The recessed arrangement preserves the continuous roof and the existing charging circuit.

## Electrical constraint

[Nice Keyboards' nice!nano documentation](https://nicekeyboards.com/docs/nice-nano/) describes a default charging rate of approximately 100 mA, with approximately 85 mA mentioned as the typical actual rate, and recommends batteries of at least 100 mAh. Treat 100 mA as the design requirement until the exact controller charger tolerance is established. A capacity of 100 mAh alone does not prove that a pack permits a 100 mA charge; its own maximum charge-current rating must allow it. Do not enable the charging boost jumper for these small packs.

[Nice Keyboards' connection instructions](https://nicekeyboards.com/docs/nice-nano/getting-started/) also require checking JST connector polarity because battery suppliers use both pin orders. A matching housing is insufficient evidence of electrical compatibility.

## Primary-source candidates

| Candidate | Published assembled dimensions, L × W × T | Capacity | Protection | Maximum charge | Result |
| --- | --- | --- | --- | --- | --- |
| [VCELL VP301230 specification](https://www.vcellpower-battery.com/3.7v/3-7v-110mah-301230-mini-lipo-battery-with-connector.html) | 32.5 × 12.5 × 3.2 mm maximum, including PCM | 110 mAh | PCM included | 1 C = 110 mA | Selected for the recessed PCB well; connector and supply terms need confirmation |
| [FP Battery LP200830 datasheet](https://www.fpbattery.com/wp-content/uploads/2024/04/fpbattery-200830-3.7V-30mAh-Lithium-Polymer-Battery-Specification.pdf) | 32 × 8 × 2 mm; drawing distinguishes 30 mm cell length and 32 mm assembly length | 30 mAh | PCM: yes | 0.5 C = 15 mA | Thin, but incompatible with default charging |
| [FP Battery LP201021 datasheet](https://www.fpbattery.com/wp-content/uploads/2024/04/fpbattery-201021-3.7V-25mAh-Lithium-Polymer-Battery-Specification.pdf) | 23 × 10 × 2 mm | 25 mAh | PCM: yes | 0.5 C = 12.5 mA | Thin, but incompatible with default charging |
| [FP Battery LP201040 datasheet](https://www.fpbattery.com/wp-content/uploads/2024/04/fpbattery-201040-3.7V-50mAh-Lithium-Polymer-Battery-Specification.pdf) | 42 × 10 × 2 mm | 50 mAh | PCM: yes | 0.5 C = 25 mA | Thin, but incompatible with default charging |
| [FP Battery LP201230 datasheet](https://www.fpbattery.com/wp-content/uploads/2023/10/201230-3.7V-60mAh-Specification.pdf) | 32 × 12 × 2 mm | 60 mAh | Protection thresholds and PCM shown | 0.5 C = 30 mA | Thin, but incompatible with default charging |
| [LiPol Battery LP201256 catalog](https://www.lipolbattery.com/Ultra-Thin-LiPo-Battery.html) | Only 56 × 12 × 2 mm nominal catalog size found | 112 mAh | Not specified for this catalog row | Not specified for this model | Plausible cell size, but protected-pack thickness and charge compatibility remain unverified |
| [PowerStream GM201030-PCB catalog](https://www.powerstream.com/thin-lithium-ion.htm) | 30 × 10 × 2 mm listed | 43 mAh | Protection board explicitly included | No model-specific maximum established | Do not assume compatibility with 100 mA charging |
| [PowerStream GM251534-PCB catalog](https://www.powerstream.com/thin-lithium-ion.htm) | 34 × 13 × 2.5 mm listed | 100 mAh | Protection board explicitly included | No model-specific maximum established | Exceeds the nominal thickness target before tolerance |

The FP individual datasheets are marked preliminary. They specify nominal T and W without tolerances. FP's [general battery table](https://www.fpbattery.com/lithium-polymer-battery/) gives thickness ±0.2 mm, width ±1.0 mm, and length ±0.5 mm, but this is not a model-specific finished-pack approval drawing. Consequently, a 2.2 mm CAD envelope inferred from a nominal 2.0 mm pack remains a design assumption until the supplied pack is measured or a model-specific drawing is obtained. The diagrams show red positive and black negative wires; they do not establish a JST-PH housing and contact-position polarity for the ordered variant.

FP offers protection and custom leads through its [small-battery catalog](https://www.fpbattery.com/ultra-small-lithium-polymer-battery/). PowerStream explicitly lists engineering quantities. Neither source establishes current stock, shipping availability, or a quoted configuration for this keyboard.

## Other small-pack checks

[Adafruit PID 1570](https://www.adafruit.com/product/1570) is a protected 100 mAh pack with a JST-PH lead and an allowed 100 mA charge. However, its linked [PKCELL LP401230 pack drawing](https://cdn-shop.adafruit.com/product-files/1570/1570datasheet.pdf), page 5, gives 30 ± 2 × 12 ± 0.3 × 4.0 ± 0.3 mm, so a conservative maximum envelope is 32 × 12.3 × 4.3 mm. The product page's 31 × 11.5 × 3.8 mm dimensions do not override that toleranced drawing. It needs a deeper well or a higher roof and is not a direct geometry substitute. PID 1578 is the 500 mAh product, not this battery.

[SparkFun PRT-13853](https://www.sparkfun.com/lithium-ion-battery-110mah.html) is protected and specifies a maximum charge of 110 mA, but its DTP401525 model is 15 mm wide and 4 mm thick. It exceeds this well's width budget. Battery model and revision matter: newer DTP specifications can differ from an older distributor-hosted specification.

## Integration and procurement checks

Record the selected VP301230 model, 110 mAh capacity, finished maximum 32.5 × 12.5 × 3.2 mm envelope, 110 mA maximum charge, ordered connector and polarity in the BOM, case parameters, reference geometry and assembly instructions. Regenerate and check both boards, the mechanical files, the case solids and both assembly previews. Retain the battery in both previews.

Before assembly, verify the supplied pack and wire exit fit without compression, the roof remains clear through full key travel, and the connector polarity matches the board. Confirm the actual controller's unboosted maximum charging current stays below the pack's 110 mA limit. Do not use the boost jumper or the listed low-capacity FP packs with an unmodified nice!nano charger.
