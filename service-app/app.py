# -*- coding: utf-8 -*-
"""
蓝象联邦学习引擎 Flask Web 应用
提供完整的前端界面和API服务，调用utils.py中的所有功能
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from utils import EngineInfo

# 创建Flask应用
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# 启用CORS支持
CORS(app)

# 全局配置 - 在实际使用时应该从环境变量或配置文件读取
CONFIG = {
    'token': 'your_api_token_here',
    'url': 'http://10.99.92.39:8865/janus/invoke/v1',
    'namespace_id': 'your_namespace_id_here',  
    'username': 'admin007'
}

# 初始化引擎实例
engine = EngineInfo(CONFIG['token'], CONFIG['url'])

# ===========================================
# 页面路由
# ===========================================

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

# ===========================================
# 配置管理API
# ===========================================

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置信息"""
    return jsonify({
        'success': True,
        'data': {
            'url': CONFIG['url'],
            'namespace_id': CONFIG['namespace_id'],
            'username': CONFIG['username']
        }
    })

@app.route('/api/config', methods=['POST'])  
def update_config():
    """更新配置信息"""
    try:
        data = request.get_json()
        
        # 更新配置
        if 'token' in data and data['token']:
            CONFIG['token'] = data['token']
        if 'url' in data and data['url']:
            CONFIG['url'] = data['url']
        if 'namespace_id' in data and data['namespace_id']:
            CONFIG['namespace_id'] = data['namespace_id']
        if 'username' in data and data['username']:
            CONFIG['username'] = data['username']
        
        # 重新初始化引擎实例
        global engine
        engine = EngineInfo(CONFIG['token'], CONFIG['url'])
        
        return jsonify({
            'success': True,
            'message': '配置更新成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'配置更新失败: {str(e)}'
        }), 500

# ===========================================
# 用户信息API
# ===========================================

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    try:
        result = engine.get_user_info()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

# ===========================================  
# 数据管理API
# ===========================================

@app.route('/api/data/local/list', methods=['GET'])
def get_local_data_list():
    """获取本地数据列表"""
    try:
        namespace_id = request.args.get('namespace_id', CONFIG['namespace_id'])
        result = engine.get_local_data_list(namespace_id)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取本地数据列表失败: {str(e)}'
        }), 500

@app.route('/api/data/partner/list', methods=['GET'])
def get_partner_data_list():
    """获取合作伙伴数据列表"""
    try:
        page_num = int(request.args.get('page_num', 1))
        page_size = int(request.args.get('page_size', 10))
        engine_tag = request.args.get('engine_tag', '蓝象-联邦学习:1.0.0')
        username = request.args.get('username', CONFIG['username'])
        
        result = engine.get_partner_data_list(page_num, page_size, engine_tag, username)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取合作伙伴数据列表失败: {str(e)}'
        }), 500

@app.route('/api/data/partner/columns', methods=['GET']) 
def get_partner_data_columns():
    """获取合作伙伴数据字段信息"""
    try:
        metano = request.args.get('metano')
        if not metano:
            return jsonify({
                'success': False,
                'message': '缺少metano参数'
            }), 400
        
        result = engine.get_partner_data_columns(metano)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据字段信息失败: {str(e)}'
        }), 500

@app.route('/api/data/export', methods=['POST'])
def export_local_data_to_csv():
    """导出本地数据到CSV"""
    try:
        data = request.get_json()
        metano = data.get('metano')
        output_filename = data.get('output_filename')
        
        if not metano:
            return jsonify({
                'success': False,
                'message': '缺少metano参数'
            }), 400
        
        result = engine.get_local_data_to_csv(metano, output_filename)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'数据导出失败: {str(e)}'
        }), 500

# ===========================================
# 任务管理API
# ===========================================

@app.route('/api/task/report', methods=['POST'])
def report_task_info():
    """上报任务执行信息"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        status = data.get('status')
        exec_time = data.get('exec_time', datetime.now().isoformat() + 'Z')
        total_time = int(data.get('total_time', 0))
        namespace_id = data.get('namespace_id', CONFIG['namespace_id'])
        
        if not all([task_id, status]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数: task_id, status'
            }), 400
        
        result = engine.report_task_info(task_id, status, exec_time, total_time, namespace_id)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'任务信息上报失败: {str(e)}'
        }), 500

# ===========================================
# 审计管理API
# ===========================================

@app.route('/api/audit/report', methods=['POST'])
def report_audit_info():
    """上报操作审计信息"""
    try:
        data = request.get_json()
        namespace_id = data.get('namespace_id', CONFIG['namespace_id'])
        username = data.get('username', CONFIG['username'])
        action = data.get('action')
        description = data.get('description')
        module = data.get('module', '蓝象-联邦学习引擎')
        
        if not all([action, description]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数: action, description'
            }), 400
        
        result = engine.report_audit_info(namespace_id, username, action, description, module)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'审计信息上报失败: {str(e)}'
        }), 500

# ===========================================
# 网络配置API
# ===========================================

@app.route('/api/network/report', methods=['POST'])
def report_network_info():
    """上报网络配置信息"""
    try:
        data = request.get_json()
        namespace_id = data.get('namespace_id', CONFIG['namespace_id'])
        network_ip = data.get('network_ip')
        access_ip = data.get('access_ip')
        
        if not all([network_ip, access_ip]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数: network_ip, access_ip'
            }), 400
        
        result = engine.report_network_info(namespace_id, network_ip, access_ip)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'网络信息上报失败: {str(e)}'
        }), 500

# ===========================================
# 文件管理API
# ===========================================

@app.route('/api/file/upload', methods=['POST'])
def upload_file_to_oss():
    """上传文件到OSS存储"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        file_name = request.form.get('file_name', file.filename)
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 保存临时文件
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)
        
        try:
            result = engine.report_file_to_center_oss(temp_path, file_name)
            return jsonify({
                'success': True,
                'data': result
            })
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'文件上传失败: {str(e)}'
        }), 500

# ===========================================
# 订单管理API  
# ===========================================

@app.route('/api/order/report', methods=['POST'])
def report_api_server():
    """上报订单结果信息"""
    try:
        data = request.get_json()
        namespace_id = data.get('namespace_id', CONFIG['namespace_id'])
        order_type = data.get('order_type')
        request_param = data.get('request_param', '')
        result_address = data.get('result_address')
        order_id = data.get('order_id', '')
        
        if not all([order_type, result_address]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数: order_type, result_address'
            }), 400
        
        result = engine.report_api_server(namespace_id, order_type, request_param, result_address, order_id)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'订单结果上报失败: {str(e)}'
        }), 500

# ===========================================
# 系统检测API
# ===========================================

@app.route('/api/test/connection', methods=['GET'])
def test_connection():
    """测试API连接状态"""
    try:
        result = engine.get_user_info()
        if result and result.get('code') in ['E0000000000', '200']:
            return jsonify({
                'success': True,
                'message': 'API连接正常',
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'message': 'API连接异常',
                'data': result
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'连接测试失败: {str(e)}'
        }), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统运行状态"""
    try:
        # 测试各个功能模块
        user_status = engine.get_user_info()
        
        status_info = {
            'api_connection': 'online' if user_status.get('code') in ['E0000000000', '200'] else 'offline',
            'user_logged_in': user_status.get('code') == 'E0000000000',
            'server_time': datetime.now().isoformat(),
            'config': {
                'url': CONFIG['url'],
                'namespace_id': CONFIG['namespace_id'],
                'username': CONFIG['username']
            }
        }
        
        return jsonify({
            'success': True,
            'data': status_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取系统状态失败: {str(e)}'
        }), 500

# ===========================================
# 错误处理
# ===========================================

@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        'success': False,
        'message': '接口不存在'
    }), 404

@app.errorhandler(500) 
def internal_error(error):
    """处理500错误"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    """处理400错误"""
    return jsonify({
        'success': False,
        'message': '请求参数错误'
    }), 400

# ===========================================
# 应用启动
# ===========================================

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True) 
    os.makedirs('static/js', exist_ok=True)
    
    print("===========================================")
    print("蓝象联邦学习引擎管理平台")
    print("===========================================")
    print(f"服务地址: http://localhost:5000")
    print(f"API地址: {CONFIG['url']}")
    print(f"命名空间: {CONFIG['namespace_id']}")
    print(f"用户名: {CONFIG['username']}")
    print("===========================================")
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)