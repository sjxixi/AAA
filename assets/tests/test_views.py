from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from assets.models import DataCenter, Server, NetworkDevice, StorageDevice, SecurityDevice

class AssetManagementTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # 创建测试数据中心
        self.datacenter = DataCenter.objects.create(
            name='测试数据中心',
            location='北京市海淀区',
            contact_name='张三',
            contact_phone='13800138000',
            area=5000.00,
            power_capacity=2000.00,
            cooling_capacity=1500.00
        )
        
        # 创建测试服务器
        self.server = Server.objects.create(
            name='Web服务器-01',
            hostname='web-server-01',
            ip_address='192.168.1.101',
            data_center=self.datacenter,
            os_type='CentOS',
            os_version='8.0',
            status='running',
            business_system='Web应用集群'
        )
        
        # 创建测试网络设备
        self.network_device = NetworkDevice.objects.create(
            name='核心交换机-01',
            ip_address='192.168.1.1',
            data_center=self.datacenter,
            device_type='交换机',
            port_count=48,
            status='running'
        )

    def test_dashboard_view(self):
        """测试仪表盘视图"""
        response = self.client.get(reverse('assets:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/dashboard.html')
        self.assertContains(response, '数据中心')
        self.assertContains(response, '服务器')

    def test_datacenter_crud(self):
        """测试数据中心的增删改查操作"""
        # 测试列表页
        response = self.client.get(reverse('assets:datacenter_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试数据中心')

        # 测试创建
        data = {
            'name': '新数据中心',
            'location': '上海市浦东新区',
            'contact_name': '李四',
            'contact_phone': '13900139000',
            'area': 3000.00,
            'power_capacity': 1500.00,
            'cooling_capacity': 1000.00
        }
        response = self.client.post(reverse('assets:datacenter_create'), data)
        self.assertEqual(response.status_code, 302)  # 重定向状态码
        self.assertTrue(DataCenter.objects.filter(name='新数据中心').exists())

        # 测试详情页
        dc = DataCenter.objects.get(name='新数据中心')
        response = self.client.get(reverse('assets:datacenter_detail', args=[dc.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '上海市浦东新区')

        # 测试编辑
        data['location'] = '上海市黄浦区'
        response = self.client.post(reverse('assets:datacenter_edit', args=[dc.id]), data)
        self.assertEqual(response.status_code, 302)
        dc.refresh_from_db()
        self.assertEqual(dc.location, '上海市黄浦区')

        # 测试删除
        response = self.client.post(reverse('assets:datacenter_delete', args=[dc.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DataCenter.objects.filter(name='新数据中心').exists())

    def test_server_crud(self):
        """测试服务器的增删改查操作"""
        # 测试列表页
        response = self.client.get(reverse('assets:server_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web服务器-01')

        # 测试创建
        data = {
            'name': '新服务器',
            'hostname': 'new-server',
            'ip_address': '192.168.1.102',
            'data_center': self.datacenter.id,
            'os_type': 'Ubuntu',
            'os_version': '20.04',
            'status': 'running',
            'business_system': '测试系统'
        }
        response = self.client.post(reverse('assets:server_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Server.objects.filter(hostname='new-server').exists())

    def test_export_functionality(self):
        """测试导出功能"""
        # 测试数据中心导出
        response = self.client.get(f"{reverse('assets:datacenter_list')}?export=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # 测试服务器导出
        response = self.client.get(f"{reverse('assets:server_list')}?export=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_search_and_filter(self):
        """测试搜索和过滤功能"""
        # 测试数据中心搜索
        response = self.client.get(f"{reverse('assets:datacenter_list')}?name=测试")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试数据中心')

        # 测试服务器搜索
        response = self.client.get(f"{reverse('assets:server_list')}?hostname=web")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'web-server-01')

    def test_authentication(self):
        """测试认证功能"""
        # 登出
        self.client.logout()
        
        # 测试未登录访问重定向
        response = self.client.get(reverse('assets:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

        # 测试错误登录
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html') 