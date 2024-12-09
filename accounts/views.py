from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.core.exceptions import PermissionDenied
from .models import User
from .forms import UserCreateForm, UserUpdateForm, PasswordChangeForm, UserPermissionForm, UserEditForm, AdminPasswordChangeForm

class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    permission_required = 'accounts.view_user'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_admin:
            # 非管理员只能看到非管理员用户
            queryset = queryset.exclude(user_type='admin')
        return queryset

class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    permission_required = 'accounts.add_user'

    def form_valid(self, form):
        if not self.request.user.is_admin and form.cleaned_data['user_type'] == 'admin':
            messages.error(self.request, '只有管理员才能创建管理员用户')
            return self.form_invalid(form)
        
        user = form.save(commit=False)
        if form.cleaned_data['user_type'] == 'admin':
            user.is_staff = True
            user.is_superuser = True
        user.save()
        
        messages.success(self.request, '用户创建成功')
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    permission_required = 'accounts.change_user'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_admin and not self.request.user.is_admin:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        if not self.request.user.is_admin and form.cleaned_data['user_type'] == 'admin':
            messages.error(self.request, '只有管理员才能设置管理员权限')
            return self.form_invalid(form)
        messages.success(self.request, '用户信息更新成功')
        return super().form_valid(form)

@login_required
@permission_required('accounts.delete_user', raise_exception=True)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_admin:
        messages.error(request, '不能删除管理员用户')
        return redirect('accounts:user_list')
    if request.method == 'POST':
        user.delete()
        messages.success(request, '用户删除成功')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

@login_required
def change_password(request, user_id):
    """管理员修改用户密码"""
    if not request.user.is_admin:
        messages.error(request, '只有管理员可以修改用户密码')
        return redirect('accounts:user_list')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, f'用户 {user.username} 的密码已成功修改')
            return redirect('accounts:user_list')
    else:
        form = AdminPasswordChangeForm()
    
    return render(request, 'accounts/change_password.html', {
        'form': form,
        'target_user': user
    })

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_permissions(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    # 只有管理员可以修改权限
    if not request.user.is_admin:
        messages.error(request, '只有管理员可以修改用户权限')
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        form = UserPermissionForm(request.POST, user=user)
        if form.is_valid():
            # 使用表单的 save 方法保存权限
            form.save(user)
            messages.success(request, '用户权限更新成功')
            return redirect('accounts:user_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = UserPermissionForm(user=user)
    
    context = {
        'form': form,
        'user_obj': user
    }
    return render(request, 'accounts/user_permissions.html', context)

@login_required
@permission_required('accounts.view_user')
def user_list(request):
    """用户列表视图"""
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'accounts/user_list.html', context)

@login_required
@permission_required('accounts.add_user')
def user_create(request):
    """创建用户视图"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'用户 {user.username} 创建成功')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm(user=request.user)
    return render(request, 'accounts/user_form.html', {'form': form})

@login_required
@permission_required('accounts.change_user')
def user_edit(request, pk):
    """编辑用户视图"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user, user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'用户 {user.username} 更新成功')
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=user, user=request.user)
    return render(request, 'accounts/user_form.html', {'form': form}) 