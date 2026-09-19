// 全局状态
let allExtensions = [];
let filteredExtensions = [];
let currentPage = 1;
let pageSize = 25;
let sortField = 'last_commit';
let sortOrder = 'desc';

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await loadExtensions();
    setupEventListeners();
    renderTable();
    updatePagination();
});

// 加载扩展数据
async function loadExtensions() {
    try {
        const response = await fetch('data/extensions.json');
        allExtensions = await response.json();
        filteredExtensions = [...allExtensions];

        // 默认按最后提交时间降序排序
        sortExtensions();

        // 显示总数
        document.getElementById('totalCount').textContent = allExtensions.length;

        // 显示更新时间(北京时间)
        const now = new Date();
        const beijingTime = new Date(now.getTime() + (8 * 60 * 60 * 1000));
        document.getElementById('updateTime').textContent = formatDateTime(beijingTime);
    } catch (error) {
        console.error('加载数据失败:', error);
        document.getElementById('tableBody').innerHTML =
            '<tr><td colspan="5" class="no-results">加载数据失败，请刷新页面重试</td></tr>';
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(handleSearch, 300));

    // 排序
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => handleSort(th.dataset.sort));
    });

    // 分页
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
            updatePagination();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        const totalPages = Math.ceil(filteredExtensions.length / pageSize);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
            updatePagination();
        }
    });

    document.getElementById('pageSize').addEventListener('change', (e) => {
        pageSize = parseInt(e.target.value);
        currentPage = 1;
        renderTable();
        updatePagination();
    });
}

// 搜索处理
function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();

    if (!query) {
        filteredExtensions = [...allExtensions];
    } else {
        filteredExtensions = allExtensions.filter(ext => {
            return (
                ext.author.toLowerCase().includes(query) ||
                ext.project.toLowerCase().includes(query) ||
                ext.tags.toLowerCase().includes(query) ||
                ext.description.toLowerCase().includes(query)
            );
        });
    }

    sortExtensions();
    currentPage = 1;
    renderTable();
    updatePagination();
}

// 排序处理
function handleSort(field) {
    if (sortField === field) {
        sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        sortField = field;
        sortOrder = field === 'last_commit' ? 'desc' : 'asc';
    }

    // 更新表头样式
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.classList.remove('active', 'asc', 'desc');
    });
    const activeTh = document.querySelector(`th[data-sort="${field}"]`);
    activeTh.classList.add('active', sortOrder);

    sortExtensions();
    renderTable();
}

// 排序扩展列表
function sortExtensions() {
    filteredExtensions.sort((a, b) => {
        let aVal = a[sortField];
        let bVal = b[sortField];

        // 日期字段特殊处理
        if (sortField === 'first_commit' || sortField === 'last_commit') {
            aVal = new Date(aVal).getTime();
            bVal = new Date(bVal).getTime();
        } else {
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
        }

        if (sortOrder === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
}

// 渲染表格
function renderTable() {
    const tbody = document.getElementById('tableBody');

    if (filteredExtensions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="no-results">没有找到匹配的扩展</td></tr>';
        return;
    }

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageData = filteredExtensions.slice(start, end);

    tbody.innerHTML = pageData.map(ext => `
        <tr>
            <td>
                <a href="${escapeHtml(ext.url)}" class="project-link" target="_blank" rel="noopener">
                    ${escapeHtml(ext.author)}/${escapeHtml(ext.project)}
                </a>
            </td>
            <td>
                <span class="date">${formatDate(ext.first_commit)}</span>
            </td>
            <td>
                <span class="date">${formatDate(ext.last_commit)}</span>
            </td>
            <td>
                <div class="tags">
                    ${ext.tags.split(',').map(tag =>
                        `<span class="tag">${escapeHtml(tag.trim())}</span>`
                    ).join('')}
                </div>
            </td>
            <td>
                <div class="description">${escapeHtml(ext.description)}</div>
            </td>
        </tr>
    `).join('');
}

// 更新分页信息
function updatePagination() {
    const totalPages = Math.ceil(filteredExtensions.length / pageSize);
    const pageInfo = document.getElementById('pageInfo');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');

    pageInfo.textContent = `第 ${currentPage} / ${totalPages} 页`;

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;
}

// 日期格式化
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 日期时间格式化(北京时间)
function formatDateTime(date) {
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0');
    const day = String(date.getUTCDate()).padStart(2, '0');
    const hours = String(date.getUTCHours()).padStart(2, '0');
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
