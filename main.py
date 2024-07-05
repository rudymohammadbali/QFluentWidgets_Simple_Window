import sys
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget, QLabel
from qfluentwidgets import FluentIcon, ScrollArea, ExpandLayout, SettingCardGroup, SwitchSettingCard, \
    OptionsSettingCard, CustomColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, isDarkTheme, InfoBar, \
    InfoBarPosition, Theme, setTheme, setThemeColor
from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont

from config import cfg, HELP_URL, YEAR, AUTHOR, VERSION, isWin11, FEEDBACK_URL

theme = 'dark' if isDarkTheme() else 'light'
STYLE_PATH = str(Path(__file__).parent / "resource" / "qss" / theme / "setting_interface.qss")


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        self.setObjectName(text.replace(' ', '-'))


class SettingInterface(ScrollArea):
    mica_enable_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.parent = parent

        self.scroll_widget = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widget)
        self.setting_label = QLabel(self.tr("Settings"), self)

        self.personal_group = SettingCardGroup(self.tr('Personalization'), self.scroll_widget)

        self.mica_card = SwitchSettingCard(
            FluentIcon.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            cfg.micaEnabled,
            self.personal_group
        )

        self.theme_card = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personal_group
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personal_group
        )

        self.about_group = SettingCardGroup(self.tr('About'), self.scroll_widget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FluentIcon.HELP,
            self.tr('Help'),
            self.tr('Discover new features and learn useful tips about UltraFetch'),
            self.about_group
        )
        self.feedback_card = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FluentIcon.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve UltraFetch by providing feedback'),
            self.about_group
        )
        self.about_card = PrimaryPushSettingCard(
            self.tr('Check update'),
            FluentIcon.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.about_group
        )

        self.__init_widget()

        self.setObjectName("settings_interface")

    def __init_widget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__set_qss()
        self.mica_card.setEnabled(isWin11())

        # initialize layout
        self.__init_layout()
        self.__connect_signal_to_slot()

    def __init_layout(self):
        self.setting_label.move(60, 63)

        # add cards to group
        self.personal_group.addSettingCard(self.mica_card)
        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)

        self.about_group.addSettingCard(self.helpCard)
        self.about_group.addSettingCard(self.feedback_card)
        self.about_group.addSettingCard(self.about_card)

        # add setting card group to layout
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)
        self.expand_layout.addWidget(self.personal_group)
        self.expand_layout.addWidget(self.about_group)

    def __set_qss(self):
        self.scroll_widget.setObjectName('scrollWidget')
        self.setting_label.setObjectName('settingLabel')

        with open(STYLE_PATH, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __show_restart_tooltip(self):
        InfoBar.warning(
            self.tr('Warning'),
            self.tr('Configuration takes effect after restart'),
            duration=5000,
            parent=self.window(),
            position=InfoBarPosition.BOTTOM_RIGHT
        )

    def __on_theme_changed(self, theme: Theme):
        setTheme(theme)

        self.__set_qss()

    def __check_update(self) -> None:
        pass

    def __connect_signal_to_slot(self):
        cfg.appRestartSig.connect(self.__show_restart_tooltip)
        cfg.themeChanged.connect(self.__on_theme_changed)

        self.mica_card.checkedChanged.connect(self.mica_enable_changed)
        self.theme_color_card.colorChanged.connect(setThemeColor)

        self.feedback_card.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

        self.about_card.clicked.connect(self.__check_update)


class Window(FluentWindow):
    """ Main Interface """

    def __init__(self):
        super().__init__()

        self.home_interface = Widget('Home Interface', self)
        self.setting_interface = SettingInterface(self)
        self.setting_interface.mica_enable_changed.connect(self.setMicaEffectEnabled)

        self.init_navigation()
        self.init_window()

    def init_navigation(self):
        self.addSubInterface(self.home_interface, FluentIcon.HOME, 'Home')
        self.addSubInterface(self.setting_interface, FluentIcon.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.resize(1280, 720)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('Simple Window')

        # Set Mica effect
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # Center window
        desktop = QApplication.desktop().availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.move(width // 2 - self.width() // 2, height // 2 - self.height() // 2)

    def closeEvent(self, event):
        pass

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
