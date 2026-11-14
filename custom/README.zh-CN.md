# MHGU Recomp 简体中文维护分支

这是移植版 F1／手柄设置菜单的源码汉化，包含设置标签、帮助、按键、错误提示与联机通知。
游戏内文字由用户自己的游戏数据决定。没有把中文塞进 Spanish 槽位，Chinese 是独立语言，英语和西班牙语均保留。

源码维护在 `yshtonytc/MHGURecomp` 的 `chinese-ui` 分支。作者更新后无需再次 Fork：

```powershell
python custom/sync_upstream.py --tag latest --push
```

有冲突时先人工解决并提交；新增标签必须补充 `custom/zh-CN.json`，
再运行 `python custom/generate_catalog.py` 生成 `runtime/settings_zh.h`。
**MHGU Chinese Windows** 每 6 小时自动检查正式版，有新版或缺少成品才合并、验证并发布。
缺翻译、冲突或构建失败就停止，不推送半成品；无更新时跳过 Windows 构建。
手动 `check_only` 只检查，人工修复后可勾选 `publish` 发布。
预发行版只在明确指定标签时处理，保留 prerelease 标记，不自动降级至较旧正式版。

本机双击 `升级中文版.cmd`，或使用血源工作区的 `升级两个游戏.cmd`，直接安装已验证成品。
已安装相同或更高版本时立即结束，不重复下载、编译或实测游戏。

中文版本号在官方版本后加一位，例如上游 0.16.0 → 0.16.0.1，
同一上游下的汉化修订可递增末位。这样既不覆盖上游标签，也能让自有更新器识别修订。
本分支更新器只访问自己的 Release，不会自动更新成未汉化的官方程序。

构建不需要也不上传游戏 dump：只编译开源主程序、更新器，
其余公开程序库从对应官方 Release 验证 SHA-256 后取得，并核对 GAMELIB_ID。
上游标识包含源码换行字节；`align_gamelib.py` 只接受相同 ABI 源码和编译参数的
LF／CRLF 两种哈希中，同时出现在官方主程序及程序库的那一个。不会取消运行时匹配检查。
公开包不含个人 exefs／romfs、存档、模组、缓存和配置。

中文字体优先加载系统字体；无系统中文字体时使用随包的 Noto Sans SC，
其原始文件与 SIL OFL 1.1 许可证地址、提交和哈希记录在 `custom/font.json`。
不随包分发微软雅黑。代码保留上游 MIT 许可和作者署名。

本机从旧版二进制汉化迁移时，退出游戏后只需把 INI 的 Application/Language 改为 Chinese，
其余画质、帧率、输入、网络和游戏语言设置保留。旧 F1_Chinese_Font 模组可继续保留，但已不是必需项。
