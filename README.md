# JMS Linux

JMS（Jim608 Media Server）基於 [DonutWare/Fladder](https://github.com/DonutWare/Fladder)，使用 GPLv3 授權並保留原作者與第三方署名。

本倉庫專門提供 **EndeavourOS／Arch Linux x86_64** 發布與更新資訊，不宣稱支援所有 Linux 發行版。

## 下載與安裝

目前測試版：[JMS 0.11.1-jms.31](https://github.com/jim608/JMS-Linux/releases/tag/v0.11.1-jms.31)，完整 App 版本為 `0.11.1-jms.31+33`。下載前閱讀版本說明，並使用同版的 [SHA256SUMS.txt](https://github.com/jim608/JMS-Linux/releases/download/v0.11.1-jms.31/SHA256SUMS.txt) 核對檔案。

- [官方 pacman 安裝套件](https://github.com/jim608/JMS-Linux/releases/download/v0.11.1-jms.31/JMS-Linux-0.11.1-jms.31-x86_64.pkg.tar.xz)，套件名稱為 `jms`。
- [可攜式套件](https://github.com/jim608/JMS-Linux/releases/download/v0.11.1-jms.31/JMS-Linux-0.11.1-jms.31-x64.tar.gz)，仍需系統依賴。
- [本機 yay／makepkg 配方](https://github.com/jim608/JMS-Linux/releases/download/v0.11.1-jms.31/JMS-Linux-0.11.1-jms.31-jms-bin-aur.tar.gz)，內含 `PKGBUILD`、`.SRCINFO` 與繁體中文說明，套件名稱為 `jms-bin`。

在已完成正常系統更新的環境，使用官方安裝套件：

```bash
sudo pacman -U ./JMS-Linux-0.11.1-jms.31-x86_64.pkg.tar.xz
```

使用本機配方時，解開至全新目錄並閱讀 `jms-bin/PKGBUILD`。yay 13 的本機建置流程需要可核對的 Git 工作目錄；在解開封存後、包含 `jms-bin` 的目錄，以一般使用者建立僅含配方的本機提交。不要重設既有 Git 倉庫，提交身分可換成自己的公開 noreply 身分：

```bash
git init --initial-branch=jms-local ./jms-bin
git -C ./jms-bin add -- PKGBUILD .SRCINFO README.zh-Hant.md
git -C ./jms-bin -c user.name=jim608 -c user.email=60721672+jim608@users.noreply.github.com commit -m "chore(package): 核對 JMS Linux 本機配方"
git -C ./jms-bin branch jms-local-source
git -C ./jms-bin branch --set-upstream-to=jms-local-source jms-local
```

兩個分支指向相同的本機配方提交，不設定遠端，也不推送任何內容。完成後執行：

```bash
yay -Bi ./jms-bin
```

未使用 yay 時，也可進入 `jms-bin` 目錄執行 `makepkg --verifysource`，再執行 `makepkg -si`。配方固定下載同一版本的官方二進位，核對 SHA256、版本、來源提交與 Build ID，不重新編譯 App。

**本機配方尚未刊登 AUR，不能使用 `yay -S jms-bin`。** 後續升級需下載新版配方後再次執行。`jms-bin` 與官方 `jms` 互斥，切換時須由使用者明確確認；不主動刪除使用者的 JMS 設定。

## 更新與服務

Linux 更新資訊為 `update-linux.json`，只使用本倉庫的公開 Release。測試版需開啟「接收測試版」；自動檢查更新不等於自動下載或安裝。官方 `jms` 安裝由 PolicyKit 與 pacman 執行，須有桌面驗證代理；`jms-bin` 安裝者使用本機配方手動更新，App 不會默默切換套件渠道。

本版需要 glibc 2.36 以上、MPV、GTK 3、ALSA、桌面 D-Bus／NetworkManager，以及已解鎖的 Secret Service（gnome-keyring）。Seerr 工作階段使用安全儲存，無可用安全服務時不以明文保存。

可直接設定 Jellyfin，也可輸入管理者提供的 JMS HTTPS 網站入口以取得服務設定。本人登入、帳號與服務來源隔離；手動設定保留優先權。診斷回報須另行同意，入口不能自行開啟上傳。

可選擇分享 Discord 播放／暫停狀態，每個 JMS 帳號預設關閉，影片名稱另需同意。Discord 桌面版須在同一台電腦開啟並登入；停止播放、登出、切換帳號或進入隱身模式時清除狀態。Discord 未開啟或連線失敗不影響播放。實際 Discord 個人檔案顯示仍待使用者裝置驗證；本版未提供 Flatpak 套件。

本版未提供正式發行者簽章，安裝遵循本機 pacman 信任政策，不自動降低檢查。隔離 Arch 驗證涵蓋套件、啟動、升級、本機 yay 配方與設定保留；實體 EndeavourOS／Arch 的 GPU 播放、本人登入與互動式 PolicyKit 授權仍待驗證。

## 共用來源與其他平台

完整 Flutter 原始碼只維護於 [JMS-Android 的 jms 分支](https://github.com/jim608/JMS-Android/tree/jms)。本倉庫不另存一份 `lib/`。本版共用來源提交為 [`8f2f9960cc4f8c70eedf8da315a82c2675a5fcf7`](https://github.com/jim608/JMS-Android/commit/8f2f9960cc4f8c70eedf8da315a82c2675a5fcf7)，Build ID 為 `JMS-0.11.1-jms.31-linux-8f2f9960cc4f`。

各版本另附真正對應 sourceCommit 的完整來源 ZIP、原生依賴材料與授權。GitHub 自動產生的 Source code.zip 僅含此發布倉庫文件，不能代替共用 Flutter 完整來源。

Windows 請使用 [JMS-Desktop](https://github.com/jim608/JMS-Desktop)，Android 請使用 [JMS-Android](https://github.com/jim608/JMS-Android)。不同平台不互相作為更新備援。
