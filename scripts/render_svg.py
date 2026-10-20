from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication([])
source = Path(sys.argv[1])
renderer = QSvgRenderer(str(source))
size = renderer.defaultSize()
image = QImage(size.width(), size.height(), QImage.Format_ARGB32)
image.fill(Qt.white)
painter = QPainter(image)
renderer.render(painter)
painter.end()
if not image.save(str(source.with_suffix('.png'))):
    raise RuntimeError('Cannot save preview')
