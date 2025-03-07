'''
Created on 24-Jan-2025

@author: kayma
'''
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsDropShadowEffect 
from PyQt5.QtGui import QColor , QFont
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextCharFormat
from Qt import QtCore, QtWidgets

class KNELib():
    
    def nodeSetShadow(self, node):
        shadow_effect = QGraphicsDropShadowEffect() 
        shadow_effect.setBlurRadius(15) 
        shadow_effect.setColor(QColor("black")) 
        shadow_effect.setOffset(3, 3)          
        node.view.setGraphicsEffect(shadow_effect)
        node.update()        

    def nodeChangeLabelFontSize(self, node, fontSize=10):
        font = QFont()
        font.setFamily("Consolas")
        font.setBold(1)
        
        # #CHar Spacing
        # spacing = 10
        #
        #
        # doc = node.view.text_item.document()
        # cursor = QTextCursor(doc)
        #
        # # Set the text character format to include character spacing
        # char_format = QTextCharFormat()
        # char_format.setFontLetterSpacing(spacing)

        # Insert the text with the custom character spacing
        #cursor.insertText(text, char_format)

        # Set the QTextDocument to the QGraphicsTextItem
        #self        
        
        node.view.text_item.setFont(font)
        node.update()

    def nodeIOLabelFontSize(self, node, fontSize=10):
        font = QFont()
        font.setPointSize(fontSize)
        
        if hasattr(node,'inputs_ports'):
            for ip in node.inputs_ports():
                lblItm = node.view._input_items[ip.view]
                lblItm.setFont(font)
                
        if hasattr(node,'output_ports'):
            for op in node.output_ports():
                lblItm = node.view._output_items[op.view]
                lblItm.setFont(font)
        
        node.view.height = 400
        node.view.draw_node()
        node.update()   
        
    def nodeOverride_mouseDoubleClickEvent(self, event):
        """
        Re-implemented to emit "node_double_clicked" signal.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        if event.button() == QtCore.Qt.LeftButton:
            if not self.disabled:
                # enable text item edit mode.
                items = self.scene().items(event.scenePos())
                if self._text_item in items:
                    self._text_item.set_editable(True)
                    self._text_item.setFocus()
                    event.ignore()
                    return

            viewer = self.viewer()
            if viewer:
                viewer.node_double_clicked.emit(self.id)
        super(NodeItem, self).mouseDoubleClickEvent(event)         