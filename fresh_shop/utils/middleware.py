import re

from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect

from cart.models import ShoppingCart
from user.models import User


class AuthMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        # 拦截请求之前的函数
        # 1、给request, user属性赋值，赋值为当前登录系统用户
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(pk=user_id).first()
            request.user = user
        # 2、登录校验，需区分哪些地址需要登录校验，哪些地址不需要登录校验
        path = request.path
        if path == '/':
            return None
        # 不需要登录校验的路由
        not_need_check = ['/user/register/', '/user/login/', '/goods/index/', '/goods/detail/.*/', '/cart/.*/']
        for check_path in not_need_check:
            # 匹配是否是不需要做登录校验的路由
            if re.match(check_path, path):
                return None
        # 需要进行登录验证的路由，判断用户是否登录，没有登录的跳转至登录界面
        if not user_id:
            return HttpResponseRedirect(reverse('user:login'))


class SessionToDbMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        # 同步session中的商品信息和数据库中购物车表的商品信息
        # 1、判断用户是否登录，登录才能做数据同步操作
        user_id = request.session.get('user_id')
        if user_id:
            # 2、同步
            # 2.1 判断session中的商品是否存在于数据库中，如果存在，则更新
            # 2.2 如果不存在则创建
            # 2.3 同步数据库的数据到session中
            session_goods = request.session.get('goods')
            if session_goods:
                for se_goods in session_goods:
                    # se_goods结构为[goods_id, num, is_select]
                    cart = ShoppingCart.objects.filter(user_id=user_id, goods_id=se_goods[0]).first()
                    if cart:
                        # 更新商品信息
                        if cart.nums != se_goods[1] or cart.is_select != se_goods[2]:
                            cart.nums = se_goods[1]
                            cart.is_select = se_goods[2]
                            cart.save()
                    else:
                        # 创建
                        ShoppingCart.objects.create(user_id=user_id, goods_id=se_goods[0], nums=se_goods[1], is_select=se_goods[2])
            # 同步数据库中的数据到session中
            db_carts = ShoppingCart.objects.filter(user_id=user_id)
            # 组装多个商品格式：[[goods_id, num, is_select] ...]
            if db_carts:
                new_session_goods = [[cart.goods_id, cart.nums, cart.is_select] for cart in db_carts]
                request.session['goods'] = new_session_goods
        return response
