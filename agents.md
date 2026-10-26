Commit coherent changes as work progresses. Keep TODO.md to one task per line, tagged @agent or @user. Do not add user documentation or code comments; preserve third-party licence and attribution notices.

Work in reviewed stages: Ergogen, KiCad, firmware, mechanical. Do not advance a board to the next stage without user review. Never present placement files, stale routing, provisional adapters or envelope models as fabrication-ready. Review approvals must refer to current source hashes.

Use one root npm installation and KiCad 10 for every active board. Keep the existing QBF geometry unchanged during repository cleanup. The active QBF case is modular-case; bumper-case and mechanical are historical.

The three new modules must share one PCB footprint, approximately half a Pixel 6 Pro. Each needs a display, controller, battery, power switch, reset button and at least four 1.5U keys. Keys, trackpad and display must be on the top face and mirror-symmetric left-to-right as an interaction layout. A directional display may need firmware rotation for handedness. These requirements do not apply to the existing QBF board, which has no display or separate reset.

Keep direct GPIO-to-ground switches without a matrix or diodes. Battery selection, protection, polarity, charging limits, antenna clearance and component stack-up require verification before fabrication. Do not suppress real DRC errors to pass a build.
