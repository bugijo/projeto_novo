from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import (
    QTextCharFormat, QSyntaxHighlighter, QColor, QPainter, 
    QTextFormat, QFontMetrics, QFont
)
from PyQt6.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurar fonte
        font = QFont("Fira Code", 12)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Área de números de linha
        self.line_number_area = LineNumberArea(self)
        
        # Conectar sinais
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Configurar área de números de linha
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
        # Configurar editor
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(' ') * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Syntax highlighter
        self.highlighter = PythonHighlighter(self.document())

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, newBlockCount):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2b2b2b"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#7f7f7f"))
                painter.drawText(0, int(top), self.line_number_area.width(), 
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2f2f2f")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Palavras-chave
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#ff79c6"))
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield"
        ]
        self.add_mapping("\\b(" + "|".join(keywords) + ")\\b", keyword_format)
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#f1fa8c"))
        self.add_mapping('"[^"\\\\]*(\\\\.[^"\\\\]*)*"', string_format)
        self.add_mapping("'[^'\\\\]*(\\\\.[^'\\\\]*)*'", string_format)
        
        # Números
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#bd93f9"))
        self.add_mapping("\\b[0-9]+\\b", number_format)
        
        # Comentários
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272a4"))
        self.add_mapping("#[^\n]*", comment_format)
        
        # Funções
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#50fa7b"))
        self.add_mapping("\\bdef\\s+\\w+\\b", function_format)
        
        # Classes
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#8be9fd"))
        self.add_mapping("\\bclass\\s+\\w+\\b", class_format)

    def add_mapping(self, pattern, format):
        from PyQt6.QtCore import QRegularExpression
        self.highlighting_rules.append((QRegularExpression(pattern), format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format) 