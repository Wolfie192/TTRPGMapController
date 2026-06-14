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
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setInteractive(False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.view)

        self.map_item = None

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
            self.map_item.setPos(0, 0)
            self.view.setSceneRect(self.map_item.sceneBoundingRect())

    def update_map_view(self, map_item_pos: QPointF, scale_factor: float, rotation: float):
        if self.map_item is None:
            return

        transform = QTransform()
        transform.scale(scale_factor, scale_factor)
        self.view.setTransform(transform)

        self.map_item.setPos(map_item_pos)
        self.map_item.setRotation(rotation)