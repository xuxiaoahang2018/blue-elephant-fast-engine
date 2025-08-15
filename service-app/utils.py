"""
蓝象联邦学习引擎工具类模块

本模块提供与蓝象联邦学习平台的API交互功能，包括：
- 用户认证与授权
- 数据资产管理
- 任务执行与监控
- 审计日志记录
- 文件传输与存储
"""

import requests
import json
import pandas as pd
import base64
from typing import Dict, Any, Optional


class EngineInfo:
    """
    蓝象联邦学习引擎信息管理类
    
    该类提供与蓝象平台的完整API交互功能，包括用户管理、数据操作、
    任务执行、审计记录等核心功能。
    
    Attributes:
        token (str): API访问令牌，用于身份认证
        url (str): 平台API服务的基础URL地址
    """

    def __init__(self, token: str, url: str):
        """
        初始化引擎信息实例
        
        Args:
            token (str): API访问令牌
            url (str): API服务地址，例如: http://10.99.92.39:8865/janus/invoke/v1
        """
        self.token = token
        self.url = url

    def http_post_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP POST请求的便捷方法
        
        自动添加认证信息并调用静态方法执行实际请求
        
        Args:
            body (Dict[str, Any]): 请求体数据
            
        Returns:
            Dict[str, Any]: API响应结果
        """
        return self.do_http_post_request(
            body=body, 
            url=self.url, 
            headers={"Authorization": self.token}
        )

    @staticmethod
    def do_http_post_request(body: Dict[str, Any], url: Optional[str] = None, 
                           headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        执行HTTP POST请求的核心方法
        
        Args:
            body (Dict[str, Any]): 请求体数据
            url (Optional[str]): 目标URL地址
            headers (Optional[Dict[str, str]]): 自定义请求头
            
        Returns:
            Dict[str, Any]: 解析后的JSON响应或空字典（请求失败时）
            
        请求成功示例:
            {
                'code': '200', 
                'message': '执行成功', 
                'signature': '',
                'content': {'userName': 'admin007', 'userId': 1754447233}, 
                'success': True
            }
            
        请求失败示例:
            {
                'code': 'E0000000500', 
                'message': '用户未登录', 
                'signature': '', 
                'success': False
            }
        """
        # 设置默认请求头
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # 合并自定义请求头
        if headers:
            default_headers.update(headers)
            
        try:
            # 发送POST请求
            response = requests.post(
                url=url,
                data=json.dumps(body),
                headers=default_headers,
                timeout=30
            )
            
            # 检查响应内容类型并返回相应格式
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('application/json'):
                return response.json()
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            print(f"HTTP请求异常: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON解析异常: {e}")
            return {}
        except Exception as e:
            print(f"未知错误: {e}")
            return {}

    @staticmethod
    def build_request_param(method: str, **kwargs) -> Dict[str, Any]:
        """
        构建标准化的API请求参数
        
        为所有API调用添加统一的方法签名后缀和参数结构
        
        Args:
            method (str): API方法名
            **kwargs: 方法参数
            
        Returns:
            Dict[str, Any]: 格式化的请求体
        """
        # 固定的方法签名后缀
        fixed_suffix = ".0001100000000000000000000000000000000.lx0000000000000.trustbe.net"
        
        request_body = {
            "method": method + fixed_suffix,
            "content": {
                "param": kwargs
            }
        }
        return request_body

    def get_user_info(self) -> Dict[str, Any]:
        """
        获取用户信息并校验用户登录状态
        
        Returns:
            Dict[str, Any]: 用户信息响应结果
            
        响应示例:
            未登录状态:
            {
                'code': 'E0000000001', 
                'message': '用户未登录:reference_handler.go:199', 
                'cause': None, 
                'content': None
            }
            
            登录成功状态:
            {
                'code': 'E0000000000', 
                'message': '请求成功', 
                'cause': None, 
                'content': {'userId': 1755166221, 'userName': 'admin007'}
            }
        """
        param = self.build_request_param("info.user.paas")
        resp = self.http_post_request(param)
        
        if not resp:  # 更优雅的空检查
            return self.failed_request_resp()
        return resp

    def get_local_data_list(self, namespace_id: str) -> Dict[str, Any]:
        """
        获取本地数据资产列表
        
        返回数据资产的唯一标识符，需结合 get_local_data_to_csv 方法使用
        
        Args:
            namespace_id (str): 命名空间ID，用于标识数据所属的组织或项目
            
        Returns:
            Dict[str, Any]: 包含数据资产ID列表的响应结果
            
        响应示例:
            {
                'code': 'E0000000000', 
                'message': '请求成功', 
                'cause': None, 
                'content': ['225819277', '225819278']
            }
        """
        body = {"namespaceId": namespace_id}
        param = self.build_request_param(method="list.data.local.engine.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    def get_partner_data_list(self, page_num: int = 1, page_size: int = 10, 
                            engine_tag: str = "蓝象-联邦学习:1.0.0", 
                            username: str = "admin007") -> Dict[str, Any]:
        """
        获取外部合作伙伴授权数据信息列表
        
        Args:
            page_num (int): 页码，默认为1
            page_size (int): 每页大小，默认为10
            engine_tag (str): 引擎标签，默认为"蓝象-联邦学习:1.0.0"
            username (str): 用户名，默认为"admin007"
            
        Returns:
            Dict[str, Any]: 分页的合作伙伴数据列表
            
        响应示例:
            {
                'code': 'E0000000000', 
                'message': '请求成功', 
                'cause': None, 
                'content': {
                    'content': [{
                        'authNumber': 'ec9b56cf56d54ffca905a3a16503f13c',
                        'engineTag': '蓝象-联邦学习:1.0.0',
                        'expiresAt': '', 
                        'grantedAt': '2025-07-23 11:06:11',
                        'instName': '节点083公司',
                        'lineCount': 10000, 
                        'metaCount': 81,
                        'metaname': '83-partner-1w-new',
                        'metano': '2257188319',
                        'namespaceId': 'jg0200008300000500',
                        'networkIp': '',
                        'publishedInstId': 'jg0100008300000000',
                        'status': '已授权'
                    }],
                    'current': 1, 
                    'pageSize': 10, 
                    'total': 1
                }
            }
        """
        body = {
            "pageNum": page_num, 
            "pageSize": page_size, 
            "engineTAG": engine_tag, 
            "username": username
        }
        param = self.build_request_param(method="list.resource.receive.auth.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    def get_partner_data_columns(self, metano: str) -> Dict[str, Any]:
        """
        获取外部合作伙伴授权数据的字段信息
        
        Args:
            metano (str): 元数据编号，用于标识特定的数据集
            
        Returns:
            Dict[str, Any]: 数据字段详细信息
        """
        body = {"metano": metano}
        param = self.build_request_param(method="detail.partner.metaset.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    def report_task_info(self, task_id: str, status: str, exec_time: str, 
                        total_time: int, namespace_id: str) -> Dict[str, Any]:
        """
        上报任务执行信息到平台
        
        Args:
            task_id (str): 任务唯一标识符
            status (str): 任务状态，如 "success", "failed", "running"
            exec_time (str): 任务执行时间，ISO格式时间戳
            total_time (int): 任务总耗时，单位：秒
            namespace_id (str): 命名空间ID
            
        Returns:
            Dict[str, Any]: 上报结果响应
            
        请求体示例:
            {
                "taskId": "12345678abc2",
                "status": "success", 
                "execTime": "2025-06-05T11:15:23.050541Z",
                "totalTime": 300,
                "namespaceId": "JG0100006200000000"
            }
            
        响应示例:
            {
                'code': 'E0000000000', 
                'message': '请求成功', 
                'cause': None, 
                'content': None
            }
        """
        body = {
            "taskId": task_id,
            "status": status, 
            "execTime": exec_time,
            "totalTime": total_time,
            "namespaceId": namespace_id
        }
        param = self.build_request_param(method="save.task.engine.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    def report_audit_info(self, namespace_id: str, username: str, action: str, 
                         description: str, module: str) -> Dict[str, Any]:
        """
        上报操作审计信息到平台
        
        用于记录用户在系统中的关键操作，确保操作可追溯性和安全合规性
        
        Args:
            namespace_id (str): 命名空间ID，标识操作所属的组织或项目
            username (str): 执行操作的用户名
            action (str): 操作类型，如"查询"、"修改"、"删除"等
            description (str): 操作的详细描述
            module (str): 执行操作的模块名称
            
        Returns:
            Dict[str, Any]: 审计记录上报结果
            
        请求体示例:
            {
                "spaceName": "JG0100006200000000",
                "userName": "admin",
                "action": "查询",
                "description": "查询了用户敏感信息",
                "module": "蓝象-联邦学习引擎"
            }
            
        响应示例:
            {
                'code': 'E0000000000', 
                'message': '请求成功', 
                'cause': None, 
                'content': None
            }
        """
        body = {
            "spaceName": namespace_id,
            "userName": username, 
            "action": action,
            "description": description,
            "module": module
        }
        param = self.build_request_param(method="record.operate.audit.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    def get_local_data_to_csv(self, metano: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        分片从中心平台拉取本地数据并保存为CSV文件
        
        该方法会分批获取数据，避免一次性加载大量数据导致内存溢出
        
        Args:
            metano (str): 元数据编号，标识要获取的数据集
            output_filename (Optional[str]): 输出文件名，默认使用metano作为文件名
            
        Returns:
            Dict[str, Any]: 数据获取操作的结果响应
            
        Raises:
            Exception: 当数据解码或文件写入失败时抛出异常
        """
        limit = 1000  # 每批次获取的记录数
        offset = 0    # 当前批次偏移量
        
        # 构建初始请求参数
        body = {"metano": metano, "limit": limit, "offset": offset}
        param = self.build_request_param(method="range.delivery.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
            
        try:
            # 获取数据总量和列信息
            total = resp["content"]["total"]
            columns = [col["name"] for col in resp["content"]["columns"]]
            
            # 确定输出文件名
            csv_filename = output_filename or f"{metano}.csv"
            
            # 分批获取数据
            while offset * limit < total:
                body = {"metano": metano, "limit": limit, "offset": offset}
                param = self.build_request_param(method="range.delivery.paas", **body)
                resp = self.http_post_request(param)
                
                # 解码Base64编码的数据内容
                encoded_content = resp["content"]["content"]
                decoded_data = base64.b64decode(encoded_content)
                json_data = json.loads(decoded_data)
                
                # 创建DataFrame并追加到CSV文件
                df = pd.DataFrame(json_data)
                
                # 第一批数据时写入列头，后续追加时不写入列头
                header = columns if offset == 0 else False
                df.to_csv(csv_filename, mode="a", index=False, header=header)
                
                print(f"已处理第 {offset + 1} 批数据，共 {len(json_data)} 条记录")
                offset += 1
                
            print(f"数据导出完成，共 {total} 条记录，保存至: {csv_filename}")
            return {"code": "E0000000000", "message": "数据导出成功", "filename": csv_filename}
            
        except (KeyError, json.JSONDecodeError, Exception) as e:
            print(f"数据处理失败: {e}")
            return {"code": "E0000000500", "message": f"数据处理失败: {str(e)}"}

    def report_network_info(self, namespace_id: str, network_ip: str, access_ip: str) -> Dict[str, Any]:
        """
        上报网络配置信息到平台
        
        Args:
            namespace_id (str): 命名空间ID
            network_ip (str): 组网IP地址和端口，格式："IP:PORT"
            access_ip (str): 应用前端访问入口地址，格式："IP:PORT"
            
        Returns:
            Dict[str, Any]: 网络信息上报结果
            
        请求体示例:
            {
                "namespace": "jg0100006200000000",
                "networkIp": "127.0.0.1:1001", 
                "accessIp": "127.0.0.1:9977"
            }
        """
        body = {
            "namespace": namespace_id,
            "networkIp": network_ip,
            "accessIp": access_ip
        }
        param = self.build_request_param(method="report.network.engine.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    def report_file_to_center_oss(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        上传文件到中心平台OSS存储
        
        注意：文件大小限制为5MB以内，使用HTTP传输和Base64编码
        
        Args:
            file_path (str): 本地文件路径
            file_name (str): 上传后的文件名
            
        Returns:
            Dict[str, Any]: 文件上传结果，包含文件的ETag等信息
            
        Raises:
            FileNotFoundError: 当指定的文件不存在时
            MemoryError: 当文件过大导致内存不足时
        """
        try:
            # 检查文件大小（5MB限制）
            import os
            file_size = os.path.getsize(file_path)
            max_size = 5 * 1024 * 1024  # 5MB
            
            if file_size > max_size:
                return {
                    "code": "E0000000400",
                    "message": f"文件大小超出限制，当前文件：{file_size/1024/1024:.2f}MB，最大限制：5MB"
                }
            
            # 读取文件并进行Base64编码
            with open(file_path, "rb") as f:
                data = f.read()
            b64_str = base64.b64encode(data).decode("utf-8")
            
            # 构建上传请求
            body = {"fileName": file_name, "content": b64_str}
            param = self.build_request_param(method="upload.file.engine.paas", **body)
            resp = self.http_post_request(param)
            
            if not resp:
                return self.failed_request_resp()
            return resp
            
        except FileNotFoundError:
            return {
                "code": "E0000000404",
                "message": f"文件不存在: {file_path}"
            }
        except MemoryError:
            return {
                "code": "E0000000507",
                "message": "文件过大，内存不足"
            }
        except Exception as e:
            return {
                "code": "E0000000500", 
                "message": f"文件上传失败: {str(e)}"
            }

    def report_api_server(self, namespace_id: str, order_type: str, request_param: str, 
                         result_address: str, order_id: str = "") -> Dict[str, Any]:
        """
        上报任务产出结果到中心平台
        
        支持两种类型的任务结果：API服务类型和文件类型
        
        Args:
            namespace_id (str): 命名空间ID
            order_type (str): 订单类型，"api" 或 "file"
            request_param (str): 请求参数（API类型）或空字符串（文件类型）
            result_address (str): 结果地址（API类型为服务地址，文件类型为OSS ETag）
            order_id (str): 订单ID，可选扩展参数
            
        Returns:
            Dict[str, Any]: 任务产出上报结果
            
        使用示例:
            API服务类型:
            report_api_server(
                namespace_id="jg0100006200000000",
                order_type="api",
                request_param="{'input':{'身份证号':'310xxx'}}",
                result_address="10.0.0.1:7702/order/demo",
                order_id=""
            )
            
            文件类型（需先调用report_file_to_center_oss获取ETag）:
            report_api_server(
                namespace_id="jg0100006200000000", 
                order_type="file",
                request_param="",
                result_address="64adaxxxxx",  # OSS ETag
                order_id=""
            )
        """
        body = {
            "namespace": namespace_id,
            "orderType": order_type,
            "requestParam": request_param,
            "resultAddress": result_address,
            "orderId": order_id
        }
        param = self.build_request_param(method="report.order.engine.paas", **body)
        resp = self.http_post_request(param)
        
        if not resp:
            return self.failed_request_resp()
        return resp

    @staticmethod
    def failed_request_resp() -> Dict[str, Any]:
        """
        生成标准的请求失败响应
        
        Returns:
            Dict[str, Any]: 标准的失败响应格式
        """
        return {
            "code": "E0000000500",
            "message": "请求失败"
        }
