from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from lv_chordia_lab.domain.analysis_result import AnalysisResult
from lv_chordia_lab.domain.chord_event import ChordEvent


@dataclass(frozen=True, slots=True)
class _TimelineMetrics:
    pixels_per_second: float = 56.0
    height: float = 112.0
    top: float = 16.0


class _ChordRectItem(QGraphicsRectItem):
    def __init__(
        self,
        event: ChordEvent,
        rect: QRectF,
        on_selected,
    ) -> None:
        super().__init__(rect)
        self.event = event
        self._on_selected = on_selected
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(
            f"{event.chord}\n{event.start_time:.2f} — {event.end_time:.2f} s"
        )

    def mousePressEvent(self, event) -> None:
        self._on_selected(self.event)
        event.accept()


class TimelineView(QGraphicsView):
    seek_requested = Signal(float)
    event_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._metrics = _TimelineMetrics()
        self._result: AnalysisResult | None = None
        self._playhead: QGraphicsLineItem | None = None
        self._current_item: _ChordRectItem | None = None
        self._items_by_event: dict[ChordEvent, _ChordRectItem] = {}

        self.setMinimumHeight(165)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def set_result(self, result: AnalysisResult) -> None:
        self._result = result
        self._render()

    def set_position(self, seconds: float) -> None:
        if self._result is None or self._playhead is None:
            return

        x = seconds * self._metrics.pixels_per_second
        self._playhead.setLine(
            x,
            0,
            x,
            self._metrics.top + self._metrics.height,
        )

        event = self._result.chord_at(seconds)
        self._set_current_event(event)

        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        if x < viewport_rect.left() or x > viewport_rect.right():
            self.centerOn(QPointF(x, self._metrics.height / 2))

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.18 if event.angleDelta().y() > 0 else 1 / 1.18
            current = self.transform().m11()
            target = current * factor

            if 0.45 <= target <= 6.0:
                self.scale(factor, 1.0)

            event.accept()
            return

        super().wheelEvent(event)

    def _render(self) -> None:
        self._scene.clear()
        self._items_by_event.clear()
        self._current_item = None
        self._playhead = None

        if self._result is None:
            return

        app = QApplication.instance()
        palette = app.palette() if app is not None else None
        base_color = palette.highlight().color() if palette else QColor("#4B8BF4")
        text_color = palette.highlightedText().color() if palette else QColor("white")
        border_color = palette.mid().color() if palette else QColor("#777777")
        playhead_color = palette.text().color() if palette else QColor("#111111")

        duration = max(self._result.duration, 1.0)
        scene_width = duration * self._metrics.pixels_per_second
        scene_height = self._metrics.top + self._metrics.height + 28
        self._scene.setSceneRect(0, 0, scene_width, scene_height)

        for index, event in enumerate(self._result.chords):
            left = event.start_time * self._metrics.pixels_per_second
            width = max(1.5, event.duration * self._metrics.pixels_per_second)

            rect = QRectF(left, self._metrics.top, width, self._metrics.height)
            item = _ChordRectItem(event, rect, self._select_event)

            color = QColor(base_color)
            if event.chord == "N":
                color.setAlpha(75)
            else:
                color.setAlpha(120 if index % 2 else 150)

            item.setBrush(QBrush(color))
            item.setPen(QPen(border_color, 0.8))
            self._scene.addItem(item)
            self._items_by_event[event] = item

            if width >= 38:
                label = QGraphicsSimpleTextItem(event.chord)
                label.setBrush(QBrush(text_color))
                font = QFont()
                font.setBold(True)
                font.setPointSize(10)
                label.setFont(font)

                bounds = label.boundingRect()
                label.setPos(
                    left + max(6.0, (width - bounds.width()) / 2),
                    self._metrics.top + (self._metrics.height - bounds.height()) / 2,
                )
                label.setZValue(2)
                self._scene.addItem(label)

        self._playhead = self._scene.addLine(
            0,
            0,
            0,
            self._metrics.top + self._metrics.height,
            QPen(playhead_color, 2.0),
        )
        self._playhead.setZValue(10)

    def _select_event(self, event: ChordEvent) -> None:
        self.seek_requested.emit(event.start_time)
        self.event_selected.emit(event)

    def _set_current_event(self, event: ChordEvent | None) -> None:
        if self._current_item is not None:
            pen = self._current_item.pen()
            pen.setWidthF(0.8)
            self._current_item.setPen(pen)

        self._current_item = self._items_by_event.get(event) if event else None

        if self._current_item is not None:
            pen = self._current_item.pen()
            pen.setWidthF(3.0)
            self._current_item.setPen(pen)
