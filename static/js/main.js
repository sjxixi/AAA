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
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('.sortable');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach(header => {
            if (header.dataset.sortable !== 'false') {
                header.addEventListener('click', () => {
                    sortTable(table, Array.from(headers).indexOf(header));
                });
            }
        });
    });
});

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isNumeric = rows.every(row => 
        !isNaN(row.children[column].textContent.trim())
    );
    
    const direction = table.dataset.sortDirection === 'asc' ? -1 : 1;
    
    rows.sort((a, b) => {
        const aValue = a.children[column].textContent.trim();
        const bValue = b.children[column].textContent.trim();
        
        if (isNumeric) {
            return direction * (parseFloat(aValue) - parseFloat(bValue));
        }
        return direction * aValue.localeCompare(bValue);
    });
    
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    table.dataset.sortDirection = direction === 1 ? 'asc' : 'desc';
}

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