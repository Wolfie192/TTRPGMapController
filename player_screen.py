from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QTransform, QPainter
from PyQt6.QtCore import Qt, QPointF

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
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.view.setInteractive(False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.view)

        self.pixmap_item = None

    def load_map(self, pixmap: QPixmap):
        self.scene.clear()
        if not pixmap.isNull():
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            self.view.setSceneRect(self.pixmap_item.boundingRect())
            self.pixmap_item.setPos(0, 0)

    def update_map_view(self, map_item_pos: QPointF, scale_factor: float):
        if self.pixmap_item is None:
            return

        transform = QTransform()
        transform.scale(scale_factor, scale_factor)
        self.view.setTransform(transform)

        self.pixmap_item.setPos(map_item_pos)