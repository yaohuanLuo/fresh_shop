from django.core.paginator import Paginator
from django.shortcuts import render

from goods.models import Goods, GoodsCategory


def index(request):
    if request.method == 'GET':
        # 如果访问首页，返回渲染的首页index.html页面
        cate_dict = {
            1: '新鲜水果',
            2: '海鲜水产',
            3: '猪牛羊肉',
            4: '禽类蛋品',
            5: '新鲜蔬菜',
            6: '速冻食品'
        }
        categorys = GoodsCategory.objects.all()
        msg = []
        for category in categorys:
            goods = Goods.objects.filter(category_id=int(category.category_type)).all()[:4]
            dicts = {
                'type_name': cate_dict[category.category_type],
                'type_img': category.category_front_image,
                'goods': goods
            }
            msg.append(dicts)
        # print(msg[1]['goods'][0].name)
        return render(request, 'index.html', {'msg': msg})


def detail(request, id):
    if request.method == 'GET':
        # 返回详情页面解析的商品信息
        goods = Goods.objects.filter(pk=id).first()
        goods.click_nums += 1
        goods.save()
        # 浏览记录存储格式： [[id, name, shop_price, goods_front_image]]
        img = str(goods.goods_front_image)
        bro = [int(goods.id), goods.name, goods.shop_price, img]
        browse = request.session.get('browse', [])
        if browse:
            if bro in browse:
                browse.remove(bro)
            if len(browse) == 20:
                browse.pop(19)
        browse.insert(0, bro)
        request.session['browse'] = browse
        types = goods.category_id
        all_type = {1: '新鲜水果', 2: '海鲜水产', 3: '猪牛羊肉', 4: '禽类蛋品', 5: '新鲜蔬菜', 6: '速冻食品'}
        types = [all_type[types], types]
        return render(request, 'detail.html', {'goods': goods, 'types': types})


def list(request):
    if request.method == 'GET':
        if request.GET.get('genre'):
            types = int(request.GET.get('genre'))
            goods = Goods.objects.filter(category_id=types)
            all_type = {1: '新鲜水果', 2: '海鲜水产', 3: '猪牛羊肉', 4: '禽类蛋品', 5: '新鲜蔬菜', 6: '速冻食品'}
            types = [all_type[types], types]
        else:
            goods = Goods.objects.all()
            types = 0
        page = int(request.GET.get('page', 1))
        pg = Paginator(goods, 20)
        goods = pg.page(page)
        news = Goods.objects.all().order_by('-add_time')[:3]
        return render(request, 'list.html', {'goods': goods, 'types': types, 'news': news})
