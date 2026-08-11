# API密钥配置指南

## 一、获取OKX API密钥

### 步骤1：登录OKX
- 访问 [OKX官网](https://www.okx.com)
- 登录你的账户

### 步骤2：进入API管理
- 点击右上角头像
- 选择「API」

### 步骤3：创建API Key
- 点击「创建API Key」
- 填写信息：
  - 名称：自定义（如：quant-trading）
  - 权限：**读取 + 交易**（不要勾选提币）
  - IP限制：可选（建议绑定IP）

### 步骤4：保存密钥
创建成功后会显示：
- **API Key**：类似 1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6
- **Secret Key**：类似 ABCDEFGH12345678
- **Passphrase**：你自己设置的密码

**⚠️ 重要：立即保存，页面关闭后无法再查看！**

---

## 二、配置密钥

### 方式1：直接编辑配置文件

编辑 config/api_keys.py：

`python
API_KEY = '你的API_Key'
SECRET = '你的Secret_Key'
PASSPHRASE = '你的Passphrase'
`

### 方式2：环境变量（更安全）

`ash
# Windows PowerShell
="your_api_key"
="your_secret"
="your_passphrase"

# Linux/Mac
export OKX_API_KEY="your_api_key"
export OKX_SECRET="your_secret"
export OKX_PASSPHRASE="your_passphrase"
`

---

## 三、安全建议

### ✅ 推荐做法
1. **先用模拟环境测试**
   - 设置 sandbox=True
   - 使用OKX测试网络

2. **权限最小化**
   - 只开放「读取 + 交易」
   - 不要开放「提币」权限

3. **IP限制**
   - 绑定你的服务器IP
   - 防止密钥被盗用

4. **定期更换**
   - 每3-6个月更换一次密钥

### ❌ 避免做法
1. 不要把密钥提交到Git
2. 不要分享给他人
3. 不要在公共网络传输
4. 不要开启提币权限

---

## 四、测试连接

配置完成后，运行测试：

`ash
py run.py
`

如果看到「OKX连接成功」说明配置正确。

---

## 五、模拟环境 vs 实盘

### 模拟环境（推荐先用）
`python
# config/settings.py
SANDBOX = True  # 使用模拟环境
`

### 实盘
`python
# config/settings.py
SANDBOX = False  # 使用实盘
`

**建议：先用模拟环境运行1-2周，确认策略稳定后再切换实盘**

---

## 六、常见问题

### Q1: 提示「Invalid API Key」
- 检查API_KEY是否正确
- 检查是否有空格
- 确认API Key是否已激活

### Q2: 提示「Invalid Sign」
- 检查SECRET是否正确
- 检查PASSPHRASE是否正确
- 确认时间同步

### Q3: 提示「IP not allowed」
- 检查IP限制设置
- 添加当前IP到白名单

---

*最后更新：2026-08-11*
