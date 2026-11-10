# MHGU Recomp 简体中文维护分支

这是移植版 F1／手柄设置菜单的源码汉化，包含设置标签、帮助、按键、错误提示与联机通知。
游戏内文字由用户自己的游戏数据决定。没有把中文塞进 Spanish 槽位，Chinese 是独立语言，英语和西班牙语均保留。

源码维护在 `yshtonytc/MHGURecomp` 的 `chinese-ui` 分支。作者更新后无需再次 Fork：

```powershell
python custom/sync_upstream.py --tag latest --push
```

有冲突时先人工解决并提交；新增标签必须补充 `custom/zh-CN.json`，
再运行 `python custom/generate_catalog.py` 生成 `runtime/settings_zh.h`。
推送后 Actions 构建检查；手动运行 **MHGU Chinese Windows** 并勾选 publish，验证成功才发布。

中文版本号在官方版本后加一位，例如上游 0.16.0 → 0.16.0.1，
同一上游下的汉化修订可递增末位。这样既不覆盖上游标签，也能让自有更新器识别修订。
本分支更新器只访问自己的 Release，不会自动更新成未汉化的官方程序。

构建不需要也不上传游戏 dump：只编译开源主程序、更新器，
其余公开程序库从对应官方 Release 验证 SHA-256 后取得，并核对 GAMELIB_ID。
公开包不含个人 exefs／romfs、存档、模组、缓存和配置。

中文字体优先加载系统字体；无系统中文字体时使用随包的 Noto Sans SC，
其原始文件与 SIL OFL 1.1 许可证地址、提交和哈希记录在 `custom/font.json`。
不随包分发微软雅黑。代码保留上游 MIT 许可和作者署名。

本机从旧版二进制汉化迁移时，退出游戏后只需把 INI 的 Application/Language 改为 Chinese，
其余画质、帧率、输入、网络和游戏语言设置保留。旧 F1_Chinese_Font 模组可继续保留，但已不是必需项。
