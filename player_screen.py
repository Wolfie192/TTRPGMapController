from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QTransform, QPainter
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtSvgWidgets import QGraphicsSvgItem

class PlayerScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Player Screen")
        self.setGeometry(900, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-100000, -100000, 200000, 200000)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.view.setInteractive(False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.view)

        self.map_item = None
        self.zoom_factor = 1.0

    def _get_base_scale(self):
        if not self.map_item:
            return 1.0
        rect = self.map_item.boundingRect()
        if rect.width() <= 0 or rect.height() <= 0:
            return 1.0
        return min(self.view.viewport().width() / rect.width(), self.view.viewport().height() / rect.height())

    def load_map(self, file_path: str, rotation: float):
        self.scene.clear()
        if file_path:
            is_svg = file_path.lower().endswith('.svg')
            if is_svg:
                self.map_item = QGraphicsSvgItem(file_path)
            else:
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    print("Failed to load image in player screen.")
                    self.map_item = None
                    return
                self.map_item = QGraphicsPixmapItem(pixmap)

            self.scene.addItem(self.map_item)
            self.map_item.setTransformOriginPoint(self.map_item.boundingRect().center())
            self.map_item.setRotation(rotation)
            self.map_item.setPos(-self.map_item.boundingRect().center())
            self.view.centerOn(0, 0)
            self._apply_view_transform()

    def update_map_view(self, map_item_pos: QPointF, zoom_factor: float, rotation: float):
        if self.map_item is None:
            return

        self.zoom_factor = zoom_factor
        self.map_item.setPos(map_item_pos)
        self.map_item.setRotation(rotation)
        self._apply_view_transform()

    def _apply_view_transform(self):
        if not self.map_item:
            return
        base = self._get_base_scale()
        total_scale = base * self.zoom_factor
        self.view.setTransform(QTransform().scale(total_scale, total_scale))
        self.view.centerOn(0, 0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11 or event.key() == Qt.Key.Key_F:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.map_item:
            self._apply_view_transform()