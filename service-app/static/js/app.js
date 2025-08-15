/**
 * 蓝象联邦学习引擎管理平台 - 前端交互逻辑
 * 提供完整的API调用和页面交互功能
 */

// ===========================================
// 全局变量和配置
// ===========================================

let currentConfig = {
    token: '',
    url: '',
    namespace_id: '',
    username: ''
};

let localDataCache = [];
let partnerDataCache = [];

// ===========================================
// 工具函数
// ===========================================

/**
 * 显示Toast通知
 */
function showToast(title, message, type = 'info') {
    const toastElement = document.getElementById('liveToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    
    toastTitle.textContent = title;
    toastBody.textContent = message;
    
    // 根据类型设置样式
    const toastHeader = toastElement.querySelector('.toast-header');
    toastHeader.className = 'toast-header';
    
    switch(type) {
        case 'success':
            toastHeader.classList.add('bg-success');
            break;
        case 'error':
            toastHeader.classList.add('bg-danger');
            break;
        case 'warning':
            toastHeader.classList.add('bg-warning');
            break;
        default:
            toastHeader.classList.add('bg-info');
    }
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

/**
 * 显示加载状态
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('d-none');
    }
}

/**
 * 隐藏加载状态
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('d-none');
    }
}

/**
 * 更新连接状态
 */
function updateConnectionStatus(isConnected) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        if (isConnected) {
            statusElement.textContent = '已连接';
            statusElement.className = 'badge bg-success';
        } else {
            statusElement.textContent = '未连接';
            statusElement.className = 'badge bg-danger';
        }
    }
}

/**
 * API请求封装
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        showToast('错误', `请求失败: ${error.message}`, 'error');
        return { success: false, message: error.message };
    }
}

// ===========================================
// 页面初始化
// ===========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('蓝象联邦学习引擎管理平台已加载');
    
    // 加载配置信息
    loadConfig();
    
    // 测试连接状态
    testConnection();
    
    // 获取系统状态
    getSystemStatus();
    
    // 设置定时刷新
    setInterval(getSystemStatus, 30000); // 每30秒刷新一次状态
});

// ===========================================
// 配置管理
// ===========================================

/**
 * 加载配置信息
 */
async function loadConfig() {
    const result = await apiRequest('/api/config');
    
    if (result.success) {
        currentConfig = result.data;
        
        // 更新配置模态框的值
        document.getElementById('configUrl').value = currentConfig.url;
        document.getElementById('configNamespaceId').value = currentConfig.namespace_id;
        document.getElementById('configUsername').value = currentConfig.username;
    }
}

/**
 * 保存配置
 */
async function saveConfig() {
    const token = document.getElementById('configToken').value;
    const url = document.getElementById('configUrl').value;
    const namespaceId = document.getElementById('configNamespaceId').value;
    const username = document.getElementById('configUsername').value;
    
    if (!token || !url || !namespaceId || !username) {
        showToast('错误', '请填写完整的配置信息', 'error');
        return;
    }
    
    const result = await apiRequest('/api/config', {
        method: 'POST',
        body: JSON.stringify({
            token: token,
            url: url,
            namespace_id: namespaceId,
            username: username
        })
    });
    
    if (result.success) {
        showToast('成功', '配置保存成功', 'success');
        currentConfig = {
            token: token,
            url: url,
            namespace_id: namespaceId,
            username: username
        };
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('configModal'));
        modal.hide();
        
        // 重新测试连接
        testConnection();
    } else {
        showToast('错误', result.message, 'error');
    }
}

// ===========================================
// 系统检测
// ===========================================

/**
 * 测试连接
 */
async function testConnection() {
    const result = await apiRequest('/api/test/connection');
    
    if (result.success) {
        updateConnectionStatus(true);
        showToast('成功', 'API连接正常', 'success');
    } else {
        updateConnectionStatus(false);
        showToast('错误', result.message, 'error');
    }
}

/**
 * 获取系统状态
 */
async function getSystemStatus() {
    const result = await apiRequest('/api/system/status');
    
    if (result.success) {
        const status = result.data;
        
        // 更新连接状态
        updateConnectionStatus(status.api_connection === 'online');
        
        // 更新用户状态
        const userStatusElement = document.getElementById('userStatus');
        if (userStatusElement) {
            userStatusElement.textContent = status.user_logged_in ? '已登录' : '未登录';
        }
    }
}

// ===========================================
// 用户信息管理
// ===========================================

/**
 * 获取用户信息
 */
async function getUserInfo() {
    showLoading('localDataLoading');
    
    const result = await apiRequest('/api/user/info');
    
    hideLoading('localDataLoading');
    
    if (result.success) {
        const userInfo = result.data;
        
        // 更新用户状态显示
        const userStatusElement = document.getElementById('userStatus');
        if (userStatusElement) {
            if (userInfo.code === 'E0000000000' && userInfo.content) {
                userStatusElement.textContent = `${userInfo.content.userName} (${userInfo.content.userId})`;
            } else {
                userStatusElement.textContent = '未登录';
            }
        }
        
        showToast('成功', '用户信息获取成功', 'success');
    } else {
        showToast('错误', result.message, 'error');
    }
}

// ===========================================
// 数据管理
// ===========================================

/**
 * 加载本地数据
 */
async function loadLocalData() {
    showLoading('localDataLoading');
    
    const result = await apiRequest('/api/data/local/list?' + new URLSearchParams({
        namespace_id: currentConfig.namespace_id
    }));
    
    hideLoading('localDataLoading');
    
    if (result.success) {
        localDataCache = result.data.content || [];
        
        // 更新数据计数
        const localDataCountElement = document.getElementById('localDataCount');
        if (localDataCountElement) {
            localDataCountElement.textContent = localDataCache.length;
        }
        
        // 渲染数据列表
        renderLocalDataList(localDataCache);
        
        showToast('成功', '本地数据加载成功', 'success');
    } else {
        showToast('错误', result.message, 'error');
    }
}

/**
 * 渲染本地数据列表
 */
function renderLocalDataList(dataList) {
    const containerElement = document.getElementById('localDataList');
    
    if (!containerElement) return;
    
    if (dataList.length === 0) {
        containerElement.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-database"></i>
                <p>暂无本地数据</p>
            </div>
        `;
        return;
    }
    
    const tableHtml = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>数据编号</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${dataList.map(item => `
                    <tr class="data-row">
                        <td>${item}</td>
                        <td>
                            <div class="btn-group-action">
                                <button class="btn btn-sm btn-success" onclick="exportData('${item}')">
                                    <i class="fas fa-download me-1"></i>导出CSV
                                </button>
                                <button class="btn btn-sm btn-info" onclick="viewDataDetails('${item}', 'local')">
                                    <i class="fas fa-eye me-1"></i>查看详情
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    containerElement.innerHTML = tableHtml;
}

/**
 * 加载合作伙伴数据
 */
async function loadPartnerData() {
    showLoading('partnerDataLoading');
    
    const pageNum = parseInt(document.getElementById('pageNum')?.value || '1');
    const pageSize = parseInt(document.getElementById('pageSize')?.value || '10');
    const engineTag = document.getElementById('engineTag')?.value || '蓝象-联邦学习:1.0.0';
    
    const result = await apiRequest('/api/data/partner/list?' + new URLSearchParams({
        page_num: pageNum,
        page_size: pageSize,
        engine_tag: engineTag,
        username: currentConfig.username
    }));
    
    hideLoading('partnerDataLoading');
    
    if (result.success) {
        const partnerData = result.data.content || {};
        partnerDataCache = partnerData.content || [];
        
        // 更新数据计数
        const partnerDataCountElement = document.getElementById('partnerDataCount');
        if (partnerDataCountElement) {
            partnerDataCountElement.textContent = partnerData.total || 0;
        }
        
        // 渲染数据列表
        renderPartnerDataList(partnerDataCache);
        
        // 渲染分页
        renderPagination(partnerData);
        
        showToast('成功', '合作伙伴数据加载成功', 'success');
    } else {
        showToast('错误', result.message, 'error');
    }
}

/**
 * 渲染合作伙伴数据列表
 */
function renderPartnerDataList(dataList) {
    const containerElement = document.getElementById('partnerDataList');
    
    if (!containerElement) return;
    
    if (dataList.length === 0) {
        containerElement.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-handshake"></i>
                <p>暂无合作伙伴数据</p>
            </div>
        `;
        return;
    }
    
    const tableHtml = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>数据名称</th>
                    <th>机构名称</th>
                    <th>授权状态</th>
                    <th>数据量</th>
                    <th>字段数</th>
                    <th>授权时间</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${dataList.map(item => `
                    <tr class="data-row">
                        <td>${item.metaname}</td>
                        <td>${item.instName}</td>
                        <td>
                            <span class="badge ${item.status === '已授权' ? 'bg-success' : 'bg-warning'}">
                                ${item.status}
                            </span>
                        </td>
                        <td>${item.lineCount?.toLocaleString() || 0}</td>
                        <td>${item.metaCount || 0}</td>
                        <td>${item.grantedAt}</td>
                        <td>
                            <div class="btn-group-action">
                                <button class="btn btn-sm btn-info" onclick="viewPartnerDataColumns('${item.metano}')">
                                    <i class="fas fa-columns me-1"></i>字段信息
                                </button>
                                <button class="btn btn-sm btn-primary" onclick="viewDataDetails('${item.metano}', 'partner')">
                                    <i class="fas fa-eye me-1"></i>详情
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    containerElement.innerHTML = tableHtml;
}

/**
 * 渲染分页控件
 */
function renderPagination(data) {
    const containerElement = document.getElementById('partnerPagination');
    
    if (!containerElement) return;
    
    const current = data.current || 1;
    const pageSize = data.pageSize || 10;
    const total = data.total || 0;
    const totalPages = Math.ceil(total / pageSize);
    
    if (totalPages <= 1) {
        containerElement.innerHTML = '';
        return;
    }
    
    let paginationHtml = `
        <nav>
            <ul class="pagination justify-content-center">
                <li class="page-item ${current <= 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${current - 1})">上一页</a>
                </li>
    `;
    
    // 显示页码
    for (let i = Math.max(1, current - 2); i <= Math.min(totalPages, current + 2); i++) {
        paginationHtml += `
            <li class="page-item ${i === current ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    paginationHtml += `
                <li class="page-item ${current >= totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${current + 1})">下一页</a>
                </li>
            </ul>
        </nav>
        <div class="text-center mt-2">
            <small class="text-muted">共 ${total} 条记录，每页 ${pageSize} 条</small>
        </div>
    `;
    
    containerElement.innerHTML = paginationHtml;
}

/**
 * 切换页码
 */
function changePage(pageNum) {
    document.getElementById('pageNum').value = pageNum;
    loadPartnerData();
}

/**
 * 查看合作伙伴数据字段信息
 */
async function viewPartnerDataColumns(metano) {
    const result = await apiRequest('/api/data/partner/columns?' + new URLSearchParams({
        metano: metano
    }));
    
    if (result.success) {
        // 在模态框中显示字段信息
        showDataDetails(`合作伙伴数据字段信息 (${metano})`, result.data);
    } else {
        showToast('错误', result.message, 'error');
    }
}

/**
 * 显示数据详情
 */
function showDataDetails(title, data) {
    const modal = document.getElementById('dataDetailsModal');
    const titleElement = modal.querySelector('.modal-title');
    const contentElement = document.getElementById('dataDetailsContent');
    
    titleElement.textContent = title;
    contentElement.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

/**
 * 查看数据详情
 */
function viewDataDetails(metano, type) {
    if (type === 'local') {
        showDataDetails(`本地数据详情 (${metano})`, { metano: metano, type: 'local' });
    } else {
        viewPartnerDataColumns(metano);
    }
}

// ===========================================
// 数据导出
// ===========================================

/**
 * 导出数据到CSV
 */
async function exportData(metano = null) {
    const metanoValue = metano || document.getElementById('exportMetano')?.value;
    const filename = document.getElementById('exportFilename')?.value;
    
    if (!metanoValue) {
        showToast('错误', '请输入元数据编号', 'error');
        return;
    }
    
    // 显示导出进度
    showToast('信息', '开始导出数据，请稍候...', 'info');
    
    const result = await apiRequest('/api/data/export', {
        method: 'POST',
        body: JSON.stringify({
            metano: metanoValue,
            output_filename: filename
        })
    });
    
    if (result.success) {
        showToast('成功', `数据导出成功: ${result.data.filename}`, 'success');
    } else {
        showToast('错误', result.message, 'error');
    }
}

// ===========================================
// 任务管理
// ===========================================

/**
 * 上报任务信息
 */
async function reportTask() {
    const taskId = document.getElementById('taskId').value;
    const status = document.getElementById('taskStatus').value;
    const totalTime = parseInt(document.getElementById('taskTotalTime').value || '0');
    
    if (!taskId) {
        showToast('错误', '请输入任务ID', 'error');
        return;
    }
    
    const result = await apiRequest('/api/task/report', {
        method: 'POST',
        body: JSON.stringify({
            task_id: taskId,
            status: status,
            total_time: totalTime,
            namespace_id: currentConfig.namespace_id
        })
    });
    
    if (result.success) {
        showToast('成功', '任务信息上报成功', 'success');
        
        // 清空表单
        document.getElementById('taskId').value = '';
        document.getElementById('taskTotalTime').value = '0';
        
        // 更新任务状态显示
        const taskStatusElement = document.getElementById('taskStatus');
        if (taskStatusElement) {
            taskStatusElement.textContent = status;
        }
    } else {
        showToast('错误', result.message, 'error');
    }
}

// ===========================================
// 文件上传
// ===========================================

/**
 * 上传文件到OSS
 */
async function uploadFile() {
    const fileInput = document.getElementById('uploadFile');
    const filename = document.getElementById('uploadFilename').value;
    
    if (!fileInput.files.length) {
        showToast('错误', '请选择要上传的文件', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const finalFilename = filename || file.name;
    
    // 检查文件大小（5MB限制）
    if (file.size > 5 * 1024 * 1024) {
        showToast('错误', '文件大小不能超过5MB', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_name', finalFilename);
    
    showToast('信息', '开始上传文件，请稍候...', 'info');
    
    try {
        const response = await fetch('/api/file/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('成功', '文件上传成功', 'success');
            
            // 清空表单
            fileInput.value = '';
            document.getElementById('uploadFilename').value = '';
        } else {
            showToast('错误', result.message, 'error');
        }
    } catch (error) {
        showToast('错误', `文件上传失败: ${error.message}`, 'error');
    }
}

// ===========================================
// 审计和网络管理
// ===========================================

/**
 * 上报审计信息
 */
async function reportAudit(action, description) {
    const result = await apiRequest('/api/audit/report', {
        method: 'POST',
        body: JSON.stringify({
            action: action,
            description: description,
            namespace_id: currentConfig.namespace_id,
            username: currentConfig.username,
            module: '蓝象-联邦学习引擎'
        })
    });
    
    if (result.success) {
        console.log('审计信息上报成功');
    } else {
        console.error('审计信息上报失败:', result.message);
    }
}

/**
 * 上报网络信息
 */
async function reportNetwork() {
    const networkIp = prompt('请输入组网IP地址 (格式: IP:PORT)');
    const accessIp = prompt('请输入访问IP地址 (格式: IP:PORT)');
    
    if (!networkIp || !accessIp) {
        showToast('警告', '网络信息不完整', 'warning');
        return;
    }
    
    const result = await apiRequest('/api/network/report', {
        method: 'POST',
        body: JSON.stringify({
            network_ip: networkIp,
            access_ip: accessIp,
            namespace_id: currentConfig.namespace_id
        })
    });
    
    if (result.success) {
        showToast('成功', '网络信息上报成功', 'success');
    } else {
        showToast('错误', result.message, 'error');
    }
}

// ===========================================
// 页面交互增强
// ===========================================

// 自动记录用户操作审计
document.addEventListener('click', function(e) {
    const button = e.target.closest('button');
    if (button && currentConfig.username) {
        const action = button.textContent.trim();
        if (action && !action.includes('取消') && !action.includes('关闭')) {
            reportAudit('页面操作', `用户点击了: ${action}`);
        }
    }
});

// 文件拖拽上传支持
const uploadArea = document.getElementById('uploadFile');
if (uploadArea) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        uploadArea.classList.add('dragover');
    }
    
    function unhighlight(e) {
        uploadArea.classList.remove('dragover');
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        uploadArea.files = files;
    }
}