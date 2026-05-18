# APN 测速对比

时间: 2026-05-17
SIM 卡: 中国电信
设备: CN1 (http://192.168.100.1)

## 结果

| APN | 运营商 | 下载 | 上传 | 延迟 |
|-----|--------|:----:|:----:|:----:|
| **cmnet** | 中国移动 NET | **28.44 Mbps** 🥇 | 8.55 Mbps | 40 ms |
| **uninet** | 中国联通 NET | 26.56 Mbps 🥈 | 7.40 Mbps | 41 ms |
| **ctnet** | 中国电信 NET | 24.16 Mbps | 6.12 Mbps | 40 ms |
| **uniwap** | 中国联通 WAP | 23.53 Mbps | **15.84 Mbps** 🥇 | 40 ms |
| **3gnet** | 中国联通 3G/4G | 23.50 Mbps | 10.91 Mbps | 40 ms |
| **cmwap** | 中国移动 WAP | 23.40 Mbps | 5.10 Mbps | 42 ms |
| **ctlte** | 中国电信 LTE | 12.85 Mbps | 8.39 Mbps | 40 ms |

## 推荐

| 需求 | 推荐 APN |
|------|---------|
| 下载最快 | `cmnet`（28.44 Mbps） |
| 上传最快 | `uniwap`（15.84 Mbps） |
| 最均衡 | `3gnet`（下载23.5 / 上传10.9） |
