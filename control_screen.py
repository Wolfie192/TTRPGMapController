from PyQt6.QtWidgets import (
QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
QLabel, QFileDialog,  QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
QSlider, QLineEdit, QApplication
)
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform, QIntValidator, QPainter
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QBuffer, QIODevice
from PIL import Image
import io

class ControlScreen(QMainWindow):
    map_loaded = pyqtSignal(QPixmap)
    view_state_changed = pyqtSignal(QPointF, float)
    closing = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Screen")
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.scene = QGraphicsScene(self)
        self.view =  QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(self.view)

        self.pixmap_item = None
        self.original_pixmap = None

        self.control_view_scale = 1.0
        self.player_target_scale = 1.0

        self._pan = False
        self._pan_start_point = QPointF()

        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)

        self.load_map_button = QPushButton("Load Map")
        self.load_map_button.clicked.connect(self._load_map)
        controls_layout.addWidget(self.load_map_button)

        self.upscale_map_button = QPushButton("Upscale Map")
        self.upscale_map_button.clicked.connect(self._upscale_map)
        self.upscale_map_button.setEnabled(False)
        controls_layout.addWidget(self.upscale_map_button)

        self.recenter_map_button = QPushButton("Re-Center Maps")
        self.recenter_map_button.clicked.connect(self._recenter_map)
        self.recenter_map_button.setEnabled(False)
        controls_layout.addWidget(self.recenter_map_button)

        scale_label = QLabel("Map Scale:")
        controls_layout.addWidget(scale_label)

        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(30)
        self.minus_button.setObjectName("scaleMinusButton")
        self.minus_button.clicked.connect(self._decrease_player_scale)
        controls_layout.addWidget(self.minus_button)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 5000)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.valueChanged.connect(self._on_player_scale_slider_changed)
        controls_layout.addWidget(self.scale_slider)

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(30)
        self.plus_button.setObjectName("scalePlusButton")
        self.plus_button.clicked.connect(self._increase_player_scale)
        controls_layout.addWidget(self.plus_button)

        self.scale_input = QLineEdit("100")
        self.scale_input.setFixedWidth(60)
        self.scale_input.setValidator(QIntValidator(10, 5000))
        self.scale_input.editingFinished.connect(self._on_player_scale_input_finished)
        controls_layout.addWidget(self.scale_input)
        controls_layout.addWidget(QLabel("%"))

        self.view.mousePressEvent = self._view_mouse_press_event
        self.view.mouseMoveEvent = self._view_mouse_move_event
        self.view.mouseReleaseEvent = self._view_mouse_release_event
        self.view.wheelEvent = self._view_wheel_event

    def _load_map(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.original_pixmap = pixmap
                self._display_pixmap(pixmap)
                self.upscale_map_button.setEnabled(True)
                self.recenter_map_button.setEnabled(True)
            else:
                print("Failed to load image.")

    def _display_pixmap(self, pixmap: QPixmap):
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.pixmap_item.setPos(0, 0)
        self.view.setSceneRect(self.pixmap_item.boundingRect())

        self.view.setTransform(QTransform())
        self.control_view_scale = 1.0

        self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.control_view_scale = self.view.transform().m11()

        self.player_target_scale = 1.0
        self.scale_slider.setValue(100)
        self.scale_input.setText("100")

        self.map_loaded.emit(pixmap)
        self._emit_map_view_state()

    def _upscale_map(self):
        if self.original_pixmap is None:
            return

        factor = 2

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        self.original_pixmap.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data().data()))
        buffer.close()

        new_width = pil_image.width * factor
        new_height = pil_image.height * factor

        upscaled_pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

        img_byte_arr = io.BytesIO()
        upscaled_pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        new_pixmap = QPixmap()
        new_pixmap.loadFromData(img_byte_arr.getvalue(), 'PNG')

        if not new_pixmap.isNull():
            self._display_pixmap(new_pixmap)
        else:
            print("Failed to upscale image.")

    def _recenter_map(self):
        if self.pixmap_item is None:
            return

        self.view.setTransform(QTransform())
        self.control_view_scale = 1.0
        self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.control_view_scale = self.view.transform().m11()
        self.pixmap_item.setPos(0, 0)

        self._emit_map_view_state()

    def _view_mouse_press_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap_item:
            self._pan = True
            self._pan_start_point = self.view.mapToScene(event.position().toPoint())
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        super(QGraphicsView, self.view).mousePressEvent(event)

    def _view_mouse_move_event(self, event: QMouseEvent):
        if self._pan and self.pixmap_item:
            current_mouse_pos_scene = self.view.mapToScene(event.position().toPoint())
            delta_scene = current_mouse_pos_scene - self._pan_start_point

            self.pixmap_item.setPos(self.pixmap_item.pos() + delta_scene)

            self._pan_start_point = current_mouse_pos_scene
            self._emit_map_view_state()
        super(QGraphicsView, self.view).mouseMoveEvent(event)

    def _view_mouse_release_event(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = False
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self._emit_map_view_state()
        super(QGraphicsView, self.view).mouseReleaseEvent(event)

    def _view_wheel_event(self, event):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.view.scale(zoom_factor, zoom_factor)
            self.control_view_scale *= zoom_factor
        else:
            self.view.scale(1 / zoom_factor, 1 / zoom_factor)
            self.control_view_scale /= zoom_factor

        self._emit_map_view_state()
        super(QGraphicsView, self.view).wheelEvent(event)

    def _on_player_scale_slider_changed(self, value):
        self.player_target_scale = value / 100.0
        self.scale_input.setText(str(value))
        self._emit_map_view_state()

    def _on_player_scale_input_finished(self):
        try:
            value = int(self.scale_input.text())
            if 10 <= value <= 5000:
                self.scale_slider.setValue(value)
            else:
                self.scale_input.setText(str(self.scale_slider.value()))
        except ValueError:
            self.scale_input.setText(str(self.scale_slider.value()))

    def _increase_player_scale(self):
        step = 10 if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        current_value = self.scale_slider.value()
        new_value = min(self.scale_slider.maximum(), current_value + step)
        self.scale_slider.setValue(new_value)

    def _decrease_player_scale(self):
        step = 10 if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier else 1
        current_value = self.scale_slider.value()
        new_value = min(self.scale_slider.maximum(), current_value - step)
        self.scale_slider.setValue(new_value)

    def _emit_map_view_state(self):
        if self.pixmap_item:
            self.view_state_changed.emit(self.pixmap_item.pos(), self.player_target_scale)

    def closeEvent(self, event):
        self.closing.emit()
        super().closeEvent(event)