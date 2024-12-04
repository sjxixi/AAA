function confirmDelete(itemType, itemId) {
    if (confirm(`确定要删除这个${itemType}吗？`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/${itemType.toLowerCase()}/${itemId}/delete/`;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
    return false;
}

// 获取URL前缀
function getUrlPrefix(itemType) {
    switch(itemType) {
        case '服务器':
            return 'server';
        case '网络设备':
            return 'network';
        case '存储设备':
            return 'storage';
        case '安全设备':
            return 'security';
        case '数据中心':
            return 'datacenter';
        default:
            return itemType;
    }
}

// 表格排序功能
function sortTable(table, column) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isNumeric = rows.some(row => !isNaN(row.cells[column].textContent));
    const direction = table.getAttribute('data-sort') === 'asc' ? -1 : 1;

    rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();
        
        if (isNumeric) {
            return direction * (parseFloat(aValue) - parseFloat(bValue));
        }
        return direction * aValue.localeCompare(bValue);
    });

    table.setAttribute('data-sort', direction === 1 ? 'asc' : 'desc');
    rows.forEach(row => table.querySelector('tbody').appendChild(row));
}

// 添加排序事件监听
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('table.sortable');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (!header.classList.contains('no-sort')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
});

// 搜索功能
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        let show = false;
        const cells = rows[i].getElementsByTagName('td');
        
        for (let cell of cells) {
            if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                show = true;
                break;
            }
        }
        
        rows[i].style.display = show ? '' : 'none';
    }
}

// 表单验证
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('invalid');
            isValid = false;
        } else {
            input.classList.remove('invalid');
        }
    });

    return isValid;
}

// 导入相关函数
function showImportModal() {
    document.getElementById('importModal').style.display = 'block';
    document.getElementById('importModal').classList.add('show');
}

function closeImportModal() {
    document.getElementById('importModal').style.display = 'none';
    document.getElementById('importModal').classList.remove('show');
}

function validateImport() {
    const fileInput = document.querySelector('input[type="file"]');
    if (!fileInput.files.length) {
        alert('请选择要导入的文件');
        return false;
    }
    return true;
} 