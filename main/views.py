# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, HttpResponse
from django.contrib.auth.decorators import login_required
import json
from main.models import Hotel, Destination, MyTokens, MyBookings
from coral_client import book
import time
import redis
from django.conf import settings
from tokengenerate import AliToken
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


redis_obj = redis.StrictRedis(host='localhost', port=6379)
domain_name = 'http://127.0.0.1:8080'

book_instance = book.Book()
book_instance.login(settings.API_USERNAME, settings.API_PASSWORD)


@login_required()
def index(request):
    all_entries = Destination.objects.all()
    return render(request, 'main/index.html', {"destinations": all_entries})


@login_required()
def hotels(request):
    # Butun degerleri tek satirda alabilir miyiz?
    pax = request.GET.get('pax')
    checkin_date = request.GET.get('check_in_date')
    checkout_date = request.GET.get('check_out_date')
    destination_code = request.GET.get('destination_code')
    search_params = {'checkin': str(checkin_date),
                     'checkout': str(checkout_date),
                     'pax': str(pax),
                     'destination_code': destination_code,
                     'client_nationality': 'tr',
                     'currency': 'USD'}

    try:
        result = cache_control_search(search_params)
    except ValueError:
        return render_to_response('main/error.html')

    hotel_static = Hotel.objects.values_list('coral_code')
    redis_obj.set('pax_count', json.dumps(pax), ex=3600)
    redis_obj.set('checkin_date', json.dumps(checkin_date), ex=3600)
    redis_obj.set('checkout_date', json.dumps(checkout_date), ex=3600)

    context = [{'hotel_obj_name':
               Hotel.objects.get(coral_code=pro['hotel_code']).name,
               'final_price': min_price(pro), 'hotel_code': pro['hotel_code']}
               for pro in result['results'] if (pro['hotel_code'],)
               in hotel_static]

    # values
    # for product in result['results']:
    #     if (product['hotel_code'],) in hotel_static: #
    # Tek elemanli tuple kontrolu aksi halde false donuyor.
    #         hotel_obj = Hotel.objects.get(coral_code=product['hotel_code'])
    #         final_price = min_price(hotel=product)
    #         hotel_code = product['hotel_code']
    #         context.append({'hotel_obj_name': hotel_obj.name, '
    # final_price': final_price, 'hotel_code': hotel_code})
    if len(context) > 0:
        return render(request, 'main/hotels.html', {"hotels_info": context})
    else:
        return render_to_response('main/noroom.html')


@login_required()
def rooms(request, hotel_code):
    hotel_src_par = {'checkin': json.loads(redis_obj.get('checkin_date')),
                     'checkout': json.loads(redis_obj.get('checkout_date')),
                     'pax': json.loads(redis_obj.get('pax_count')),
                     'hotel_code': hotel_code,
                     'client_nationality': 'tr',
                     'currency': 'USD'}
    redis_obj.set('hotel_code', json.dumps(hotel_code), ex=3600)

    redis_obj.set('hotel_code', json.dumps(hotel_code), ex=3600)

    try:
        result = \
            book_instance.search(hotel_src_par)[0]['results'][0]['products']
    except:
        return render_to_response('main/error.html')

    hotel_obj = Hotel.objects.get(coral_code=hotel_code)
    redis_obj.set('hotel_name', json.dumps(hotel_obj.name), ex=3600)
    sorted_room = sorted(result, key=lambda k: float(k['price']))
    # request.session['hotel_name'] = hotel_obj.name
    return render(request, 'main/rooms.html',
                  {'room_list': sorted_room,
                   'hotel_obj_name': hotel_obj.name})


def room(request, product_code):
    try:
        availability_result = cache_control_availability(product_code)
    except ValueError:
        return render_to_response('main/error.html')
    pax_generator = xrange(int(json.loads(redis_obj.get('pax_count'))))
    redis_obj.set('product_code', json.dumps(product_code), ex=3600)

    # checkout =
    # datetime.strptime(str(request.session['checkout_date']), '%Y-%m-%d')
    # checkin =
    # datetime.strptime(str(request.session['checkin_date']), '%Y-%m-%d')
    total_price = availability_result[0]['price']
    # price_per_night = float(total_price) * int((checkout - checkin).days)

    if availability_result[1] == 200:
        return render(request, 'main/book.html',
                      {'availability_result': availability_result,
                       'pax_generator': pax_generator,
                       'hotel_name': json.loads(redis_obj.get('hotel_name')),
                       'final_price': total_price,
                       'product_code': product_code})
    else:
        return render(request, 'main/noroom.html', {'param': 'room_not_ava'})


@login_required()
def book(request):
    pax = []
    names_surnames = []
    if request.method == "POST":
        product_code = request.POST.get('product_code', 'pax_name')
        mail = str(request.POST.get('mail'))
        redis_obj.set('mail', json.dumps(mail), ex=3600)
        pax_name = request.POST.getlist('pax_name')
        # pax_count = request.session['pax']
        for name in pax_name:
            name_list = name.split()
            last_name = name_list[-1]
            name_list.pop()
            first_name = ' '.join(name_list)
            names_surnames.append((first_name, last_name))
            pax.append('1,{},{},adult'.format(first_name, last_name))

        # request.session['pax_list'] = pax
        redis_obj.set('names_surnames', json.dumps(names_surnames), ex=3600)

        redis_obj.set('pax_list', json.dumps(pax), ex=3600)

        # if total_pax != '':
        #     total_pax = total_pax + '&' + pax +
        # else:
        #     total_pax = pax_count + ',' + pax
        # with cf.ThreadPoolExecutor(max_workers=1) as executor:
        #     executor.submit(send_confirmation_mail, request, mail,
        #                     cache_control_availability(product_code)
        #                     )
        send_confirmation_mail(request, mail,
                               cache_control_availability(product_code))
    return HttpResponse('Check your e-mail to confirm your book ')


@login_required()
def confirmation(request, confirmation_code):
    current_user = request.user
    tokenobj = AliToken()
    product_code = json.loads(redis_obj.get('product_code'))
    mail_token = confirmation_code
    creation_time = MyTokens.objects.get(token_id=mail_token).creation_time
    static_token = MyTokens.objects.get(token_id=mail_token)
    if tokenobj.check_token(current_user, token=mail_token) \
            and not MyTokens.objects.get(token_id=mail_token).used_flag \
            and tokenobj.token_life_time(creation_time):
        static_token.used_flag = True
        static_token.save()
        pro_result = book_instance.provision(product_code)

        if float(pro_result[0]['price']) == \
                float(cache_control_availability(product_code)[0]['price']):
            book_result = book_instance.book(
                provision_code=pro_result[0]['code'],
                book_info={'name': json.loads(redis_obj.get('pax_list'))})
            if book_result[1] == 200:
                # pax_names = json.loads(redis_obj.get('pax_list'))
                # # for pax in pax_names:
                # #
                # # #pax_name = ' '.join(pax_names)
                pax_names = json.loads(redis_obj.get('names_surnames'))
                names = ''
                for item in pax_names:
                    names += item[0] + ' ' + item[1] + ','

                room_type = str(book_result[0]['confirmation_numbers'][0]
                                ['rooms'][0]['room_type'])

                book_code = book_result[0]['code']
                room_description = str(book_result[0]
                                       ['confirmation_numbers'][0]['rooms']
                                       [0]['room_description'])

                pax_count = json.loads(redis_obj.get('pax_count'))
                price = pro_result[0]['price']
                mail = json.loads(redis_obj.get('mail'))
                hotel_code = json.loads(redis_obj.get('hotel_code'))
                provision_code = pro_result[0]['code']
                hotel_name = json.loads(redis_obj.get('hotel_name'))
                c_time = time.ctime()
                book_obj = MyBookings(user=request.user,
                                      provision_code=provision_code,
                                      hotel_code=hotel_code,
                                      coral_booking_code=book_code,
                                      room_type=room_type,
                                      room_description=room_description,
                                      pax_count=pax_count, pax_names=names,
                                      hotel_name=hotel_name,
                                      price=price, email=mail,
                                      book_time=c_time)

                MyBookings.save(book_obj)
                return render_to_response('main/book_messages.html',
                                          {'messages': 'Book success'})

            else:
                return render_to_response('main/book_messages.html',
                                          {'messages':
                                           'Sorry, error occured when '
                                           'book stage, Please '
                                           'try again later'})
        else:
            return render_to_response('main/book_messages.html',
                                      {'messages': 'Sorry, Current price'
                                                   '  has changed, '
                                                   'Please try again '})
    else:
        return render_to_response('main/book_messages.html',
                                  {'messages': 'Invalid confirmation code '})


@login_required()
def mybookings(request):
    booking_list = MyBookings.objects.filter(
                user=request.user).values('price',
                                          'room_type',
                                          'email',
                                          'room_description',
                                          'pax_names',
                                          'hotel_name',
                                          'book_time')
    return render(request, 'main/booking_list.html', {'data': booking_list})


def min_price(hotel):
    return min(hotel["products"], key=lambda k: float(k['price']))['price']


def cache_control_search(params):
    if redis_obj.get(params):
        result = json.loads(redis_obj.get(params))
    else:
        result = book_instance.search(params)[0]
        redis_obj.set(params, json.dumps(result), ex=3600)
    return result


def cache_control_availability(params):
    if redis_obj.get(params):
        result = json.loads(redis_obj.get(params))
    else:
        result = book_instance.availability(params)
        redis_obj.set(params, json.dumps(result), ex=3600)
    return result


def send_confirmation_mail(my_request, mail_address, avab_result):
    current_user = my_request.user
    creation_time = time.time()

    tokenobj = AliToken()

    my_token_id = tokenobj.make_token(current_user)
    my_token_obj = MyTokens(token_id=my_token_id, creation_time=creation_time)
    MyTokens.save(my_token_obj)
    confirmation_link = '{0}/confirmation/{1}'.format(domain_name, my_token_id)
    body = message(avab_response=avab_result,
                   confirmation_code=confirmation_link)

    subject, to = 'Booking Info', mail_address

    email = EmailMultiAlternatives(subject, body=body,
                                   to=[to])
    email.content_subtype = 'html'
    email.send()


def message(avab_response, confirmation_code):
    return render_to_string('main/mail.html',
                            {'book_response': avab_response[0],
                             'hotel_name':
                                 json.loads(redis_obj.get('hotel_name')),
                             'confirmation_code': confirmation_code})
