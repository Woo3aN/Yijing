"""设置页面 —— 全局 QSS 统一样式"""

import threading

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from storage.app_settings import load_settings, save_settings, AppSettings
from ai.llm_client import test_connection

PRESET_MODELS = [
    # DeepSeek
    "deepseek-v4-pro", "deepseek-v4-flash",
    # 通义千问
    "qwen3.7-plus", "qwen3.6-flash",
    # 智谱 GLM
    "glm-5.2", "glm-4.7-flash",
    # OpenAI
    "gpt-5.5", "gpt-5.4-mini",
    # Anthropic Claude
    "claude-fable-5", "claude-sonnet-4-6",
    # Kimi (月之暗面) — 2026.06 最新
    "kimi-k2.7-code", "kimi-k2.6", "kimi-k2.5",
    # MiniMax (海螺 AI) — 2026.06 最新
    "minimax-m3", "minimax-m2.7", "minimax-m2.5",
    # 小米 MiMo — 2026.06 最新
    "mimo-v2.5-pro", "mimo-v2.5",
    # 自定义
    "—— 自定义 ——",
]

MODEL_ENDPOINTS = {
    "deepseek": "https://api.deepseek.com",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "glm": "https://open.bigmodel.cn/api/paas/v4",
    "gpt": "https://api.openai.com/v1",
    "claude": "https://api.anthropic.com",
    "kimi": "https://api.moonshot.cn/v1",
    "minimax": "https://api.minimax.io/v1",
    "mimo": "https://api.xiaomimimo.com/v1",
}


def _get_endpoint(model: str) -> str | None:
    for prefix, ep in MODEL_ENDPOINTS.items():
        if model.startswith(prefix):
            return ep
    return None


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._custom_model = ""
        self._setup_ui()
        self.load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        card = QFrame()
        card.setObjectName("card")
        c = QVBoxLayout(card)
        c.setSpacing(12)

        title = QLabel("AI 解读设置")
        title.setObjectName("cardTitle")
        c.addWidget(title)

        hint = QLabel("配置大模型 API 后可使用 AI 解卦。支持 DeepSeek 及所有 OpenAI 兼容接口。\nAPI 密钥仅保存在您的本地电脑上，不会上传到任何服务器。")
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        c.addWidget(hint)

        # API Key
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        c.addWidget(self._row("API 密钥", self.api_key))

        # API Endpoint
        self.api_endpoint = QLineEdit()
        c.addWidget(self._row("API 地址", self.api_endpoint))

        # Model
        self.model_combo = QComboBox()
        self.model_combo.addItems(PRESET_MODELS)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        c.addWidget(self._row("模型选择", self.model_combo))

        self.custom_model = QLineEdit()
        self.custom_model.hide()
        c.addWidget(self._row("", self.custom_model))

        # 主题切换
        theme_row = QHBoxLayout()
        self.dark_btn = QPushButton("深 色")
        self.dark_btn.setObjectName("themeDark")
        self.dark_btn.setCheckable(True)
        self.dark_btn.setCursor(Qt.PointingHandCursor)
        self.dark_btn.clicked.connect(lambda: self._toggle_theme("dark"))
        theme_row.addWidget(self.dark_btn)
        self.light_btn = QPushButton("浅 色")
        self.light_btn.setObjectName("themeLight")
        self.light_btn.setCheckable(True)
        self.light_btn.setCursor(Qt.PointingHandCursor)
        self.light_btn.clicked.connect(lambda: self._toggle_theme("light"))
        theme_row.addWidget(self.light_btn)
        theme_row.addStretch()
        c.addWidget(self._row("界面主题", self._wrap_layout(theme_row)))

        # Buttons
        btn_row = QHBoxLayout()
        self.test_btn = QPushButton("测试连接")
        self.test_btn.setObjectName("outlineBtn")
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.clicked.connect(self._test)
        btn_row.addWidget(self.test_btn)

        save_btn = QPushButton("保存设置")
        save_btn.setObjectName("primaryBtn")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        c.addLayout(btn_row)

        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        c.addWidget(self.status_label)

        c.addStretch()
        layout.addWidget(card)

    def _wrap_layout(self, lo):
        w = QWidget()
        w.setLayout(lo)
        return w

    def _row(self, label, widget):
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        if label:
            lbl = QLabel(label)
            lbl.setFixedWidth(80)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setObjectName("settingLabel")
            row.addWidget(lbl)
        row.addWidget(widget, 1)
        return w

    def _toggle_theme(self, mode: str):
        self.dark_btn.setChecked(mode == "dark")
        self.light_btn.setChecked(mode == "light")
        self.theme_changed.emit("darkly" if mode == "dark" else "litera")

    def _on_model_changed(self, text):
        if text == "—— 自定义 ——":
            self.custom_model.show()
            self.custom_model.setText(self._custom_model)
        else:
            self.custom_model.hide()
            self._custom_model = ""
            ep = _get_endpoint(text)
            if ep:
                self.api_endpoint.setText(ep)

    def _get_model(self):
        sel = self.model_combo.currentText()
        return self.custom_model.text().strip() if sel == "—— 自定义 ——" else sel

    def load_settings(self):
        s = load_settings()
        self.api_key.setText(s.api_key)
        self.api_endpoint.setText(s.api_endpoint)
        model = s.model_name
        if model in PRESET_MODELS and model != "—— 自定义 ——":
            self.model_combo.setCurrentText(model)
            self.custom_model.hide()
        else:
            self.model_combo.setCurrentText("—— 自定义 ——")
            self._custom_model = model
            self.custom_model.setText(model)
            self.custom_model.show()
        theme = s.theme if hasattr(s, 'theme') else "darkly"
        is_dark = theme in ("darkly", "superhero", "solar", "cyborg", "vapor")
        self.dark_btn.setChecked(is_dark)
        self.light_btn.setChecked(not is_dark)
        self.status_label.setText("")

    def _save(self):
        s = AppSettings(
            api_key=self.api_key.text().strip(),
            api_endpoint=self.api_endpoint.text().strip(),
            model_name=self._get_model(),
            theme="darkly" if self.dark_btn.isChecked() else "litera",
        )
        save_settings(s)
        self.status_label.setText("✓ 设置已保存")

    def _test(self):
        self._save()
        self.test_btn.setEnabled(False)
        self.test_btn.setText("正在测试...")
        self.status_label.setText("正在测试连接...")

        def run():
            ok, msg = test_connection()
            self.test_btn.setEnabled(True)
            self.test_btn.setText("测试连接")
            self.status_label.setText(msg)

        threading.Thread(target=run, daemon=True).start()
