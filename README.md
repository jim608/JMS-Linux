# JMS Linux

JMS（Jim608 Media Server）基於 [DonutWare/Fladder](https://github.com/DonutWare/Fladder)，使用 GPLv3 授權並保留原作者與第三方署名。

本倉庫專門提供 **EndeavourOS／Arch Linux x86_64** 發布與更新資訊，不宣稱支援所有 Linux 發行版。

## 下載與更新

請從 [Releases](https://github.com/jim608/JMS-Linux/releases) 下載 pacman 套件或可攜式套件，依 SHA256SUMS.txt 核對檔案。測試版不會推送給僅接收穩定版的使用者；自動檢查更新不等於自動安裝。

更新資訊為 `update-linux.json`。需要 glibc 2.36 以上、MPV、GTK 3、ALSA、桌面 D-Bus／NetworkManager，以及已解鎖的 Secret Service（gnome-keyring）。Seerr 工作階段使用安全儲存，無可用安全服務時不以明文保存。

本次驗證使用隔離 Arch 桌面環境；實體 EndeavourOS 的 GPU 播放、登入及 Polkit 安裝互動仍需驗證。詳細限制以各版本說明為準。

## 共用來源與其他平台

完整 Flutter 原始碼只維護於 [JMS-Android 的 jms 分支](https://github.com/jim608/JMS-Android/tree/jms)。本倉庫不另存一份 lib/。每版附件提供精確 sourceCommit 對應的完整來源 ZIP、原生依賴材料與授權；GitHub 自動 Source code.zip 僅含此發布倉庫文件。

Windows 請使用 [JMS-Desktop](https://github.com/jim608/JMS-Desktop)，Android 請使用 [JMS-Android](https://github.com/jim608/JMS-Android)。不同平台不互相作為更新備援。
