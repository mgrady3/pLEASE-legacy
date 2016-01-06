class PyLeemStyles(object):
    """
    """
    def __init__(self):
        """
        initialize css strings
        zip strings in to dict with key,value pairs
        """
        but_style = """
            QPushButton {
                color: #333;
                color: #333;
                border: 2px solid #555;
                border-radius: 11px;
                padding: 5px;
                background: qradialgradient(cx: 0.3, cy: -0.4,
                fx: 0.3, fy: -0.4,
                radius: 1.35, stop: 0 #fff, stop: 1 #888);
                min-width: 80px;
                }
        """
        group_style = """
            QGroupBox {
                background-color: rgb(48, 47, 47);
                border: 8px solid rgb(108, 122, 137);
                border-radius: 8px
                }
        """
        tab_style = """
            QTabBar {
                tab:
                    width: 250;
                font-size: 18;
                font-family: Courier;
                }
        """
        can_style = """
            QGroupBox {
                background-color: rgb(48, 47, 47);
                border: 8px solid rgb(108, 122, 137);
                border-radius: 8px
                }
        """
        # Thanks to JazzyCamel in the Qt help forums
        menu_style = """
            QMenuBar {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
            border: 1px solid #000;
        }

        QMenuBar::item {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
        }

        QMenuBar::item::selected {
            background-color: rgb(30,30,30);
        }

        QMenu {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
            border: 1px solid #000;
        }

        QMenu::item::selected {
            background-color: rgb(30,30,30);
        }

        """
        keys = ['tab', 'can', 'group', 'menu', 'but']
        values = [tab_style, can_style, group_style, menu_style, but_style]

        self.css_dict = dict(zip(keys, values))

    def get_styles(self):
        """
        getter method for accessing the css_dict
        """
        return self.css_dict
