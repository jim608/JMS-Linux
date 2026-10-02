# Arch Linux / EndeavourOS 安裝與發佈

本機制適用於 **x86_64 Arch Linux / EndeavourOS**；其他 Arch 衍生版仍需驗證套件版本與桌面服務。顯示名稱為 JMS，套件與終端命令使用小寫。

## 目前狀態

本倉庫提供 AUR 配方及本地軟體庫 staging 工具；**這不表示套件已在 AUR 上架或 pacman 軟體庫已啟用**。目前配方明確鎖定 `v0.11.1-jms.25` 測試版，不能將它宣稱為穩定版。安裝前閱讀該版 release notes。

- AUR 公開上架後：`yay -S jms-bin`
- 加入並信任維護者的簽章軟體庫後：`sudo pacman -Syu jms`（更新全系統，避免 Arch 部分升級）
- 啟動：應用程式選單 **JMS** 或 `jms`

`yay -S JMS`、`pacman -S JMS` 不是本方案的套件名稱。pacman 不會直接查詢 AUR。沒有軟體庫設定時，`pacman -S jms` 不會憑空找到 GitHub Releases。

## 安裝會處理什麼

makepkg / yay / pacman 透過宣告的 dependencies 安裝 MPV、GTK 3、ALSA、SQLite、libsecret、gnome-keyring、NetworkManager、Polkit 等。套件放在 `/opt/jms`，提供 `/usr/bin/jms`、選單捷徑及圖示。不使用 root 安裝腳本下載程式，也不改動使用者設定或刪除帳號資料。

安裝不會強制切換網路管理程式、啟用 systemd 服務、修改 PAM / 自動登入、解鎖 keyring、建立 Jellyfin 伺服器或代填帳密。桌面工作階段仍須有 D-Bus 和可用且已解鎖的 Secret Service；GNOME/KDE 等桌面設定不同，若登入保存失敗應先檢查 keyring。GPU、音訊、播放與真實桌面登入仍需實機測試。

## AUR 配方本機測試

先檢查 PKGBUILD 與下載來源，再以一般使用者執行（不要 sudo makepkg）：

```sh
sudo pacman -Syu --needed base-devel git
cd packaging/aur/jms-bin
makepkg --verifysource
makepkg --printsrcinfo > .SRCINFO
makepkg -si
```

配方固定版本與 SHA256，從發布的 portable payload 重新封裝，不另存或建置 Flutter 原始碼。共用程式仍由 JMS-Android 的 jms 分支維護。AUR 的 `jms-bin` 以 `provides=('jms=...')`、`conflicts=('jms')` 宣告與官方二進位 `jms` 的相同檔案用途；兩者不能同時安裝。套件管理員會要求確認替換，請勿用 `--overwrite '*'`。切回官方 jms 前亦須透過套件管理員移除 jms-bin，保留使用者資料。程式內建更新安裝可能切回官方 jms，因此 AUR 使用者請透過 yay 更新。

首次上架需要：

1. 確认 AUR 的 jms-bin 名稱可用，或取得既有維護者同意；不可覆蓋無關套件
2. 使用者的 AUR 帳號與已授權 SSH 金鑰（此程式不建立或上傳金鑰）
3. 先在隔離 Arch 執行 workflow 的建置、安裝與移除檢查，再完成桌面播放測試
4. 明確批准將 PKGBUILD、.SRCINFO、desktop 檔公開推送到 `ssh://aur@aur.archlinux.org/jms-bin.git`

上架時只將 `packaging/aur/jms-bin/` 內這三個檔案放進 AUR Git；不得上傳二進位、src/、pkg/ 或憑證。由 `makepkg --printsrcinfo` 更新 metadata；新版需確認 release manifest 與 artifact hash，更新版本、pkgrel、checksum，重新測試。pkgrel 目前與上游 versionCode 27 相同，以保留 packageVersion 的對應。

## pacman 簽章軟體庫

保留官方 release 的 `jms` 套件身份，不把 AUR 的 jms-bin 改名混發。本工具只建立本地待審閱目錄：

```sh
# 先從 release 的 SHA256SUMS / releases/*.json 核對套件
scripts/stage-arch-repo.sh JMS-Linux-0.11.1-jms.25-x86_64.pkg.tar.xz FULL_SIGNING_FINGERPRINT ./new-repo
```

需先備妥 Arch 的 repo-add、Python 3.11 以上、GnuPG，以及使用者已授權的發行者簽章金鑰。本工具不產生新金鑰、不保存密碼、不上傳、不改 pacman.conf。它核對本倉庫 release manifest 中的檔名與 SHA256，再檢查套件名稱 / 架構，簽署套件與資料庫並驗證簽章。它不替代 release 來源審查與完整測試，也不宣稱原始 release 本身已簽署。

公開前需要明確批准：

- 用哪個既有發行者金鑰簽署；公開完整 fingerprint 與公開金鑰的可靠驗證途徑
- 一個可持續維護的 HTTPS 靜態下載位置，承載 x86_64/ 中的 package、.sig、jms.db、jms.db.sig、jms.files 及相關檔案
- 發布整個已驗證 snapshot，先上傳套件再原子切換資料庫；保留舊套件讓升級中的使用者可下載
- 是否發布目前測試版；不要把測試版混入只提供穩定版的軟體庫

使用者必須自行核對並明確信任發行者金鑰，才能加入以下設定。不要用未知網址或未核對的 fingerprint。下方 URL 是待替换的範例，並非已上線服務：

```ini
[jms]
SigLevel = Required DatabaseRequired
Server = https://YOUR-VERIFIED-HOST/arch/$arch
```

不要設定 `SigLevel = Never` 或繞過簽章錯誤。金鑰 enrollment、pacman.conf 編輯與信任變更應由使用者明確批准。設定完成後 `sudo pacman -Syu jms`；後續正常 `sudo pacman -Syu` 即可一起更新。

## 驗證範圍

`python -m unittest discover -s tests -v` 檢查 metadata、release hash、依賴與 desktop。設定 `JMS_PORTABLE_ARCHIVE=/absolute/path/archive.tar.gz` 可在臨時目錄執行真實 payload 封裝並逐檔比對，**不安裝到本機**。

`scripts/print-srcinfo.sh` 使用官方 makepkg 產生 metadata；CI 做逐位元比對、Arch 容器建置、實際 pacman 安裝 / 移除以及 ELF 動態庫缺失檢查。CI 不發布、不簽署、不推送 AUR。不應把 metadata / staging 通過說成 Arch 實機播放通過。升級舊 jms、AUR 與 repo 互換、Secret Service、Polkit、Wayland/X11、音訊與 GPU 播放仍需專門的桌面測試。

參考：[PKGBUILD](https://man.archlinux.org/man/PKGBUILD.5.en)、[repo-add](https://man.archlinux.org/man/repo-add.8.en)、[pacman.conf](https://man.archlinux.org/man/pacman.conf.5.en)。
