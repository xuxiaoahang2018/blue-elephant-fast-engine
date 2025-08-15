# 蓝象三方引擎接入 API 文档

本文档描述了蓝象联邦学习引擎 `utils.py` 模块中提供的所有API接口。

## 概述

蓝象联邦学习引擎工具类模块提供与蓝象联邦学习平台的API交互功能，包括：
- 用户认证与授权
- 数据资产管理
- 任务执行与监控
- 审计日志记录
- 文件传输与存储

## 类：EngineInfo

### 初始化

#### `__init__(token: str, url: str)`

初始化引擎信息实例

**参数：**
- `token` (str): API访问令牌
- `url` (str): API服务地址，例如: `http://10.99.92.39:8865/janus/invoke/v1`

---

## API 接口

### 1. 用户认证接口

#### `get_user_info()`

获取用户信息并校验用户登录状态

**返回值：** `Dict[str, Any]`

**响应示例：**

未登录状态:
```json
{
    "code": "E0000000001", 
    "message": "用户未登录:reference_handler.go:199", 
    "cause": null, 
    "content": null
}
```

登录成功状态:
```json
{
    "code": "E0000000000", 
    "message": "请求成功", 
    "cause": null, 
    "content": {
        "userId": 1755166221, 
        "userName": "admin007"
    }
}
```

---

### 2. 数据管理接口

#### `get_local_data_list(namespace_id: str)`

获取本地数据资产列表

**参数：**
- `namespace_id` (str): 命名空间ID，用于标识数据所属的组织或项目

**返回值：** `Dict[str, Any]`

**响应示例：**
```json
{
    "code": "E0000000000", 
    "message": "请求成功", 
    "cause": null, 
    "content": ["225819277", "225819278"]
}
```

#### `get_partner_data_list(page_num: int = 1, page_size: int = 10, engine_tag: str = "蓝象-联邦学习:1.0.0", username: str = "admin007")`

获取外部合作伙伴授权数据信息列表

**参数：**
- `page_num` (int): 页码，默认为1
- `page_size` (int): 每页大小，默认为10
- `engine_tag` (str): 引擎标签，默认为"蓝象-联邦学习:1.0.0"
- `username` (str): 用户名，默认为"admin007"

**返回值：** `Dict[str, Any]`

**响应示例：**
```json
{
    "code": "E0000000000", 
    "message": "请求成功", 
    "cause": null, 
    "content": {
        "content": [{
            "authNumber": "ec9b56cf56d54ffca905a3a16503f13c",
            "engineTag": "蓝象-联邦学习:1.0.0",
            "expiresAt": "", 
            "grantedAt": "2025-07-23 11:06:11",
            "instName": "节点083公司",
            "lineCount": 10000, 
            "metaCount": 81,
            "metaname": "83-partner-1w-new",
            "metano": "2257188319",
            "namespaceId": "jg0200008300000500",
            "networkIp": "",
            "publishedInstId": "jg0100008300000000",
            "status": "已授权"
        }],
        "current": 1, 
        "pageSize": 10, 
        "total": 1
    }
}
```

#### `get_partner_data_columns(metano: str)`

获取外部合作伙伴授权数据的字段信息

**参数：**
- `metano` (str): 元数据编号，用于标识特定的数据集

**返回值：** `Dict[str, Any]`

#### `get_local_data_to_csv(metano: str, output_filename: Optional[str] = None)`

分片从中心平台拉取本地数据并保存为CSV文件

**参数：**
- `metano` (str): 元数据编号，标识要获取的数据集
- `output_filename` (Optional[str]): 输出文件名，默认使用metano作为文件名

**返回值：** `Dict[str, Any]`

**注意：** 该方法会分批获取数据，避免一次性加载大量数据导致内存溢出

**成功响应示例：**
```json
{
    "code": "E0000000000", 
    "message": "数据导出成功", 
    "filename": "225819277.csv"
}
```

---

### 3. 任务管理接口

#### `report_task_info(task_id: str, status: str, exec_time: str, total_time: int, namespace_id: str)`

上报任务执行信息到平台

**参数：**
- `task_id` (str): 任务唯一标识符
- `status` (str): 任务状态，如 "success", "failed", "running"
- `exec_time` (str): 任务执行时间，ISO格式时间戳
- `total_time` (int): 任务总耗时，单位：秒
- `namespace_id` (str): 命名空间ID

**返回值：** `Dict[str, Any]`

**请求体示例：**
```json
{
    "taskId": "12345678abc2",
    "status": "success", 
    "execTime": "2025-06-05T11:15:23.050541Z",
    "totalTime": 300,
    "namespaceId": "JG0100006200000000"
}
```

**响应示例：**
```json
{
    "code": "E0000000000", 
    "message": "请求成功", 
    "cause": null, 
    "content": null
}
```

#### `report_api_server(namespace_id: str, order_type: str, request_param: str, result_address: str, order_id: str = "")`

上报任务产出结果到中心平台

**参数：**
- `namespace_id` (str): 命名空间ID
- `order_type` (str): 订单类型，"api" 或 "file"
- `request_param` (str): 请求参数（API类型）或空字符串（文件类型）
- `result_address` (str): 结果地址（API类型为服务地址，文件类型为OSS ETag）
- `order_id` (str): 订单ID，可选扩展参数

**返回值：** `Dict[str, Any]`

**使用示例：**

API服务类型：
```python
report_api_server(
    namespace_id="jg0100006200000000",
    order_type="api",
    request_param="{'input':{'身份证号':'310xxx'}}",
    result_address="10.0.0.1:7702/order/demo",
    order_id=""
)
```

文件类型（需先调用report_file_to_center_oss获取ETag）：
```python
report_api_server(
    namespace_id="jg0100006200000000", 
    order_type="file",
    request_param="",
    result_address="64adaxxxxx",  # OSS ETag
    order_id=""
)
```

---

### 4. 审计日志接口

#### `report_audit_info(namespace_id: str, username: str, action: str, description: str, module: str)`

上报操作审计信息到平台

**参数：**
- `namespace_id` (str): 命名空间ID，标识操作所属的组织或项目
- `username` (str): 执行操作的用户名
- `action` (str): 操作类型，如"查询"、"修改"、"删除"等
- `description` (str): 操作的详细描述
- `module` (str): 执行操作的模块名称

**返回值：** `Dict[str, Any]`

**请求体示例：**
```json
{
    "spaceName": "JG0100006200000000",
    "userName": "admin",
    "action": "查询",
    "description": "查询了用户敏感信息",
    "module": "蓝象-联邦学习引擎"
}
```

**响应示例：**
```json
{
    "code": "E0000000000", 
    "message": "请求成功", 
    "cause": null, 
    "content": null
}
```

---

### 5. 网络配置接口

#### `report_network_info(namespace_id: str, network_ip: str, access_ip: str)`

上报网络配置信息到平台

**参数：**
- `namespace_id` (str): 命名空间ID
- `network_ip` (str): 组网IP地址和端口，格式："IP:PORT"
- `access_ip` (str): 应用前端访问入口地址，格式："IP:PORT"

**返回值：** `Dict[str, Any]`

**请求体示例：**
```json
{
    "namespace": "jg0100006200000000",
    "networkIp": "127.0.0.1:1001", 
    "accessIp": "127.0.0.1:9977"
}
```

---

### 6. 文件管理接口

#### `report_file_to_center_oss(file_path: str, file_name: str)`

上传文件到中心平台OSS存储

**参数：**
- `file_path` (str): 本地文件路径
- `file_name` (str): 上传后的文件名

**返回值：** `Dict[str, Any]`

**注意：** 
- 文件大小限制为5MB以内
- 使用HTTP传输和Base64编码
- 可能抛出 `FileNotFoundError` 或 `MemoryError` 异常

**错误响应示例：**
```json
{
    "code": "E0000000400",
    "message": "文件大小超出限制，当前文件：6.50MB，最大限制：5MB"
}
```

```json
{
    "code": "E0000000404",
    "message": "文件不存在: /path/to/file.txt"
}
```

---

## 工具方法

### `http_post_request(body: Dict[str, Any])`

发送HTTP POST请求的便捷方法，自动添加认证信息

**参数：**
- `body` (Dict[str, Any]): 请求体数据

**返回值：** `Dict[str, Any]`

### `do_http_post_request(body: Dict[str, Any], url: Optional[str] = None, headers: Optional[Dict[str, str]] = None)` [静态方法]

执行HTTP POST请求的核心方法

**参数：**
- `body` (Dict[str, Any]): 请求体数据
- `url` (Optional[str]): 目标URL地址
- `headers` (Optional[Dict[str, str]]): 自定义请求头

**返回值：** `Dict[str, Any]`

**请求成功示例：**
```json
{
    "code": "200", 
    "message": "执行成功", 
    "signature": "",
    "content": {
        "userName": "admin007", 
        "userId": 1754447233
    }, 
    "success": true
}
```

**请求失败示例：**
```json
{
    "code": "E0000000500", 
    "message": "用户未登录", 
    "signature": "", 
    "success": false
}
```

### `build_request_param(method: str, **kwargs)` [静态方法]

构建标准化的API请求参数

**参数：**
- `method` (str): API方法名
- `**kwargs`: 方法参数

**返回值：** `Dict[str, Any]`

### `failed_request_resp()` [静态方法]

生成标准的请求失败响应

**返回值：** `Dict[str, Any]`

```json
{
    "code": "E0000000500",
    "message": "请求失败"
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| E0000000000 | 请求成功 |
| E0000000001 | 用户未登录 |
| E0000000400 | 客户端请求错误（如文件过大） |
| E0000000404 | 资源不存在（如文件不存在） |
| E0000000500 | 服务器内部错误 |
| E0000000507 | 内存不足 |

---

## 使用示例

```python
# 初始化引擎
engine = EngineInfo(
    token="your_api_token",
    url="http://10.99.92.39:8865/janus/invoke/v1"
)

# 获取用户信息
user_info = engine.get_user_info()

# 获取本地数据列表
data_list = engine.get_local_data_list("your_namespace_id")

# 导出数据到CSV
engine.get_local_data_to_csv("225819277", "output.csv")

# 上报任务信息
engine.report_task_info(
    task_id="task123",
    status="success",
    exec_time="2025-06-05T11:15:23.050541Z",
    total_time=300,
    namespace_id="your_namespace_id"
)
```