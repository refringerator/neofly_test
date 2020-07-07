var bookingUrl = 'http://booking.neofly.ru';
$(document).ready(function () {

    var currentItem = window.location.pathname;
    $('.menu_item[href="' + currentItem + '"]').addClass('active');

    $(".page-content .main-page__photo-slider").slick({
        slidesToShow: 5,
        cernterMode: !0,
        infinite: !0,
        nextArrow: $(".page-content .main-page__photo-slider-next"),
        prevArrow: $(".page-content .main-page__photo-slider-prev")
    });

    $('.btn-back').on('click', function() {
        window.history.back();
    });
    
    function getStatusAuth(){
        $.ajax({
            url: bookingUrl + "/api/get-status-auth",
            xhrFields: { withCredentials: true },
            success: function (response) {
                if (response.status == 'ok') {
                    var block = $('<div/>');
                    var image = $('<img/>');
                    var link = $('<a/>');

                    link.addClass('user-block__text').text('Мой кабинет').attr('href', bookingUrl + '/lk/');
                    image.addClass('user-block__img').attr('src', bookingUrl + '/' + response.userImage);
                    block.addClass('menu__user-block').append(image).append(link);
                    $('.menu').prepend(block);
                    $('.main-page__panel-cabinet').hide();
                }
            }
        });
    }
    getStatusAuth();

    $('.menu__burger').click(function(){
        $(this).toggleClass('open');
        $('.menu__wrap').toggleClass('open');
    });
});