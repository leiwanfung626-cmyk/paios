# OpenWrt 二级路由搬移后 Clash / AdGuard 不生效 — 修复 SOP

## 适用场景
- 拓扑:光猫 → 主路由(LAN 出) → 二楼 OpenWrt(WAN 入,LAN + WiFi 出)
- 一楼设备直连主路由,不过代理;二楼 LAN / WiFi 经 OpenWrt 走 Clash + AdGuard
- 症状:OpenWrt 从一楼挪到二楼(或换接入端口 / 换交换机口)后,WAN 口 IP 变化,代理与去广告失效

## 根因(已验证典型)
OpenWrt 的 WAN 网段随接入位置改变(例:一楼 `192.168.1.x` → 二楼 `192.168.0.x`),
但配置中**写死了旧网段地址**(尤其 WAN 的 DNS 仍是旧网关 `192.168.1.1`),导致:

1. OpenWrt 系统 DNS 解析打到不可达死地址 → 超时;
2. 二楼设备的查询经 AdGuard / Clash 转上来,上游也指向死地址 → 解析失败;
3. 表现 = 去广告和代理"都不起作用"。

二楼作为二级路由,客户端网关 / DNS 天然是 OpenWrt 的 LAN IP,**无需改 DHCP 下发**。
只要清掉旧网段死地址、WAN 用 DHCP 自动获取 + 公共 DNS,即可恢复。

## 诊断
SSH 到 OpenWrt 执行:
```bash
# 1) 全局扫描所有写死的旧网段地址(把 192.168.1 换成你的旧网段)
grep -rIn "192.168.1\." /etc/ 2>/dev/null
# 2) 看 WAN 当前状态(协议 / 地址 / 网关)
ifstatus wan | jsonfilter -e '@.proto' -e '@["ipv4-address"][0].address' -e '@.route[0].nexthop'
# 3) 看系统 DNS 当前值
cat /etc/resolv.conf
```
若 grep 命中 `192.168.1.1` 出现在 network / adguardhome / clash 等配置,即为元凶。

## 修复:WAN DNS(关键一步)
```bash
# 不用对端(主路由)通告的 DNS,避免其下发混乱值
uci set network.wan.peerdns='0'
# 清空并重写为公共 DNS(彻底删掉旧网段死地址)
uci del network.wan.dns
uci add_list network.wan.dns='223.5.5.5'
uci add_list network.wan.dns='119.29.29.29'
uci commit network
service network restart   # 可能短暂断 SSH,重连即可;温和替代: ubus call network reload
```
若 `uci set network.wan...` 报 "Configuration ... not found",先用 `uci show network | grep -i wan` 确认实际接口名(通常为 `wan`)。

## AdGuard Home 清理
- 后台:服务 → AdGuard Home → 设置 → DNS 设置 → 上游 DNS 服务器
- 删除任何 `192.168.1.x`,填公共 DNS(同上)
- 监听接口:LAN 或 `0.0.0.0`,端口 53
- 确认 OpenWrt 自带 dnsmasq 已让位 53(否则端口冲突)
- 命令行定位配置:`grep -rIn "192.168.1\." /etc/adguardhome/ /etc/config/ 2>/dev/null`

## Clash(OpenClash / Nikki)清理
- DNS / nameserver / fallback:删除 `192.168.1.x`,改用公共 DNS
- 运行模式:TProxy 或 Redir-Host 透明代理(非"仅本地")
- 监听绑定 `0.0.0.0` 或 LAN 接口,**不要**绑旧 WAN IP
- 防火墙:确保 Clash 服务启用,LAN → WAN 转发接受,透明重定向规则已挂载

## 验证(二楼设备)
```bash
# 路由器侧
ping -c3 223.5.5.5
nslookup www.baidu.com        # 应返回 IP,且 resolv.conf 中无 192.168.1.x
# 二楼客户端
ipconfig /all                 # 默认网关 / DNS = OpenWrt LAN IP(如 192.168.2.1)
```
- AdGuard「查询日志」出现二楼设备请求 → 去广告生效
- Clash「连接」面板有实时流量 → 代理生效

## 防复发原则
- **WAN 侧任何地址都不写死**:WAN 用 DHCP 客户端自动获取;上游 DNS 用公共 DNS。
- WAN IP 是租约制(会过期续租 / 变更),依赖固定 WAN IP 的配置必崩。
- 搬楼层 / 换端口后,第一动作 = 全局 grep 旧网段 + 清 WAN DNS。

## 实战补充(本次真实修复记录)

> 实际环境:iStoreOS + **Nikki(mihomo 内核)** 透明代理 + **AdGuardHome** 去广告。
> 链路:`客户端 → dnsmasq(:53) → AdGuardHome(:5353 过滤) → 上游 Nikki(:1053) → fake-ip 路由`。

### 拓扑校正:管理入口在 LAN,不在 WAN
- 本机(PAIOS 机器)实际在二楼 OpenWrt 的 LAN 下(网段 `192.168.1.x`,网关 `192.168.1.1`)。
- OpenWrt 的 SSH(dropbear)**默认只监听 WAN 接口**,不监听 LAN。所以:
  - 用 WAN IP(`192.168.0.x`)能 SSH,但 WAN 是 DHCP 租约,重启 / 续租后 IP 变 → 通道断;
  - 正确做法:管理入口用 **LAN IP `192.168.1.1`**(OpenWrt 静态地址,不随 WAN 变);
  - 改法:LuCI → 系统 → 管理权 → SSH 访问 → 接口,下拉从 `wan` 改 `lan`(或留空监听全部) → 保存应用。
- 之后 `ssh root@192.168.1.1` 稳定连接,**无需去主路由绑固定 IP**。

### 关键坑:AdGuard 规则从未下载成功(去广告"开了但不拦")
现象:AdGuard「启用」标记都在,但广告域名返回 Clash 的 fake-ip(`198.18.x`)而非被拦截。链路其实通(`dnsmasq:53 → AdGuard:5353 → 上游 Nikki`),只是**规则文件是空的**。

根因链(实测):
1. WAN 坏 DNS 时期 AdGuard 首次下载规则失败,且数据目录在 **`/tmp/lib/adguardhome/`**(重启丢失);
2. 修好 WAN DNS 后 `filters/` 仍空 → 重启 AdGuard 仍下不到;
3. 路由器**本机进程出站**(AdGuard/curl)走 OUTPUT 链→直连 WAN,而 Nikki 的 tproxy 只劫持"转发流量",**不劫持本机自身发起的流量**;
4. 被墙的 filter 源(`adguardteam.github.io`、`anti-ad.net`)在本机直连下超时 → 永远下不下来。

诊断铁证:
```bash
ls -la /tmp/lib/adguardhome/data/filters/      # 空 = 没下载
curl -m10 https://raw.githubusercontent.com/...  # 本机 000 / 超时(被墙)
nslookup adguardteam.github.io                 # 被墙类域名解析失败
```

修复(持久、重启不丢):**把规则源部署到路由器本地 uhttpd,AdGuard 从回环拉取**
1. 本机(走 Clash tproxy,可达 github)下载 **DNS 友好的纯 hosts 源**:
   - 推荐 **StevenBlack/hosts**(纯 hosts 格式,DNS 层完美生效,覆盖广告/追踪/恶意,~7万条);
   - ⚠️ 勿用 `AdguardFilters/.../adservers.txt`——规则带 `$third-party` modifier,DNS 层无法判定第三方上下文会被跳过,等于没拦;
   - 本机落盘受限时用管道直传:`curl <url> | ssh openwrt 'cat > /www/adguard/stevenblack.txt'`;
   - 先在本机 `curl -o /dev/null -w "%{http_code}"` 验证源可达(仅 `raw.githubusercontent.com/StevenBlack/hosts/master/hosts` 在本环境可达)。
2. 路由器建目录 + 校验回环访问:
   ```bash
   mkdir -p /www/adguard
   curl -m5 -o /dev/null -w "%{http_code}\n" http://127.0.0.1/adguard/stevenblack.txt   # 应 200
   ```
3. 改 `/etc/adguardhome.yaml` 的 filter url 指向本地:
   ```yaml
   filters:
     - url: http://127.0.0.1/adguard/stevenblack.txt
       enabled: true
   ```
4. 删旧缓存强制重下 + 重启:
   ```bash
   rm -f /tmp/lib/adguardhome/data/filters/1.txt
   /etc/init.d/adguardhome restart; sleep 20
   ls -la /tmp/lib/adguardhome/data/filters/   # 应出现 ~2MB 大文件
   ```
5. 关键:即使 url 改了,AdGuard 可能不自动重下 → **必须手动删旧 `1.txt` 再重启**才触发。

### ⚠️ 重启安全陷阱(致命):AdGuard 数据在 /tmp,重启即丢
- 默认数据目录 `/tmp/lib/adguardhome/data/`,**在内存盘,路由器重启/断电必清空**。
- 若依赖"开机从 127.0.0.1 重下规则",存在启动竞态(uhttpd 未起 / AdGuard 不开机自更新)→ 重启后规则空 → 去广告失效且 dnsmasq 回退公共 DNS 直解(表现: DNS 通但广告不拦)。
- **根治**:把 AdGuard 数据目录迁到**持久存储**(overlayfs 可写区,如 `/etc/adguardhome` 或 `/usr/lib/adguardhome`),并预置规则文件,使重启无需重新下载。
  ```bash
  # 停止服务 → 迁移数据目录 → 改 work_dir → 预置规则 → 重启
  /etc/init.d/adguardhome stop
  mkdir -p /etc/adguardhome/data/filters
  cp /www/adguard/stevenblack.txt /etc/adguardhome/data/filters/1.txt   # 预置, 开机即有
  # 改 /etc/adguardhome.yaml 的 data_dir 或启动参数 -w 指向 /etc/adguardhome
  # 同时保留 http://127.0.0.1/adguard/ 作为更新源(后台点"更新过滤器"走回环)
  /etc/init.d/adguardhome start
  ```
- 验证持久性:重启路由器后再查 `filters/` 仍有大文件、广告域返回 `0.0.0.0`。

### 最终验证铁证(区分"链路通"与"真拦截")
直接对 AdGuard 端口发 DNS 查询(绕过 dnsmasq),看广告域名是否被返回 `0.0.0.0` / `NXDOMAIN`:
- 广告域(`securepubads.g.doubleclick.net` 等)→ `0.0.0.0` = AdGuard 拦截成功;
- 正常域(`www.baidu.com`)→ `198.18.x` fake-ip = Clash 代理正常;
- 两者并存 = 全部修复完成。

> ⚠️ **验证"路由器透明代理"别用本机 curl**:若管理机自身有出墙代理(`HTTP_PROXY=127.0.0.1:xxxx`),`curl` 默认走本机代理,与路由器 Clash 无关,会得出假阳性。正确做法:① `env -u HTTP_PROXY -u HTTPS_PROXY curl https://www.google.com`(通=路由器代理生效, 超时=未接管);② 从二楼无代理设备测;③ 直接探测 `192.168.1.1` 上 Nikki 端口(9090/1080/789x)是否 OPEN。

## 排错速查
| 现象 | 原因 | 处理 |
|------|------|------|
| 二楼全屋断网 | OpenWrt WAN 没拿到 IP / 网关错 | `ifstatus wan` 查,确认协议为 DHCP 客户端 |
| AdGuard 无日志 | DNS 没指过来 / dnsmasq 占 53 | 查监听端口、grep 旧地址 |
| Clash 不代理 | 非透明模式 / 网关没指过来 | 查运行模式、防火墙规则 |
| 解析慢 / 超时 | WAN DNS 仍含死地址 | 重跑诊断 grep + 修复步骤 |
| AdGuard"开了但不拦" | `filters/` 规则文件为空(下载失败) | 见上文"AdGuard 规则从未下载成功"整段 |
| SSH 通道 WAN 重启后失联 | dropbear 只听 WAN + WAN IP 变 | 改 SSH 访问接口为 lan,改用 LAN IP 连接 |
| 本机进程下不到被墙源 | tproxy 不劫持本机出站 | 规则源改本地 uhttpd 回环(见上文) |
| 二楼 WiFi 连上但不过代理(google 超时) | 节点服务器不可达 / 订阅过期 | 见下文"节点不可达(机场订阅问题)" |
| 路由器订阅自动更新 success=0 | 订阅域名被 GFW 拦截(Cloudflare 前端 TLS EOF,直连拉不到) | 改用机场给的**直连 IP 镜像链接**(`http://IP:端口/uuid/...`)作 `nikki.subscription.url`,路由器可自拉 → success=1;或走"PAIOS 代理拉取→管道推送路由器" |
| 换了新订阅链接仍不通 | 新链接是同一死机场续费 URL,节点后端(server IP)未变 | 经可用代理拉取核对节点 server;连可用代理都连不上节点 IP = 服务器真死,需联系机场 |

### 节点不可达(机场订阅问题)— 与配置无关
表现:Clash/Nikki 进程在跑、tproxy 规则有命中、AdGuard 正常,但二楼设备访问 google 等超时(`env -u HTTP_PROXY curl google` → 000)。
诊断步骤(判断是否真节点挂,而非配置错):
1. 查 Proxy 组当前选中:`curl -H "Authorization: Bearer <secret>" 127.0.0.1:9090/proxies/Proxy` → 若 `now` 是"官网/提示"类占位节点,先切到真实节点(B1002 香港等)。
2. 提取节点服务器域名(订阅里 `server:` 字段),确认其在 fake-ip-filter 中(否则被 fake-ip 污染连假 IP)。
3. 从**路由器**和**管理机(不走代理)**双侧 `nc -z -w5 <节点IP> <端口>` 测端口:
   - 两侧都 CLOSED → **节点服务器真宕机/被 ISP 封锁/订阅过期** = 机场问题,非本机配置可解。
   - 仅路由器侧 CLOSED、管理机 OPEN → 路由器出站被挡(查 fake-ip-filter / 防火墙)。
4. 查订阅分发服务器:`nc -z <sub域名> 443`,CLOSED = 订阅服务器也挂。
关键陷阱:`subxxx.xyz` 类订阅域名若**不在 fake-ip-filter**,Nikki 自动更新订阅时会把它解析成 `198.18.x` 假 IP → 连假 IP 失败 → `uci get nikki.subscription.success` = `0`(自动更新永远失败)。必须把订阅域名加入 `nikki.mixin.fake_ip_filters`。
处置:节点服务器不可达属机场订阅过期/服务器宕机,需用户续费订阅或联系机场换节点;配置侧只需保证:① Proxy 组默认选真实节点(订阅常把"官网"占位节点排第一,需手动切或调订阅顺序);② 订阅域名在 fake-ip-filter 中(自动更新才能成功)。修复后节点服务器恢复即可立即生效。

### 订阅域名被墙 + 新链接验证(本次 2026-07-10 实战)
现象:用户发来"新订阅链接"期望修复代理,但改完仍不通。

关键发现(已逐条验证):
1. **新链接 = 同一家死机场的续费 URL,节点后端未变**。
   - 经可用代理拉取新链接(89454 字节),与路由器磁盘旧订阅**逐字节相同**;
   - 38 个节点全部指向 `1096.rabbitpro-in-5.com` → 解析 `112.49.66.81`(死 IP),共 1722 个代理条目、46 处 rabbitpro 残留;
   - 结论:换链接不换节点 = 机场服务器未恢复,配置层无解。
2. **路由器直连拉订阅被 GFW 拦截(TLS EOF)**。
   - 新订阅域名 `subxxx.xyz` 解析到 Cloudflare IPv6,路由器/管理机直连 HTTPS 均 `curl exit 35`(SSL - connection indicated an EOF);
   - 导致 `nikki.subscription.success='0'`,路由器自动更新永远失败;
   - **但经 PAIOS 本地代理(127.0.0.1:7897)可拉通(200 OK)** —— 该代理本身能通外网(google=200)。
3. **区分"服务器真死" vs "仅路线被墙"的决定性测试**:
   - 用「能通外网的代理」去 `CONNECT` 节点 IP:若连能用的代理都连不上 `112.49.66.81:27101`(code 000, 0.2s 速断),则服务器**真宕机**(代理能绕过普通路线封锁却仍连不上 = 服务器本身挂,非 GFW 路线问题)。
   - 本次:PAIOS 代理通 google=200、通订阅域=200,但 CONNECT `112.49.66.81:27101` 失败 → 服务器真死。

处置 / 标准作业(后续换到可用订阅时):
- **路由器自动更新对 Cloudflare 前端订阅域名不可靠(直连被墙)**。改用「PAIOS 代理拉取 → 推送路由器」路径:
  1. 管理机落盘:`curl -s --compressed -x http://127.0.0.1:7897 -A clash <新订阅URL> > /tmp/sub.yaml`(用 shell 重定向,`-o` 偶发写体失败 exit 23);
  2. 推送:`cat /tmp/sub.yaml | ssh openwrt 'cat > /etc/nikki/subscriptions/subscription.yaml'`(**勿用 scp** —— 本路由器 dropbear 无 sftp-server,`scp` 报 `sftp-server: not found` 直接失败;管道直传等价于 scp);
  3. 重启:`ssh openwrt '/etc/init.d/nikki restart'`;
  4. 切 Proxy 组到真实节点(mihomo API 或 LuCI);
  5. 验证:路由器 `nc -z <节点IP> <端口>` 可达 + 二楼设备 `env -u HTTP_PROXY curl google` 通。
- 收到新机场链接时,**先经 PAIOS 代理拉取并检查节点 `server` 是否仍为死 IP**;若仍指向 `112.49.66.81` 类死地址,直接告知用户机场未恢复,勿盲目重启刷配置。

### 直连 IP 镜像链接(本次 2026-07-10 实战续)
用户随后发来**形态完全不同的新链接**:`http://8.148.211.250:21312/uuid/n4hx4bTchQPsdlFk?clash=1`
- 与之前的 Cloudflare 前端域名(`https://api.subxxx.xyz/...`)**逐字不同**:裸 `http://` + 直连 IP:端口 + 同 uuid;
- **路由器 / 管理机直连、经本地代理,三路全部拉通(89454 字节)** —— 因无域名解析、非 Cloudflare 前端,绕开了 GFW 对 `.xyz` 域名的 TLS EOF 拦截;
- 这正是"订阅域名被墙"的**根治投递方案**:把 Nikki 的 `nikki.subscription.url` 改为该直连 IP 链接后,路由器可**自拉订阅** → `uci get nikki.subscription.success` 从 `0` 变为 `1`(自动更新恢复)。

**但节点后端未变(核心结论不变)**:
- 新链接返回的仍是同一批 38 个 `1096.rabbitpro-in-5.com` 节点(端口从 27101/27102 重排到 27118–27137,md5 因此不同,但 server 域名一字未变);
- 域名仍解析 `112.49.66.81`,路由器 / 代理双侧 `nc` 端口**全 CLOSED** → 服务器真死;
- 直连 IP 链接只解决了"订阅**投递**被墙",未解决"节点**服务器**宕机"。

判定口诀:**直连 IP 链接 = 订阅能拉到 ≠ 节点能连上**。前者修配置层(自动更新),后者纯属机场责任。拿到直连 IP 链接后照常应用(改 url → 重启 Nikki → 验证 success=1),但必须再测节点端口;端口仍 CLOSED 则代理仍不生效,等机场恢复即可自动接管。
