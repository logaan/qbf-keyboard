# Battery and continuous-roof arrangement

Updated 21 October 2026. No battery was purchased and no supplier was contacted.

## Final design decision

Retain the **original protected 301055, 220 mAh battery** and recess it through an opening in the main PCB onto the existing baseplate. The design uses the existing modeled **57.5 × 10.5 × 3.5 mm envelope**, including protection. These are the keyboard model's design allowances, **not a verified manufacturer's maximum-dimension specification**. Check the actual supplied pack, insulation, protection board and wire exit against this envelope before assembly.

The opening makes a continuous 1 mm battery roof possible without changing the battery or charger. Smaller batteries researched below remain alternatives; none replaces the original battery in the final BOM or assembly previews.

## Mechanical dimensions

All coordinates use the case reference system, with the main PCB top at z = 0.

| Feature | Final design value |
| --- | --- |
| Main-PCB battery opening | 58.1 × 11.1 mm |
| Opening center | Fixed case frame (30.4,27.5); current PCB lower-left frame (31.9,29) mm |
| Modeled battery lower-left corner | x = 1.65 mm, y = 22.25 mm |
| Baseplate top | z = −1.6 mm |
| Insulating adhesive thickness | 0.2 mm |
| Battery bottom / maximum modeled top | z = −1.4 / 2.1 mm |
| Continuous roof underside / top | z = 2.4 / 3.4 mm |
| Battery-to-roof clearance | 0.3 mm |
| Fully depressed keycap underside | z = 4.0 mm |
| Roof-to-depressed-keycap clearance | 0.6 mm |
| Opening clearance around the pack envelope | 0.3 mm per side |

These clearances are geometric calculations against the existing component models, not measured physical fit. The baseplate and insulating adhesive support the pack. Keep its pouch clear of copper, solder features and exposed opening edges. Round or insulate the opening edges, preserve space for the wire exit, and do not compress the battery in the screw-and-nut sandwich. Retain the factory-insulated leads and route them toward the existing side-entry JST-PH connector.

## Charger and connector requirements

[Nice Keyboards' nice!nano documentation](https://nicekeyboards.com/docs/nice-nano/) describes approximately 100 mA default charging, with approximately 85 mA mentioned as the typical actual rate. Check the supplied battery's allowed charge current against the actual unboosted controller charger, including its tolerance. Capacity or a battery size code alone does not establish this rating. Keep the charging boost jumper open.

[Nice Keyboards' connection instructions](https://nicekeyboards.com/docs/nice-nano/getting-started/) require checking polarity because suppliers use both JST pin orders. Use a factory-fitted two-pin JST-PH lead compatible with the board's S2B-PH-K-S header: positive must reach board pad 1 (`BAT_POS`) and negative must reach pad 2 (`GND`). Confirm this electrically before connection; matching connector housings do not prove matching polarity.

## Optional researched replacement

[VCELL VP301230](https://www.vcellpower-battery.com/3.7v/3-7v-110mah-301230-mini-lipo-battery-with-connector.html) is a documented protected 110 mAh, 3.7 V alternative. The manufacturer specifies a maximum finished size including PCM of **32.5 × 12.5 × 3.2 mm**, a 4.2 V charging limit, and a maximum charge current of **1 C = 110 mA**. Its wire/connector configuration is TBD. Stock, minimum order quantity, price and delivery to Australia have not been established. It would require a different, wider PCB opening, matching case geometry and a specified factory JST-PH lead; it is **not the selected battery**.

The thin protected [FP LP200830](https://www.fpbattery.com/wp-content/uploads/2024/04/fpbattery-200830-3.7V-30mAh-Lithium-Polymer-Battery-Specification.pdf) illustrates why thickness alone was insufficient: its 32 × 8 × 2 mm pack is 30 mAh and allows only 0.5 C = 15 mA charging. It cannot use an unmodified nice!nano charger. Recessing the original pack avoids a charging redesign and retains its capacity.

## Regeneration and assembly

Keep the original 301055 envelope and recessed placement aligned across the PCB footprint, 3D reference model and case parameters. Regenerate both boards, mechanical outputs, case solids and both assembly previews after changes. The battery must remain present in both previews. Before tightening the case, confirm the actual battery fits freely, the roof stays clear through full key travel, and the leads cannot be pinched.
