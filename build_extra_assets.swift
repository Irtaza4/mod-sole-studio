import AppKit

func savePNG(image: NSImage, path: String) {
    if let tiffData = image.tiffRepresentation,
       let bitmap = NSBitmapImageRep(data: tiffData),
       let pngData = bitmap.representation(using: .png, properties: [:]) {
        try? pngData.write(to: URL(fileURLWithPath: path))
        print("Saved \(path)")
    }
}

// 1. Header Title: "PREMIUM SOLES FOR YOUR REQUIREMENTS"
func createHeaderTitle() -> NSImage {
    let width: CGFloat = 1080
    let height: CGFloat = 260
    let img = NSImage(size: NSSize(width: width, height: height))
    img.lockFocus()
    NSColor.clear.set()
    NSRect(origin: .zero, size: img.size).fill()
    
    // Line 1: "SOLES FOR YOUR"
    let font1 = NSFont(name: "Avenir Next Heavy", size: 52) ?? NSFont.boldSystemFont(ofSize: 52)
    let attrs1: [NSAttributedString.Key: Any] = [
        .font: font1,
        .foregroundColor: NSColor(red: 70/255.0, green: 75/255.0, blue: 90/255.0, alpha: 1.0),
        .kern: 3.0
    ]
    let str1 = NSAttributedString(string: "SOLES FOR YOUR", attributes: attrs1)
    let size1 = str1.size()
    str1.draw(at: NSPoint(x: (width - size1.width)/2, y: 145))
    
    // Line 2: "REQUIREMENTS"
    let font2 = NSFont(name: "Avenir Next Heavy", size: 84) ?? NSFont.boldSystemFont(ofSize: 84)
    let attrs2: [NSAttributedString.Key: Any] = [
        .font: font2,
        .foregroundColor: NSColor(red: 27/255.0, green: 36/255.0, blue: 74/255.0, alpha: 1.0), // Royal navy
        .kern: 6.0
    ]
    let str2 = NSAttributedString(string: "REQUIREMENTS", attributes: attrs2)
    let size2 = str2.size()
    str2.draw(at: NSPoint(x: (width - size2.width)/2, y: 40))
    
    img.unlockFocus()
    return img
}

savePNG(image: createHeaderTitle(), path: "assets/header_title.png")

// 2. Outro Title / Call To Action text
func createOutroCTA() -> NSImage {
    let width: CGFloat = 1080
    let height: CGFloat = 220
    let img = NSImage(size: NSSize(width: width, height: height))
    img.lockFocus()
    NSColor.clear.set()
    NSRect(origin: .zero, size: img.size).fill()
    
    let font1 = NSFont(name: "Avenir Next Bold", size: 32) ?? NSFont.boldSystemFont(ofSize: 32)
    let attrs1: [NSAttributedString.Key: Any] = [
        .font: font1,
        .foregroundColor: NSColor(red: 190/255.0, green: 140/255.0, blue: 30/255.0, alpha: 1.0),
        .kern: 4.0
    ]
    let str1 = NSAttributedString(string: "FOR INQUIRIES & BULK ORDERS", attributes: attrs1)
    let size1 = str1.size()
    str1.draw(at: NSPoint(x: (width - size1.width)/2, y: 140))
    
    let font2 = NSFont(name: "Noto Nastaliq Urdu", size: 36) ?? NSFont.systemFont(ofSize: 36)
    let attrs2: [NSAttributedString.Key: Any] = [
        .font: font2,
        .foregroundColor: NSColor(red: 30/255.0, green: 35/255.0, blue: 55/255.0, alpha: 1.0)
    ]
    let str2 = NSAttributedString(string: "معیاری جوتوں کے سول کی تیاری اور ہول سیل", attributes: attrs2)
    let size2 = str2.size()
    str2.draw(at: NSPoint(x: (width - size2.width)/2, y: 40))
    
    img.unlockFocus()
    return img
}

savePNG(image: createOutroCTA(), path: "assets/outro_cta.png")

// 3. Heritage Gold Seal
func createHeritageSeal() -> NSImage {
    let size: CGFloat = 400
    let img = NSImage(size: NSSize(width: size, height: size))
    img.lockFocus()
    NSColor.clear.set()
    NSRect(origin: .zero, size: img.size).fill()
    
    // Outer circle
    let outerRect = NSRect(x: 10, y: 10, width: size - 20, height: size - 20)
    let outerPath = NSBezierPath(ovalIn: outerRect)
    NSColor(red: 212/255.0, green: 160/255.0, blue: 23/255.0, alpha: 1.0).setStroke()
    outerPath.lineWidth = 7.0
    outerPath.stroke()
    
    // Inner dashed circle
    let innerRect = NSRect(x: 24, y: 24, width: size - 48, height: size - 48)
    let innerPath = NSBezierPath(ovalIn: innerRect)
    let dashes: [CGFloat] = [8.0, 6.0]
    innerPath.setLineDash(dashes, count: 2, phase: 0.0)
    NSColor(red: 27/255.0, green: 36/255.0, blue: 74/255.0, alpha: 0.8).setStroke()
    innerPath.lineWidth = 3.0
    innerPath.stroke()
    
    // Fill circle
    let fillRect = NSRect(x: 32, y: 32, width: size - 64, height: size - 64)
    let fillPath = NSBezierPath(ovalIn: fillRect)
    NSColor(red: 252/255.0, green: 252/255.0, blue: 254/255.0, alpha: 0.96).setFill()
    fillPath.fill()
    
    // Text: SINCE
    let f1 = NSFont(name: "Avenir Next Medium", size: 22) ?? NSFont.systemFont(ofSize: 22)
    let a1: [NSAttributedString.Key: Any] = [.font: f1, .foregroundColor: NSColor(red: 100/255.0, green: 110/255.0, blue: 130/255.0, alpha: 1.0), .kern: 3.5]
    let s1 = NSAttributedString(string: "TRUSTED SINCE", attributes: a1)
    s1.draw(at: NSPoint(x: (size - s1.size().width)/2, y: 245))
    
    // Text: 1980
    let f2 = NSFont(name: "Avenir Next Heavy", size: 76) ?? NSFont.boldSystemFont(ofSize: 76)
    let a2: [NSAttributedString.Key: Any] = [.font: f2, .foregroundColor: NSColor(red: 27/255.0, green: 36/255.0, blue: 74/255.0, alpha: 1.0), .kern: 3.0]
    let s2 = NSAttributedString(string: "1980", attributes: a2)
    s2.draw(at: NSPoint(x: (size - s2.size().width)/2, y: 155))
    
    // Text: OVER 40 YEARS EXCELLENCE
    let f3 = NSFont(name: "Avenir Next Demi Bold", size: 16) ?? NSFont.systemFont(ofSize: 16)
    let a3: [NSAttributedString.Key: Any] = [.font: f3, .foregroundColor: NSColor(red: 180/255.0, green: 130/255.0, blue: 23/255.0, alpha: 1.0), .kern: 2.0]
    let s3 = NSAttributedString(string: "40+ YEARS EXCELLENCE", attributes: a3)
    s3.draw(at: NSPoint(x: (size - s3.size().width)/2, y: 115))
    
    img.unlockFocus()
    return img
}

savePNG(image: createHeritageSeal(), path: "assets/heritage_seal.png")
