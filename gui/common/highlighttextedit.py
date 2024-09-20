from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.token import Token
from qtpy.QtGui import QColor, QFont, QPalette, QSyntaxHighlighter, QTextCharFormat
from qtpy.QtWidgets import QPlainTextEdit


class HighlightTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        style_name = "monokai"

        font = QFont()
        font.setFamily("Menlo")
        font.setPointSize(14)
        font.setFixedPitch(True)

        self.apply_background_color(style_name)
        self.setFont(font)
        PygmentsSyntaxHighlighter(self.document(), style_name)

    def apply_background_color(self, style_name):
        """Set the background color of the editor based on the Pygments style."""
        style = get_style_by_name(style_name)
        style_bg_color = style.background_color
        style_for_text = style.style_for_token(Token.Text)
        style_for_comment = style.style_for_token(Token.Comment)

        palette = self.palette()

        bg_color = QColor(f"{style_bg_color}")
        text_color = QColor(f"#{style_for_text['color']}")
        comment_color = QColor(f"#{style_for_comment['color']}")
        palette.setColor(QPalette.ColorRole.Base, bg_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.PlaceholderText, comment_color)

        self.setPalette(palette)


class PygmentsSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, style_name):
        super().__init__(document)

        self.lexer = get_lexer_by_name("sql")
        self.style = get_style_by_name(style_name)

        self.format_map = self.create_format_map(self.style)

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        index = 0
        for token_type, token in lex(text, self.lexer):
            length = len(token)
            self.setFormat(index, length, self.format_map[token_type])
            index += length

    @staticmethod
    def create_format_map(style):
        def to_fmt(token_style):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(f"#{token_style['color']}"))
            if token_style["bold"]:
                fmt.setFontWeight(QFont.Weight.Bold)
            if token_style["italic"]:
                fmt.setFontItalic(True)
            return fmt

        return {token_type: to_fmt(token_style) for token_type, token_style in style}
