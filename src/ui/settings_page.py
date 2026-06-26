"""设置页面 —— API 配置"""

import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from storage.app_settings import load_settings, save_settings, AppSettings
from ai.llm_client import test_connection

# 预设模型列表
PRESET_MODELS = [
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "deepseek-reasoner",
    "qwen-turbo-latest",
    "qwen-plus-latest",
    "glm-4-plus",
    "gpt-4o",
    "gpt-4o-mini",
    "claude-sonnet-4-6",
    "claude-fable-5",
    "—— 自定义 ——",
]

# 模型 → API 地址映射（切换模型时自动填充）
MODEL_ENDPOINTS = {
    "deepseek": "https://api.deepseek.com",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "glm": "https://open.bigmodel.cn/api/paas/v4",
    "gpt": "https://api.openai.com/v1",
    "claude": "https://api.anthropic.com",
}

def _get_endpoint_for_model(model_name: str) -> str | None:
    """根据模型名推断 API 地址"""
    for prefix, endpoint in MODEL_ENDPOINTS.items():
        if model_name.startswith(prefix):
            return endpoint
    return None


class SettingsPage:
    """设置标签页"""

    def __init__(self, parent: ttk.Notebook):
        self.frame = ttk.Frame(parent)
        self._custom_model = ""  # 用户手动输入的自定义模型名

        # ── 标题 ──
        title = ttk.Label(
            self.frame, text="AI 解读设置",
            font=("楷体", 17, "bold")
        )
        title.pack(pady=(24, 8), padx=40, anchor=W)

        hint = ttk.Label(
            self.frame,
            text="配置大模型 API 后可使用 AI 解卦。支持 DeepSeek 及所有 OpenAI 兼容接口。\n"
                 "API 密钥仅保存在您的本地电脑上，不会上传到任何服务器。",
            font=("等线", 10),
            foreground="#999999"
        )
        hint.pack(pady=(0, 20), padx=40, anchor=W)

        # ── API 密钥 ──
        key_frame = ttk.Frame(self.frame)
        key_frame.pack(fill=X, padx=40, pady=6)
        ttk.Label(key_frame, text="API 密钥", width=14, anchor=E,
                  font=("等线", 10)).pack(side=LEFT, padx=(0, 10))
        self.api_key_var = ttk.StringVar()
        self.api_key_entry = ttk.Entry(
            key_frame, textvariable=self.api_key_var, show="*", width=55,
            font=("等线", 10),
        )
        self.api_key_entry.pack(side=LEFT)

        # ── API 地址 ──
        url_frame = ttk.Frame(self.frame)
        url_frame.pack(fill=X, padx=40, pady=6)
        ttk.Label(url_frame, text="API 地址", width=14, anchor=E,
                  font=("等线", 10)).pack(side=LEFT, padx=(0, 10))
        self.api_endpoint_var = ttk.StringVar()
        self.api_endpoint_entry = ttk.Entry(
            url_frame, textvariable=self.api_endpoint_var, width=55,
            font=("等线", 10),
        )
        self.api_endpoint_entry.pack(side=LEFT)

        # ── 模型选择 ──
        model_frame = ttk.Frame(self.frame)
        model_frame.pack(fill=X, padx=40, pady=6)
        ttk.Label(model_frame, text="模型选择", width=14, anchor=E,
                  font=("等线", 10)).pack(side=LEFT, padx=(0, 10))

        # 下拉框
        self.model_combo_var = ttk.StringVar()
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_combo_var,
            values=PRESET_MODELS,
            state="readonly",
            width=30,
            font=("等线", 10),
        )
        self.model_combo.pack(side=LEFT)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)

        # 自定义模型输入框（选中"—— 自定义 ——"时显示）
        self.custom_entry_var = ttk.StringVar()
        self.custom_entry = ttk.Entry(
            model_frame, textvariable=self.custom_entry_var, width=25,
            font=("等线", 10),
        )
        # 默认隐藏，选中"自定义"时才显示
        self.custom_entry.pack(side=LEFT, padx=(8, 0))
        self.custom_entry.pack_forget()

        # ── 按钮行 ──
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=X, padx=40, pady=20)

        self.test_btn = ttk.Button(
            btn_frame, text=" 测试连接 ",
            command=self._test_connection,
            bootstyle="outline-info",
        )
        self.test_btn.pack(side=LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(
            btn_frame, text=" 保存设置 ",
            command=self._save,
            bootstyle="primary",
        )
        self.save_btn.pack(side=LEFT)

        # ── 状态提示 ──
        self.status_var = ttk.StringVar()
        self.status_label = ttk.Label(
            self.frame, textvariable=self.status_var,
            font=("等线", 9),
        )
        self.status_label.pack(pady=8, padx=40, anchor=W)

        # ── 分隔线 ──
        ttk.Separator(self.frame, orient=HORIZONTAL).pack(
            fill=X, padx=40, pady=20)

        # ── 关于 ──
        about_title = ttk.Label(
            self.frame, text="关于",
            font=("楷体", 17, "bold")
        )
        about_title.pack(pady=(5, 8), padx=40, anchor=W)

        about_text = (
            "易经占卜 v1.0\n"
            "基于《周易》通行本原文，包含完整的 64 卦卦辞、彖传、象传和爻辞。\n"
            "起卦方法：三铜钱法、随机数法\n"
            "AI 解读：支持 DeepSeek 等兼容 OpenAI 接口的大模型\n\n"
            "《周易》原文为公共领域古典文献。"
        )
        about_label = ttk.Label(
            self.frame, text=about_text,
            font=("等线", 10),
            foreground="#999999",
            justify=LEFT
        )
        about_label.pack(pady=5, padx=40, anchor=W)

        # 加载当前设置
        self.load_current_settings()

    # ── 模型选择逻辑 ──

    def _on_model_selected(self, event=None):
        """下拉框选择变化 —— 自动填充对应 API 地址"""
        selected = self.model_combo_var.get()
        if selected == "—— 自定义 ——":
            self.custom_entry.pack(side=LEFT, padx=(8, 0))
            self.custom_entry_var.set(self._custom_model)
        else:
            self.custom_entry.pack_forget()
            self._custom_model = ""  # 用预设值，清空自定义
            # 自动填充对应的 API 地址
            endpoint = _get_endpoint_for_model(selected)
            if endpoint:
                self.api_endpoint_var.set(endpoint)

    def _get_model_name(self) -> str:
        """获取当前选择的模型名称"""
        selected = self.model_combo_var.get()
        if selected == "—— 自定义 ——":
            return self.custom_entry_var.get().strip()
        return selected

    # ── 设置读写 ──

    def load_current_settings(self):
        """加载当前设置到表单"""
        settings = load_settings()
        self.api_key_var.set(settings.api_key)
        self.api_endpoint_var.set(settings.api_endpoint)

        # 判断当前模型是否在预设列表中
        model = settings.model_name
        if model in PRESET_MODELS and model != "—— 自定义 ——":
            self.model_combo_var.set(model)
            self.custom_entry.pack_forget()
        else:
            self.model_combo_var.set("—— 自定义 ——")
            self._custom_model = model
            self.custom_entry_var.set(model)
            self.custom_entry.pack(side=LEFT, padx=(8, 0))

        self.status_var.set("")

    def _save(self):
        """保存设置"""
        settings = AppSettings(
            api_key=self.api_key_var.get().strip(),
            api_endpoint=self.api_endpoint_var.get().strip(),
            model_name=self._get_model_name(),
        )
        save_settings(settings)
        self.status_var.set("✓ 设置已保存")
        self.status_label.configure(foreground="#2ecc71")

    # ── 连接测试 ──

    def _test_connection(self):
        """测试 API 连接"""
        self._save()
        self.test_btn.configure(state=DISABLED, text=" 正在测试... ")
        self.status_var.set("正在测试连接...")
        self.status_label.configure(foreground="#999999")

        def run_test():
            success, message = test_connection()
            self.frame.after(0, lambda: self._on_test_result(success, message))

        threading.Thread(target=run_test, daemon=True).start()

    def _on_test_result(self, success: bool, message: str):
        """测试结果回调"""
        self.test_btn.configure(state=NORMAL, text=" 测试连接 ")
        self.status_var.set(message)
        self.status_label.configure(foreground="#2ecc71" if success else "#e74c3c")
