import Foundation
import IOKit.hid

func emit(_ item: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: item, options: [.sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write(Data([10]))
}

func property(_ device: IOHIDDevice, _ name: String) -> Any? {
    IOHIDDeviceGetProperty(device, name as CFString)
}

var previousValues: [UInt32: Bool] = [:]

let manager = IOHIDManagerCreate(kCFAllocatorDefault, IOOptionBits(kIOHIDOptionsTypeNone))
let listing = CommandLine.arguments.contains("--list")
let matching: [String: Any] = listing ? [:] : [kIOHIDProductKey: "Mikoto Test"]
IOHIDManagerSetDeviceMatching(manager, matching as CFDictionary)
IOHIDManagerScheduleWithRunLoop(manager, CFRunLoopGetCurrent(), CFRunLoopMode.defaultMode.rawValue)
let opened = IOHIDManagerOpen(manager, IOOptionBits(kIOHIDOptionsTypeNone))
guard opened == kIOReturnSuccess else {
    emit(["type": "error", "error": "Cannot open HID manager; check macOS Input Monitoring", "code": opened])
    exit(2)
}
let devices = (IOHIDManagerCopyDevices(manager) as? Set<IOHIDDevice>) ?? []
if listing {
    for device in devices {
        emit(["type": "device", "product": property(device, kIOHIDProductKey) ?? "",
              "vendor": property(device, kIOHIDVendorIDKey) ?? 0,
              "product_id": property(device, kIOHIDProductIDKey) ?? 0,
              "location": property(device, kIOHIDLocationIDKey) ?? 0])
    }
    exit(0)
}
guard devices.count == 1 else {
    emit(["type": "error", "error": "Connect exactly one Mikoto Test keyboard", "devices": devices.count])
    exit(2)
}
IOHIDManagerRegisterInputValueCallback(manager, { _, result, _, value in
    guard result == kIOReturnSuccess else { return }
    let element = IOHIDValueGetElement(value)
    guard IOHIDElementGetUsagePage(element) == 7 else { return }
    let usage = IOHIDElementGetUsage(element)
    guard usage > 3 else { return } // exclude array rollover/error usages
    let pressed = IOHIDValueGetIntegerValue(value) != 0
    // Ignore unchanged bitfield values and initial all-released reports.
    guard pressed != (previousValues[usage] ?? false) else { return }
    previousValues[usage] = pressed
    emit(["type": "key", "usage": usage,
          "pressed": pressed,
          "time": ProcessInfo.processInfo.systemUptime])
}, nil)
emit(["type": "ready", "devices": devices.count, "product": "Mikoto Test"])
CFRunLoopRun()
